"""Collect only public AcWing directory metadata, with caching and throttling.

No login, problem statements, submissions, hidden tests, or solutions are read.
Displayed problem numbers are not assumed to equal the IDs in content URLs.
"""

import argparse
from datetime import date, datetime, timezone
import html
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.acwing.com"
INDEX_URL = BASE_URL + "/problem/"
ROWS = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
CELLS = re.compile(r"<td\b[^>]*>(.*?)</td>", re.DOTALL | re.IGNORECASE)
TITLE = re.compile(
    r'<a\s+id="problem-title-(\d+)"\s+href="([^"]+)"[^>]*>(.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)


def plain_text(value):
    value = re.sub(r"<[^>]*>", "", value)
    return " ".join(html.unescape(value).split())


def keywords(row, field):
    match = re.search(
        r"let\s+\$field\s*=\s*\$\('#problem-"
        + re.escape(field)
        + r"-\d+'\);\s*let\s+keywords\s*=\s*(\"(?:\\.|[^\"\\])*\")",
        row,
        re.DOTALL,
    )
    if not match:
        return []
    try:
        value = json.loads(match.group(1))
    except json.JSONDecodeError:
        # Retain the literal label rather than evaluating JavaScript.
        value = match.group(1)[1:-1]
    return list(
        dict.fromkeys(
            plain_text(piece)
            for piece in value.replace("，", ",").split(",")
            if plain_text(piece)
        )
    )


# Broad, conservative learning categories. Original algorithm tags are retained.
RULES = [
    ("链表", ("链表", "linked list")),
    ("栈", ("单调栈", "栈", "stack")),
    ("队列", ("单调队列", "队列", "queue")),
    ("堆", ("堆", "优先队列", "heap", "priority queue")),
    ("并查集", ("并查集", "union find", "disjoint")),
    ("区间数据结构", ("线段树", "树状数组", "前缀和", "差分", "st表", "rmq")),
    ("树", ("二叉树", "二叉搜索树", "树形", "平衡树", "lca", "最近公共祖先")),
    (
        "图",
        (
            "图论",
            "最短路",
            "最小生成树",
            "网络流",
            "拓扑",
            "二分图",
            "dijkstra",
            "floyd",
            "spfa",
            "bellman",
        ),
    ),
    ("动态规划", ("dp", "动态规划", "背包", "状态压缩", "数位统计")),
    ("贪心", ("贪心", "greedy")),
    ("搜索与回溯", ("dfs", "bfs", "搜索", "回溯", "迭代加深", "八数码")),
    ("排序与查找", ("排序", "二分", "查找", "快速选择", "归并", "逆序对")),
    ("字符串", ("字符串", "kmp", "字典树", "trie", "后缀数组", "ac自动机", "回文")),
    ("哈希与集合", ("哈希", "散列", "集合", "hash")),
    ("数组与双指针", ("双指针", "滑动窗口", "数组")),
    (
        "数学与数论",
        (
            "数学",
            "数论",
            "素数",
            "质数",
            "约数",
            "公约数",
            "快速幂",
            "组合",
            "概率",
            "期望",
            "欧拉",
            "容斥",
            "高斯",
            "博弈",
            "nim",
            "位运算",
            "线性规划",
        ),
    ),
    ("入门与模拟", ("模拟", "枚举", "implementation")),
]


def classify(title, tags):
    tag_text = " ".join(tags).lower()
    matched = [
        category for category, words in RULES if any(w in tag_text for w in words)
    ]
    for tag, category in [("树", "树"), ("图", "图")]:
        if tag in tags:
            matched.append(category)
    if matched:
        return list(dict.fromkeys(matched)), "official-tags"
    title_text = title.lower()
    matched = [
        category for category, words in RULES if any(w in title_text for w in words)
    ]
    if matched:
        return list(dict.fromkeys(matched)), "title-hint"
    return ["待分类"], "unclassified"


def parse_page(document):
    problems = []
    for row in ROWS.findall(document):
        anchor = TITLE.search(row)
        if not anchor:
            continue
        cells = CELLS.findall(row)
        if len(cells) < 7:
            raise ValueError("AcWing directory row shape changed")
        label = plain_text(cells[1])
        if not re.fullmatch(r"\d+", label):
            raise ValueError(f"Unexpected AcWing problem number: {label!r}")
        title = plain_text(anchor.group(3))
        url = urljoin(BASE_URL, html.unescape(anchor.group(2)))
        if not re.fullmatch(r"https://www\.acwing\.com/problem/content/\d+/", url):
            raise ValueError(f"Unexpected AcWing problem URL: {url}")
        tags = keywords(row, "keywords")
        categories, method = classify(title, tags)
        difficulty = plain_text(cells[-1])
        if difficulty not in {"简单", "中等", "困难"}:
            difficulty = "未评级"
        problems.append(
            {
                "id": f"ACW-{label}",
                "source": "acwing",
                "label": label,
                "title": title,
                "official_url": url,
                "category": categories[0],
                "categories": categories,
                "tags": tags,
                "origin_tags": keywords(row, "source"),
                "difficulty": difficulty,
                "rating": None,
                "paid": (
                    True if re.search(r"fa-lock\b|glyphicon-lock\b", cells[0]) else None
                ),
                "classification": method,
            }
        )
    page_numbers = [int(n) for n in re.findall(r'id="page_(\d+)"', document)]
    return problems, max(page_numbers, default=1)


def cached_response_date(path):
    """Read acquisition time, not the time a cached response was parsed again."""
    path = Path(path)
    metadata = path.with_suffix(".meta.json")
    try:
        retrieved_at = json.loads(metadata.read_text(encoding="utf-8"))["retrieved_at"]
        acquired = datetime.fromisoformat(retrieved_at)
        if acquired.tzinfo is None:
            raise ValueError("Cache acquisition time must include its timezone")
        return acquired.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    except (OSError, ValueError, KeyError, TypeError):
        # Compatibility for the initial cache, which predates acquisition sidecars.
        return (
            datetime.fromtimestamp(path.stat().st_mtime, ZoneInfo("Asia/Shanghai"))
            .date()
            .isoformat()
        )


def collect(
    cache_dir=None,
    output=None,
    interval=1.1,
    max_pages=None,
    refresh=False,
    snapshot_date=None,
):
    if snapshot_date is not None:
        snapshot_date = date.fromisoformat(str(snapshot_date)).isoformat()
    cache_dir = Path(cache_dir or ROOT / ".local/catalog-cache/acwing")
    output = Path(output or ROOT / "public/data/sources/acwing.json")
    cache_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    interval = max(1.05, interval)
    problems = {}
    content_urls = set()
    failures = []
    last_request = 0.0
    total_pages = None
    page = 1
    last_page_length = None
    response_dates = []
    with httpx.Client(timeout=35, follow_redirects=True) as client:
        while total_pages is None or page <= total_pages:
            if max_pages is not None and page > max_pages:
                failures.append(
                    f"受 --max-pages={max_pages} 限制，未继续请求后续页面。"
                )
                break
            path = cache_dir / f"page-{page}.html"
            try:
                if path.exists() and not refresh:
                    document = path.read_text(encoding="utf-8")
                else:
                    time.sleep(max(0.0, interval - (time.monotonic() - last_request)))
                    url = INDEX_URL if page == 1 else BASE_URL + f"/problem/{page}/"
                    last_request = time.monotonic()
                    response = client.get(url)
                    if response.status_code in {403, 429}:
                        failures.append(
                            f"第 {page} 页返回 HTTP {response.status_code}，停止同步，未绕过限制。"
                        )
                        break
                    response.raise_for_status()
                    document = response.text
                    path.write_text(document, encoding="utf-8")
                    path.with_suffix(".meta.json").write_text(
                        json.dumps(
                            {"retrieved_at": datetime.now(timezone.utc).isoformat()}
                        ),
                        encoding="utf-8",
                    )
                entries, discovered_pages = parse_page(document)
                if not entries:
                    raise ValueError("公开题目列表为空，可能发生访问限制或页面结构变更")
                total_pages = max(total_pages or 1, discovered_pages)
                if len(entries) > 50 or (page < total_pages and len(entries) != 50):
                    raise ValueError("公开目录分页行数改变，停止以避免误标完整覆盖")
                for problem in entries:
                    if problem["id"] in problems:
                        raise ValueError(f"重复题号 {problem['id']}，未继续抓取")
                    if problem["official_url"] in content_urls:
                        raise ValueError(f"重复 content URL {problem['official_url']}")
                    problems[problem["id"]] = problem
                    content_urls.add(problem["official_url"])
                last_page_length = len(entries)
                response_dates.append(cached_response_date(path))
                if page == 1 or page % 20 == 0 or page == total_pages:
                    print(
                        f"AcWing {page}/{total_pages} pages, {len(problems)} entries",
                        flush=True,
                    )
                page += 1
            except (httpx.HTTPError, ValueError) as error:
                failures.append(f"第 {page} 页：{error}")
                break
    complete = bool(total_pages and page > total_pages and not failures)
    expected_total = (total_pages - 1) * 50 + last_page_length if complete else None
    status = "complete" if complete else "partial"
    coverage_note = (
        f"已读取公开题库目录全部 {total_pages} 页，按页面显示题号去重；未登录，未抓取题面或测试数据。"
        if complete
        else f"已读取 {page - 1}/{total_pages or '?'} 页；" + "；".join(failures)
    )
    catalog = {
        "schema_version": 1,
        "source_id": "acwing",
        "name": "AcWing",
        "updated_at": snapshot_date or max(response_dates, default=None),
        "source_url": INDEX_URL,
        "metadata_provider": "AcWing 公开题目列表",
        "scope": "公开题库全部分页的题号、标题、来源标签、算法标签、难度和原站链接；付费访问状态未明确标出的条目不作推测。",
        "coverage": {
            "status": status,
            "expected_total": expected_total,
            "collected": len(problems),
            "note": coverage_note,
        },
        "problems": sorted(problems.values(), key=lambda p: int(p["label"])),
    }
    temporary = output.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(catalog, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    temporary.replace(output)
    print(f"Wrote {len(problems)} AcWing entries ({status}) to {output}", flush=True)
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--interval", type=float, default=1.1)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--date",
        dest="snapshot_date",
        type=date.fromisoformat,
        help="显式快照日期 YYYY-MM-DD；默认使用成功响应的实际获取日期",
    )
    args = parser.parse_args()
    collect(
        args.cache_dir,
        args.output,
        args.interval,
        args.max_pages,
        args.refresh,
        args.snapshot_date,
    )


if __name__ == "__main__":
    main()
