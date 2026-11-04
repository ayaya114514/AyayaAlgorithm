import json
from pathlib import Path
import time

from fastapi.testclient import TestClient
import pytest

from backend.app import create_app
from backend.models import Problem, SubmissionRequest
from backend.runner import judge, outputs_match

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "test-token-for-local-service-only"
AUTH = {"Authorization": "Bearer " + TOKEN}


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(data_dir=tmp_path, token=TOKEN)) as api:
        yield api


@pytest.fixture
def sum_problem():
    return Problem.model_validate_json((ROOT / "bank/problems/OJ-1001.json").read_text())


def await_submission(client, response):
    assert response.status_code == 202, response.text
    identity = response.json()["id"]
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        item = client.get("/api/submissions/" + identity, headers=AUTH).json()
        if item["status"] not in {"QUEUED", "RUNNING"}:
            return item
        time.sleep(.02)
    raise AssertionError("Submission did not finish")


def submit(client, code, language="python", mode="judge", **kwargs):
    return await_submission(client, client.post("/api/submissions", headers=AUTH, json=dict(problem_id="OJ-1001", language=language, code=code, mode=mode, **kwargs)))


@pytest.mark.parametrize("path", sorted((ROOT / "bank/problems").glob("*.json")), ids=lambda p:p.stem)
def test_every_reference_passes_its_sample_and_full_data(path):
    problem = Problem.model_validate_json(path.read_text())
    code = (ROOT / "bank/references" / f"{problem.id}.py").read_text()
    result = judge(problem, SubmissionRequest(problem_id=problem.id,language="python",code=code))
    assert result["verdict"] == "AC", (problem.title, result)


@pytest.mark.parametrize("language,code", [
    ("python", "a,b=map(int,input().split());print(a+b)"),
    ("c", '#include <stdio.h>\nint main(void){long long a,b;scanf("%lld%lld",&a,&b);printf("%lld\\n",a+b);return 0;}'),
    ("cpp", '#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b<<"\\n";}'),
])
def test_real_compilers_and_64_bit_results(client, language, code):
    result = submit(client, code, language)
    assert result["status"] == "AC", result
    assert result["result"]["passed"] == 5


@pytest.mark.parametrize("code,language,verdict", [
    ("print(0)", "python", "WA"),
    ("raise RuntimeError('test')", "python", "RE"),
    ("this is not C++", "cpp", "CE"),
    ("while True: pass", "python", "TLE"),
    ("while True: print('x'*10000)", "python", "OLE"),
])
def test_actual_failure_verdicts(sum_problem, code, language, verdict):
    problem = sum_problem.model_copy(update={"time_limit_ms": 200, "tests": sum_problem.tests[:1]})
    result = judge(problem, SubmissionRequest(problem_id=problem.id, language=language, code=code))
    assert result["verdict"] == verdict, result


def test_sample_and_custom_runs_do_not_mark_a_problem_solved(client):
    code="a,b=map(int,input().split());print(a+b)"
    assert submit(client,code,mode="sample")["status"]=="AC"
    assert client.get("/api/problems",headers=AUTH).json()["progress"]=={}
    custom=submit(client,code,mode="custom",stdin="10 20\n")
    assert custom["status"]=="RUN"
    assert custom["result"]["cases"][0]["stdout"].strip()=="30"
    assert client.get("/api/problems",headers=AUTH).json()["progress"]=={}
    assert submit(client,code)["status"]=="AC"
    assert submit(client,"print(0)")["status"]=="WA"
    assert client.get("/api/problems",headers=AUTH).json()["progress"]["OJ-1001"]=="AC"


def test_api_requires_token_and_blocks_unknown_origins_and_hosts(client):
    assert client.get("/api/health").json()["service"]=="ayaya-oj"
    assert client.get("/api/problems").status_code==401
    assert client.get("/api/problems",headers={"Authorization":"Bearer wrong"}).status_code==401
    blocked=client.post("/api/submissions",headers=AUTH|{"Origin":"https://evil.example"},json={})
    assert blocked.status_code==403
    assert client.get("/api/health",headers={"Host":"rebinding.example"}).status_code==403
    cors=client.options("/api/submissions",headers={"Origin":"http://127.0.0.1:5173","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"authorization,content-type"})
    assert cors.status_code==200
    assert cors.headers["access-control-allow-origin"]=="http://127.0.0.1:5173"


def test_problem_import_is_validated_persistent_and_never_publicizes_test_data(client):
    example=json.loads((ROOT / "public/import-example.json").read_text())
    assert client.post("/api/import",headers=AUTH,json=example).status_code==201
    assert client.post("/api/import",headers=AUTH,json=example).status_code==409
    example["id"]="../../escape"
    assert client.post("/api/import",headers=AUTH,json=example).status_code==422
    problems=client.get("/api/problems",headers=AUTH).json()["problems"]
    assert any(p["id"]=="CUSTOM-1001" for p in problems)
    assert all("tests" not in p for p in problems)
    assert client.post("/api/import",headers=AUTH,content="x"*2000001).status_code==413


def test_persistence_across_restart(tmp_path):
    with TestClient(create_app(data_dir=tmp_path, token=TOKEN)) as client:
        item=submit(client,"a,b=map(int,input().split());print(a+b)")
        example=json.loads((ROOT / "public/import-example.json").read_text())
        assert client.post("/api/import",headers=AUTH,json=example).status_code==201
    with TestClient(create_app(data_dir=tmp_path, token=TOKEN)) as client:
        assert client.get("/api/submissions/"+item["id"],headers=AUTH).json()["status"]=="AC"
        assert any(p["id"]=="CUSTOM-1001" for p in client.get("/api/problems",headers=AUTH).json()["problems"])


def test_comparator_modes():
    assert outputs_match("1  2\r\n", "1\n2")
    assert not outputs_match("1 2", "12")
    assert outputs_match("1 2\r\n", "1 2\n", "exact")
    assert not outputs_match("1  2", "1 2", "exact")


def test_public_catalog_has_real_complete_entries_and_no_reference_answers():
    catalog=json.loads((ROOT / "public/data/catalog.json").read_text())
    assert len(catalog["problems"])==51
    assert len(catalog["categories"])==17
    assert len({p["id"] for p in catalog["problems"]})==51
    assert all(p["samples"] and p["test_count"]>=4 and "tests" not in p for p in catalog["problems"])
    pat=json.loads((ROOT / "public/data/pat.json").read_text())
    assert len(pat["problems"])==304
    assert len({p["id"] for p in pat["problems"]})==304
    assert all(p["official_url"].startswith("https://pintia.cn/problem-sets/") for p in pat["problems"])
