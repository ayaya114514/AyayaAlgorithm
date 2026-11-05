"""Refresh public metadata snapshots without replacing good data on failed reads."""

import argparse
import json
from pathlib import Path
import tempfile

import catalog_acwing
import catalog_global
import catalog_luogu
from build_sources import build

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["luogu", "acwing", "codeforces", "atcoder", "leetcode"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=SOURCES, action="append")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="从公开来源重新请求，默认仅使用已有成功缓存",
    )
    args = parser.parse_args()
    for identity in args.source or SOURCES:
        destination = ROOT / "public/data/sources" / f"{identity}.json"
        try:
            with tempfile.TemporaryDirectory(prefix="ayaya-catalog-") as temporary:
                staging = Path(temporary) / f"{identity}.json"
                if identity in {"luogu", "acwing"}:
                    collector = (
                        catalog_luogu.collect
                        if identity == "luogu"
                        else catalog_acwing.collect
                    )
                    data = collector(output=staging, refresh=args.refresh)
                else:
                    data = catalog_global.COLLECTORS[identity](refresh=args.refresh)
                if data["coverage"]["status"] != "complete" and destination.exists():
                    print(
                        f"{identity}: 本次读取不完整，保留已有完整目录；详情 {data['coverage']['note']}",
                        flush=True,
                    )
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                staged = destination.with_suffix(".tmp")
                staged.write_text(
                    json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8",
                )
                staged.replace(destination)
                print(
                    f"{identity}: {data['coverage']['collected']} 条，快照 {data['updated_at']}",
                    flush=True,
                )
        except Exception as error:
            if not destination.exists():
                raise
            print(f"{identity}: {type(error).__name__}，保留现有快照", flush=True)
    build()


if __name__ == "__main__":
    main()
