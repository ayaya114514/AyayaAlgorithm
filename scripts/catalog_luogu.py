"""Read Luogu's public, server-rendered problem directory at a bounded rate."""

import argparse
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
import re
import time
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.luogu.com.cn"
DIFFICULTIES = [
    "暂无评定",
    "入门",
    "普及−",
    "普及/提高−",
    "普及+/提高",
    "提高+/省选−",
    "省选/NOI−",
    "NOI/NOI+/CTSC",
]
TOPICS = [
    ("链表", ["链表"]),
    ("并查集", ["并查集"]),
    ("区间数据结构", ["线段树", "树状数组", "st 表", "st表", "分块", "莫队", "主席树"]),
    ("堆", ["堆", "优先队列"]),
    ("栈", ["栈"]),
    ("队列", ["队列"]),
    ("树", ["树", "lca", "倍增", "树链", "点分治"]),
    ("图", ["图", "最短路", "生成树", "网络流", "匹配", "拓扑", "连通", "差分约束"]),
    ("动态规划", ["动态规划", "dp", "背包"]),
    ("字符串", ["字符串", "kmp", "trie", "字典树", "后缀", "回文", "ac 自动机"]),
    ("哈希与集合", ["哈希", "散列", "集合"]),
    ("排序与查找", ["排序", "二分", "查找", "分治", "逆序对"]),
    ("搜索与回溯", ["搜索", "dfs", "bfs", "回溯", "枚举", "迭代加深"]),
    ("贪心", ["贪心"]),
    (
        "数学与数论",
        [
            "数论",
            "数学",
            "组合",
            "素数",
            "概率",
            "矩阵",
            "多项式",
            "博弈",
            "几何",
            "线性代数",
        ],
    ),
    ("数组与双指针", ["双指针", "数组", "滑动窗口"]),
    ("入门与模拟", ["模拟", "入门", "顺序结构", "循环结构", "分支结构", "递推"]),
]


def classify(tags):
    lowered = " ".join(tags).lower()
    return [
        category
        for category, keywords in TOPICS
        if any(word in lowered for word in keywords)
    ]


def parse_page(text):
    match = re.search(r'<script id="lentille-context"[^>]*>(.*?)</script>', text, re.S)
    if not match:
        raise ValueError("公开页面缺少 lentille-context；停止同步，不尝试绕过访问限制")
    data = json.loads(match.group(1))
    if data.get("status") != 200 or data.get("template") != "problem.list":
        raise ValueError("不是公开题目列表")
    return data["data"]["problems"]


def collect(
    cache_dir=None,
    output=None,
    interval=1.1,
    max_pages=None,
    refresh=False,
    snapshot_date=None,
):
    cache = Path(cache_dir or ROOT / ".local/catalog-cache/luogu")
    destination = Path(output or ROOT / "public/data/sources/luogu.json")
    cache.mkdir(parents=True, exist_ok=True)
    interval = max(1.05, interval)
    if snapshot_date is not None:
        snapshot_date = date.fromisoformat(str(snapshot_date)).isoformat()
    last_request = 0.0
    with httpx.Client(timeout=40, follow_redirects=True) as client:

        def request(url):
            nonlocal last_request
            time.sleep(max(0, interval - (time.monotonic() - last_request)))
            response = client.get(url)
            last_request = time.monotonic()
            response.raise_for_status()
            return response

        tag_cache = cache / "tags.json"
        tags_by_id = {}
        try:
            if tag_cache.exists() and not refresh:
                tag_data = json.loads(tag_cache.read_text())
            else:
                tag_data = request(BASE + "/_lfe/tags").json()
                tag_cache.write_text(json.dumps(tag_data, ensure_ascii=False))
            # The endpoint returns {tags:[{id,name,type,...}],...}.
            tags_by_id = {tag["id"]: tag["name"] for tag in tag_data.get("tags", [])}
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            print(f"Luogu tag names unavailable: {type(error).__name__}", flush=True)

        problems = {}
        response_dates = []
        expected = None
        pages = 1
        issue = ""
        for page in range(1, 10001):
            if page > pages or (max_pages and page > max_pages):
                break
            path = cache / f"page-{page}.json"
            try:
                if path.exists() and not refresh:
                    data = json.loads(path.read_text())
                elif page == 1 and (cache / "page-1.html").exists() and not refresh:
                    data = parse_page((cache / "page-1.html").read_text())
                    path.write_text(json.dumps(data, ensure_ascii=False))
                else:
                    data = parse_page(
                        request(f"{BASE}/problem/list?type=luogu&page={page}").text
                    )
                    path.write_text(json.dumps(data, ensure_ascii=False))
                    path.with_suffix(".meta.json").write_text(
                        json.dumps(
                            {"retrieved_at": datetime.now(timezone.utc).isoformat()}
                        )
                    )
                metadata = path.with_suffix(".meta.json")
                acquired = (
                    datetime.fromisoformat(
                        json.loads(metadata.read_text())["retrieved_at"]
                    )
                    if metadata.exists()
                    else datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
                )
                response_dates.append(
                    acquired.astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
                )
                expected = data["count"]
                pages = math.ceil(expected / data["perPage"])
                for item in data["result"]:
                    pid = item["pid"]
                    tags = [
                        tags_by_id[tag]
                        for tag in item.get("tags", [])
                        if tag in tags_by_id
                    ]
                    categories = classify(tags)
                    problems[pid] = dict(
                        id=f"LG-{pid}",
                        source="luogu",
                        label=pid,
                        title=item["name"],
                        official_url=f"{BASE}/problem/{pid}",
                        category=categories[0] if categories else "待分类",
                        categories=categories,
                        tags=tags,
                        difficulty=(
                            DIFFICULTIES[item["difficulty"]]
                            if 0 <= item["difficulty"] < len(DIFFICULTIES)
                            else "暂无评定"
                        ),
                        rating=None,
                        paid=None,
                        classification=(
                            "official-tags" if categories else "unclassified"
                        ),
                    )
                if page == 1 or page % 20 == 0 or page == pages:
                    print(
                        f"Luogu {page}/{pages}: {len(problems)}/{expected} entries",
                        flush=True,
                    )
            except (httpx.HTTPError, ValueError, KeyError) as error:
                issue = f"第 {page} 页读取中止：{type(error).__name__}；保留已读取目录，未绕过访问限制。"
                print(issue, flush=True)
                break
        complete = expected is not None and len(problems) == expected and not issue
        result = dict(
            schema_version=1,
            source_id="luogu",
            name="洛谷",
            updated_at=snapshot_date or max(response_dates, default=None),
            source_url=BASE + "/problem/list?type=luogu",
            metadata_provider="洛谷官方公开题目列表与标签",
            scope="洛谷主站题库（type=luogu）；不重复收录其远程 OJ 镜像题库",
            coverage=dict(
                status="complete" if complete else "partial",
                expected_total=expected,
                collected=len(problems),
                note=issue
                or (
                    "已读取该公开目录的所有分页；目录快照可能随原站变动。"
                    if complete
                    else "本次只完成部分分页。"
                ),
            ),
            problems=list(problems.values()),
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(result, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary.replace(destination)
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-pages", type=int)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--date", dest="snapshot_date", type=date.fromisoformat)
    args = parser.parse_args()
    catalog = collect(
        max_pages=args.max_pages, refresh=args.refresh, snapshot_date=args.snapshot_date
    )
    print(json.dumps(catalog["coverage"], ensure_ascii=False), flush=True)
