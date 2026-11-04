"""Launch the local companion after activating the user's conda environment."""

import argparse
import os
from pathlib import Path
import secrets
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description="Ayaya OJ 本地判题服务")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--origin", action="append", default=[], help="允许访问的 GitHub Pages origin，如 https://用户名.github.io")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("端口必须在 1024 至 65535 之间")
    local = ROOT / ".local"
    local.mkdir(exist_ok=True)
    settings = local / "settings.json"
    import json
    config = json.loads(settings.read_text()) if settings.exists() else {"origins": []}
    for origin in args.origin:
        parsed = urlsplit(origin)
        if parsed.scheme != "https" or not parsed.netloc or parsed.path not in {"", "/"} or parsed.query or parsed.fragment or parsed.username:
            parser.error("--origin 请填写 HTTPS 域名，不含 /仓库名 路径")
        normalized = f"https://{parsed.netloc}"
        if normalized not in config["origins"]:
            config["origins"].append(normalized)
    settings.write_text(json.dumps(config, ensure_ascii=False, indent=2))
    token_file = local / "token"
    if not token_file.exists():
        descriptor = os.open(token_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as handle:
            handle.write(secrets.token_urlsafe(32))
    os.environ["AYAYA_ALLOWED_ORIGINS"] = ",".join(config["origins"] + [f"http://127.0.0.1:{args.port}", f"http://localhost:{args.port}"])
    print(f"\nAyaya OJ 本地服务：http://127.0.0.1:{args.port}", flush=True)
    print(f"连接 token：{token_file.read_text().strip()}", flush=True)
    print("仅运行你自己信任的代码。当前版本为本地资源限制执行器，不是恶意代码隔离环境。", flush=True)
    print("macOS 的耗时为本机 wall time，不提供严格内存判定。按 Ctrl+C 停止。\n", flush=True)
    import uvicorn
    from backend.app import create_app
    uvicorn.run(create_app(), host="127.0.0.1", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
