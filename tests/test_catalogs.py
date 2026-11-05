from datetime import datetime
import json
from pathlib import Path
import random
import runpy
from urllib.parse import urlsplit

import pytest

from scripts.catalog_acwing import cached_response_date, parse_page
from scripts.catalog_luogu import parse_page as parse_luogu

ROOT = Path(__file__).resolve().parents[1]


def solve(title, data):
    problem = next(
        json.loads(path.read_text())
        for path in (ROOT / "bank/problems").glob("*.json")
        if json.loads(path.read_text())["title"] == title
    )
    namespace = runpy.run_path(str(ROOT / "bank/references" / (problem["id"] + ".py")))
    return namespace["solve"](data)


def test_acwing_display_number_does_not_replace_content_id():
    html = '<table><tr><td></td><td>18</td><td><a id="problem-title-23" href="/problem/content/23/">重建二叉树</a></td><td></td><td></td><td>50%</td><td>中等</td></tr></table><a id="page_145"></a>'
    problems, pages = parse_page(html)
    assert pages == 145
    assert problems[0]["id"] == "ACW-18"
    assert problems[0]["official_url"] == "https://www.acwing.com/problem/content/23/"
    assert problems[0]["category"] == "树"


def test_luogu_parser_does_not_treat_a_block_page_as_empty_catalog():
    with pytest.raises(ValueError):
        parse_luogu("<html><title>Access restricted</title></html>")
    data = {
        "status": 200,
        "template": "problem.list",
        "data": {
            "problems": {
                "count": 1,
                "perPage": 50,
                "result": [{"pid": "P1001", "name": "A+B Problem"}],
            }
        },
    }
    html = (
        '<script id="lentille-context" type="application/json">'
        + json.dumps(data)
        + "</script>"
    )
    assert parse_luogu(html)["result"][0]["pid"] == "P1001"


def test_cache_dates_describe_acquisition_not_rerun(tmp_path):
    path = tmp_path / "page-1.html"
    path.write_text("public directory")
    path.with_suffix(".meta.json").write_text(
        json.dumps({"retrieved_at": "2026-11-03T17:00:00+00:00"})
    )
    assert cached_response_date(path) == "2026-11-04"


def test_all_source_snapshots_are_complete_consistent_and_metadata_only():
    manifest = json.loads((ROOT / "public/data/sources/index.json").read_text())
    assert [s["source_id"] for s in manifest["sources"]] == [
        "luogu",
        "acwing",
        "codeforces",
        "atcoder",
        "leetcode",
        "pat",
    ]
    assert manifest["total"] == sum(
        s["coverage"]["collected"] for s in manifest["sources"]
    )
    assert manifest["total"] >= 50000
    all_ids = set()
    for source in manifest["sources"]:
        data = json.loads((ROOT / "public/data" / source["path"]).read_text())
        problems = data["problems"]
        assert source["coverage"]["collected"] == len(problems)
        assert source["coverage"]["status"] == "complete"
        assert source["coverage"]["expected_total"] == len(problems)
        assert datetime.fromisoformat(source["updated_at"])
        ids = {p["id"] for p in problems}
        assert len(ids) == len(problems) and not ids.intersection(all_ids)
        all_ids.update(ids)
        assert all(
            not {"statement", "content", "tests", "solution", "code"}.intersection(p)
            for p in problems
        )
        assert all(urlsplit(p["official_url"]).scheme == "https" for p in problems)
    acwing = json.loads((ROOT / "public/data/sources/acwing.json").read_text())
    assert next(p for p in acwing["problems"] if p["id"] == "ACW-18")[
        "official_url"
    ].endswith("/content/23/")
    leetcode = json.loads((ROOT / "public/data/sources/leetcode.json").read_text())
    assert sum(p["paid"] is True for p in leetcode["problems"]) > 0


def test_lazy_segment_tree_against_direct_array_operations():
    rng = random.Random(4307)
    a = [rng.randrange(-20, 21) for _ in range(17)]
    current = a[:]
    operations = []
    expected = []
    for _ in range(80):
        left = rng.randrange(1, 18)
        right = rng.randrange(left, 18)
        if rng.random() < 0.6:
            delta = rng.randrange(-8, 9)
            operations.append(f"add {left} {right} {delta}")
            for i in range(left - 1, right):
                current[i] += delta
        else:
            operations.append(f"sum {left} {right}")
            expected.append(sum(current[left - 1 : right]))
    data = (
        f"17 {len(operations)}\n" + " ".join(map(str, a)) + "\n" + "\n".join(operations)
    )
    assert list(map(int, solve("区间增加与区间求和", data).split())) == expected


def test_maxflow_against_exhaustive_min_cuts():
    rng = random.Random(612)
    for _ in range(12):
        n = 5
        edges = [
            (a, b, rng.randrange(0, 7))
            for a in range(1, n + 1)
            for b in range(1, n + 1)
            if a != b and rng.random() < 0.35
        ]
        minimum = min(
            sum(c for a, b, c in edges if a in side and b not in side)
            for mask in range(1 << (n - 2))
            for side in [{1} | {i + 2 for i in range(n - 2) if mask >> i & 1}]
        )
        data = f"{n} {len(edges)} 1 {n}\n" + "\n".join(
            f"{a} {b} {c}" for a, b, c in edges
        )
        assert int(solve("有向网络最大流", data)) == minimum


def test_scc_against_all_pairs_reachability():
    rng = random.Random(170)
    for _ in range(12):
        n = 6
        edges = [(a, b) for a in range(n) for b in range(n) if rng.random() < 0.2]
        reachable = [[i == j for j in range(n)] for i in range(n)]
        for a, b in edges:
            reachable[a][b] = True
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    reachable[i][j] |= reachable[i][k] and reachable[k][j]
        groups = {
            frozenset(j for j in range(n) if reachable[i][j] and reachable[j][i])
            for i in range(n)
        }
        data = f"{n} {len(edges)}\n" + "\n".join(f"{a+1} {b+1}" for a, b in edges)
        assert int(solve("强连通分量个数", data)) == len(groups)


def test_lca_against_parent_chain_search():
    rng = random.Random(23)
    n = 35
    parent = {1: 0}
    edges = []
    for child in range(2, n + 1):
        parent[child] = rng.randrange(1, child)
        edges.append((parent[child], child))
    queries = [(rng.randrange(1, n + 1), rng.randrange(1, n + 1)) for _ in range(70)]
    expected = []
    for a, b in queries:
        ancestors = set()
        while a:
            ancestors.add(a)
            a = parent[a]
        while b not in ancestors:
            b = parent[b]
        expected.append(b)
    data = f"{n} {len(queries)} 1\n" + "\n".join(f"{a} {b}" for a, b in edges + queries)
    assert list(map(int, solve("最近公共祖先", data).split())) == expected
