"""Validate source snapshots and build the small, lazily loaded directory index."""

import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ("luogu", "洛谷主站", {"www.luogu.com.cn", "luogu.com.cn"}),
    ("acwing", "公开在线题库", {"www.acwing.com", "acwing.com"}),
    ("codeforces", "主站 Problemset", {"codeforces.com"}),
    ("atcoder", "AtCoder Problems 数据集", {"atcoder.jp"}),
    ("leetcode", "中国站公开目录", {"leetcode.cn", "leetcode.com"}),
]


def build():
    manifests = []
    for identity, short, hosts in SOURCES:
        path = ROOT / "public/data/sources" / f"{identity}.json"
        data = json.loads(path.read_text())
        problems = data["problems"]
        assert data["source_id"] == identity
        assert len(problems) == len({p["id"] for p in problems})
        assert data["coverage"]["collected"] == len(problems)
        if data["coverage"]["status"] == "complete":
            assert data["coverage"]["expected_total"] == len(problems)
        for problem in problems:
            url = urlsplit(problem["official_url"])
            assert url.scheme == "https" and url.hostname in hosts
            assert problem["source"] == identity
            assert isinstance(problem["tags"], list)
            assert isinstance(problem["categories"], list)
            assert not {
                "statement",
                "content",
                "tests",
                "solution",
                "code",
            }.intersection(problem)
        # Compact JSON saves transfer and browser parse time; no semantic rewrite.
        path.write_text(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        manifests.append(
            {key: value for key, value in data.items() if key != "problems"}
            | {
                "path": f"sources/{identity}.json",
                "scope_short": short,
                "bytes": path.stat().st_size,
                "revision": hashlib.sha256(path.read_bytes()).hexdigest()[:16],
            }
        )
    pat = json.loads((ROOT / "public/data/pat.json").read_text())
    count = len(pat["problems"])
    manifests.append(
        dict(
            schema_version=1,
            source_id="pat",
            name="PAT",
            updated_at=pat["updated_at"],
            source_url=pat["source"],
            metadata_provider="PTA 官方公开列表；算法分类为本站整理",
            scope="PAT 乙级与甲级公开练习题目集，不含顶级题目集",
            scope_short="乙级 / 甲级",
            coverage=dict(
                status="complete",
                expected_total=count,
                collected=count,
                note="乙级 125 题、甲级 179 题；分类为本站整理提示，不是官方标签。",
            ),
            path="pat.json",
        )
    )
    manifest = dict(
        schema_version=1,
        total=sum(s["coverage"]["collected"] for s in manifests),
        sources=manifests,
    )
    output = ROOT / "public/data/sources/index.json"
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "total": manifest["total"],
                "sources": {s["name"]: s["coverage"]["collected"] for s in manifests},
            },
            ensure_ascii=False,
        )
    )
    return manifest


if __name__ == "__main__":
    build()
