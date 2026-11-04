"""Authenticated loopback-only API; serve the built frontend as a Safari fallback."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hmac
import json
import logging
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import threading
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .models import Problem, SubmissionRequest
from .runner import compilers, judge

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORIGINS = ["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:4173", "http://localhost:4173", "http://127.0.0.1:8765", "http://localhost:8765"]


class Store:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / "submissions.sqlite3"
        with self.connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS submissions (id TEXT PRIMARY KEY, problem_id TEXT, title TEXT, language TEXT, mode TEXT, status TEXT, created_at TEXT, code TEXT, result TEXT)")
            connection.execute("UPDATE submissions SET status='INTERRUPTED' WHERE status IN ('QUEUED','RUNNING')")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def create(self, problem, submission):
        identity = uuid.uuid4().hex
        with self.connect() as connection:
            connection.execute("INSERT INTO submissions VALUES (?,?,?,?,?,?,?,?,?)", (identity, problem.id, problem.title, submission.language, submission.mode, "QUEUED", datetime.now(timezone.utc).isoformat(), submission.code, None))
        return identity

    def update(self, identity, status, result=None):
        with self.connect() as connection:
            connection.execute("UPDATE submissions SET status=?,result=? WHERE id=?", (status, json.dumps(result, ensure_ascii=False) if result else None, identity))

    def rows(self, limit=100, offset=0):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("SELECT * FROM submissions ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return [dict(row) | {"result": json.loads(row["result"]) if row["result"] else None} for row in rows]

    def get(self, identity):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute("SELECT * FROM submissions WHERE id=?", (identity,)).fetchone()
        return dict(row) | {"result": json.loads(row["result"]) if row["result"] else None} if row else None

    def progress(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT problem_id,status FROM submissions WHERE mode='judge' ORDER BY created_at").fetchall()
        progress = {}
        for identity, status in rows:
            if progress.get(identity) != "AC":
                progress[identity] = status
        return progress


def create_app(data_dir=None, bank_dir=None, token=None, allowed_origins=None):
    directory = Path(data_dir or os.environ.get("AYAYA_DATA_DIR", ROOT / ".local"))
    bank = Path(bank_dir or ROOT / "bank" / "problems")
    origins = allowed_origins if allowed_origins is not None else DEFAULT_ORIGINS + [origin.strip().rstrip("/") for origin in os.environ.get("AYAYA_ALLOWED_ORIGINS", "").split(",") if origin.strip()]

    @asynccontextmanager
    async def lifespan(application):
        directory.mkdir(parents=True, exist_ok=True)
        token_file = directory / "token"
        if token:
            local_token = token
        elif token_file.exists():
            local_token = token_file.read_text().strip()
        else:
            local_token = secrets.token_urlsafe(32)
            descriptor = os.open(token_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w") as handle:
                handle.write(local_token)
        application.state.token = local_token
        application.state.store = Store(directory)
        application.state.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="oj")
        application.state.capacity = threading.BoundedSemaphore(12)
        application.state.import_lock = threading.Lock()
        application.state.problems = {}
        imported = directory / "problems"
        imported.mkdir(exist_ok=True)
        for folder in [bank, imported]:
            for path in sorted(folder.glob("*.json")):
                problem = Problem.model_validate_json(path.read_text())
                if problem.id in application.state.problems:
                    raise RuntimeError(f"重复题号：{problem.id}")
                application.state.problems[problem.id] = problem
        yield
        application.state.executor.shutdown(wait=True, cancel_futures=False)

    application = FastAPI(title="Ayaya OJ Local", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    application.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"], max_age=600)

    @application.middleware("http")
    async def guard(request, call_next):
        host = request.url.hostname
        if host not in {"localhost", "127.0.0.1", "::1", "testserver"}:
            return JSONResponse({"detail": "仅接受 localhost 访问"}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin not in origins:
            return JSONResponse({"detail": "网站来源未授权；启动时通过 --origin 添加你的 GitHub Pages 域名"}, status_code=403)
        if request.method == "POST":
            size = 0
            chunks = []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 2000000:
                    return JSONResponse({"detail": "请求超过 2 MB"}, status_code=413)
                chunks.append(chunk)
            request._body = b"".join(chunks)
        return await call_next(request)

    def authorized(request: Request):
        given = request.headers.get("Authorization", "")
        if not hmac.compare_digest(given, "Bearer " + application.state.token):
            raise HTTPException(401, "连接 token 不正确，请从本地服务复制")

    @application.get("/api/health")
    def health():
        return {"service": "ayaya-oj", "version": "0.1.0", "languages": {key: value is not None for key, value in compilers().items()}, "python": sys.version.split()[0], "strict_memory_limit": sys.platform.startswith("linux"), "execution_mode": "trusted-local", "problem_count": len(application.state.problems)}

    @application.get("/api/problems", dependencies=[Depends(authorized)])
    def problems():
        return {"problems": [problem.public() for problem in application.state.problems.values()], "progress": application.state.store.progress()}

    @application.get("/api/submissions", dependencies=[Depends(authorized)])
    def submissions(limit: int = 100, offset: int = 0):
        return {"submissions": application.state.store.rows(max(1, min(limit, 100)), max(0, offset)), "progress": application.state.store.progress()}

    @application.get("/api/submissions/{identity}", dependencies=[Depends(authorized)])
    def submission_detail(identity: str):
        item = application.state.store.get(identity)
        if not item:
            raise HTTPException(404, "提交不存在")
        return item

    def work(identity, problem, submission):
        application.state.store.update(identity, "RUNNING")
        try:
            result = judge(problem, submission)
            application.state.store.update(identity, result["verdict"], result)
        except Exception:
            logging.exception("Local judging failed")
            application.state.store.update(identity, "SE", {"verdict": "SE", "score": 0, "message": "本地评测异常，请查看服务日志", "cases": []})
        finally:
            application.state.capacity.release()

    @application.post("/api/submissions", status_code=202, dependencies=[Depends(authorized)])
    def submit(submission: SubmissionRequest):
        problem = application.state.problems.get(submission.problem_id)
        if not problem:
            raise HTTPException(404, "本地题库中没有这道题")
        if not application.state.capacity.acquire(blocking=False):
            raise HTTPException(429, "判题队列已满，请稍后提交")
        try:
            identity = application.state.store.create(problem, submission)
            application.state.executor.submit(work, identity, problem, submission)
        except Exception:
            application.state.capacity.release()
            raise
        return {"id": identity, "status": "QUEUED"}

    @application.post("/api/import", status_code=201, dependencies=[Depends(authorized)])
    def import_problem(problem: Problem):
        with application.state.import_lock:
            if problem.id in application.state.problems:
                raise HTTPException(409, "题号已存在，请更换题号后导入")
            destination = directory / "problems" / f"{problem.id}.json"
            temporary = destination.with_suffix(".tmp")
            temporary.write_text(problem.model_dump_json(indent=2), encoding="utf-8")
            temporary.replace(destination)
            application.state.problems[problem.id] = problem
        return problem.public()

    # Same-origin mode avoids browser-specific HTTPS -> loopback restrictions.
    dist = ROOT / "dist"
    if (dist / "assets").exists():
        application.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")
    if (dist / "data").exists():
        application.mount("/data", StaticFiles(directory=dist / "data"), name="data")

    @application.get("/")
    def index():
        if (dist / "index.html").exists():
            return FileResponse(dist / "index.html")
        return JSONResponse({"service": "Ayaya OJ", "message": "请先运行 npm run build，或访问 http://127.0.0.1:5173"})

    @application.get("/favicon.svg")
    def favicon():
        return FileResponse(ROOT / "public" / "favicon.svg", media_type="image/svg+xml")

    return application
