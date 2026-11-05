"""Collect public directory metadata without downloading problem statements.

Codeforces uses its official public problemset API. AtCoder metadata and estimated
difficulties come from the separately attributed AtCoder Problems community data.
LeetCode uses the Chinese site's anonymous public directory, including its public
premium flags. No authentication, private APIs, statements, or judge data are used.
"""

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import time
from urllib.parse import quote, urlparse
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".local" / "catalog-cache" / "global"
OUTPUT = ROOT / "public" / "data" / "sources"
CF_URL = "https://codeforces.com/api/problemset.problems"
AT_URL = "https://kenkoooo.com/atcoder/resources/merged-problems.json"
AT_MODELS_URL = "https://kenkoooo.com/atcoder/resources/problem-models.json"
LC_URL = "https://leetcode.cn/api/problems/all/"
LAST_REQUEST = {}

# These are topic labels from the official Codeforces API, not title guesses.
CF_TOPICS = {
    "dsu": "并查集",
    "trees": "树",
    "graphs": "图",
    "flows": "图",
    "graph matchings": "图",
    "shortest paths": "图",
    "2-sat": "图",
    "dp": "动态规划",
    "greedy": "贪心",
    "sortings": "排序与查找",
    "binary search": "排序与查找",
    "ternary search": "排序与查找",
    "two pointers": "数组与双指针",
    "hashing": "哈希与集合",
    "strings": "字符串",
    "string suffix structures": "字符串",
    "dfs and similar": "搜索与回溯",
    "brute force": "搜索与回溯",
    "meet-in-the-middle": "搜索与回溯",
    "math": "数学与数论",
    "number theory": "数学与数论",
    "combinatorics": "数学与数论",
    "probabilities": "数学与数论",
    "matrices": "数学与数论",
    "bitmasks": "位运算",
    "geometry": "计算几何",
    "divide and conquer": "分治",
    "fft": "多项式",
    "games": "博弈论",
    "interactive": "交互题",
    "implementation": "入门与模拟",
    "constructive algorithms": "构造",
}
TOPIC_ORDER = [
    "链表",
    "栈",
    "队列",
    "堆",
    "树",
    "并查集",
    "区间数据结构",
    "图",
    "动态规划",
    "字符串",
    "哈希与集合",
    "数组与双指针",
    "排序与查找",
    "搜索与回溯",
    "贪心",
    "数学与数论",
    "计算几何",
    "位运算",
    "分治",
    "多项式",
    "博弈论",
    "交互题",
    "构造",
    "入门与模拟",
]

# The datasets do not expose official algorithm tags for these sources. Only
# explicit names in a title are used, with classification="title-hint".
TITLE_HINTS = [
    (r"链表|\blinked list\b", "链表"),
    (r"并查集|\bunion.?find\b|\bdisjoint sets?\b", "并查集"),
    (
        r"线段树|树状数组|\bsegment tree\b|\bfenwick\b|\bbinary indexed tree\b",
        "区间数据结构",
    ),
    (r"二叉树|二叉搜索树|\bbinary tree\b|\bbinary search tree\b|\bbst\b|\bavl\b", "树"),
    (r"\bpriority queue\b|\bheap\b|优先队列|最小堆|最大堆", "堆"),
    (r"\bstack\b|单调栈|括号|\bstack sequence\b", "栈"),
    (r"\bqueue\b|队列", "队列"),
    (
        r"最短路|最短路径|最小生成树|最大流|最小割|二分图|拓扑|\bshortest path\b|\bmax.?flow\b|\bmin.?cut\b|\bminimum spanning tree\b|\bscc\b|\btwo.?sat\b|\b2.?sat\b",
        "图",
    ),
    (r"动态规划|背包|\bknapsack\b|\bdynamic programming\b", "动态规划"),
    (
        r"字符串|回文|字典树|\bstring\b|\bpalindrome\b|\btrie\b|\bkmp\b|\bz.?algorithm\b",
        "字符串",
    ),
    (r"哈希|\bhash\b", "哈希与集合"),
    (r"二分查找|排序|\bbinary search\b|\bsort(?:ing)?\b", "排序与查找"),
    (r"数组|双指针|\barray\b|\btwo pointers\b|滑动窗口", "数组与双指针"),
    (r"排列|组合|子集|\bpermutations?\b|\bsubsets?\b|回溯", "搜索与回溯"),
    (
        r"素数|质数|公约数|公倍数|快速幂|欧拉函数|模逆|\bgcd\b|\blcm\b|\bprimes?\b|\bfactorization\b|\bmod(?:ular)? inverse\b|\bfloor sum\b",
        "数学与数论",
    ),
]


def ordered_topics(topics):
    values = set(topics)
    return sorted(
        values, key=lambda x: (TOPIC_ORDER.index(x) if x in TOPIC_ORDER else 99, x)
    )


def title_topics(title):
    return ordered_topics(
        category for pattern, category in TITLE_HINTS if re.search(pattern, title, re.I)
    )


def fetch_json(name, url, refresh=False):
    """Cache only successful JSON and obey provider pacing within this run."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    host = urlparse(url).hostname
    delay = 2.1 if host == "codeforces.com" else 1.1
    elapsed = time.monotonic() - LAST_REQUEST.get(host, 0)
    if elapsed < delay:
        time.sleep(delay - elapsed)
    LAST_REQUEST[host] = time.monotonic()
    response = httpx.get(url, timeout=60, follow_redirects=True)
    response.raise_for_status()
    data = response.json()
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
    return data


def make_catalog(
    source_id, name, source_url, provider, scope, problems, expected, note, updated
):
    identities = [problem["id"] for problem in problems]
    if len(set(identities)) != len(identities):
        raise ValueError(f"{source_id}: duplicate problem identifiers")
    if not all(
        problem["title"] and problem["official_url"].startswith("https://")
        for problem in problems
    ):
        raise ValueError(f"{source_id}: incomplete public metadata")
    return {
        "schema_version": 1,
        "source_id": source_id,
        "name": name,
        "updated_at": updated
        or datetime.fromtimestamp(
            (CACHE / f"{'leetcode_cn' if source_id == 'leetcode' else source_id}.json")
            .stat()
            .st_mtime,
            ZoneInfo("Asia/Shanghai"),
        )
        .date()
        .isoformat(),
        "source_url": source_url,
        "metadata_provider": provider,
        "scope": scope,
        "coverage": {
            "status": "complete" if len(problems) == expected else "partial",
            "expected_total": expected,
            "collected": len(problems),
            "note": note,
        },
        "problems": problems,
    }


def codeforces(refresh=False, updated=None):
    data = fetch_json("codeforces", CF_URL, refresh)
    if data.get("status") != "OK":
        raise ValueError(data.get("comment", "Codeforces API did not return OK"))
    rows = data["result"]["problems"]
    problems = []
    for row in rows:
        label = f"{row['contestId']}{row['index']}"
        tags = row.get("tags", [])
        topics = ordered_topics(CF_TOPICS[tag] for tag in tags if tag in CF_TOPICS)
        rating = row.get("rating")
        problems.append(
            {
                "id": "CF-" + label,
                "source": "codeforces",
                "label": label,
                "title": row["name"],
                "official_url": f"https://codeforces.com/problemset/problem/{row['contestId']}/{quote(row['index'], safe='')}",
                "category": topics[0] if topics else "待分类",
                "categories": topics,
                "tags": tags,
                "difficulty": str(rating) if rating is not None else "未评级",
                "rating": rating,
                "paid": None,
                "classification": "official-tags" if topics else "unclassified",
            }
        )
    problems.sort(
        key=lambda row: (int(re.match(r"\d+", row["label"])[0]), row["label"])
    )
    return make_catalog(
        "codeforces",
        "Codeforces",
        "https://codeforces.com/problemset",
        "Codeforces 官方公开 API",
        "官方 problemset.problems 主站公开题集接口返回的全部题目；不包含 Gym 或需要权限的题目集。",
        problems,
        len(rows),
        "算法标签与 rating 来自官方 API；未返回 rating 的题目标为未评级。这里只保留目录元数据和官方链接。",
        updated,
    )


def atcoder(refresh=False, updated=None):
    rows = fetch_json("atcoder", AT_URL, refresh)
    models = {}
    try:
        models = fetch_json("atcoder_models", AT_MODELS_URL, refresh)
    except (httpx.HTTPError, ValueError) as error:
        print(f"AtCoder estimated ratings unavailable: {error}", flush=True)
    problems = []
    for row in rows:
        title = row.get("name") or row["title"]
        topics = title_topics(title)
        model = models.get(row["id"], {})
        rating = model.get("difficulty")
        # Preserve the community model's raw estimate, rather than silently
        # presenting it as an official AtCoder rating or applying an undocumented scale.
        if not isinstance(rating, (int, float)) or not math.isfinite(rating):
            rating = None
        problems.append(
            {
                "id": "AT-" + row["id"],
                "source": "atcoder",
                "label": f"{row['contest_id']} {row['problem_index']}",
                "title": title,
                "official_url": f"https://atcoder.jp/contests/{quote(row['contest_id'], safe='')}/tasks/{quote(row['id'], safe='')}",
                "category": topics[0] if topics else "待分类",
                "categories": topics,
                "tags": topics,
                "difficulty": f"估计 {rating}" if rating is not None else "未评级",
                "rating": rating,
                "paid": None,
                "classification": "title-hint" if topics else "unclassified",
            }
        )
    problems.sort(key=lambda row: row["label"].casefold())
    return make_catalog(
        "atcoder",
        "AtCoder",
        "https://kenkoooo.com/atcoder/",
        "AtCoder Problems 社区维护数据",
        "AtCoder Problems merged-problems 公共数据集当前全部条目；完整是相对此数据集，不保证覆盖 AtCoder 的所有比赛和历史题目。",
        problems,
        len(rows),
        "官方作答链接指向 atcoder.jp。rating 是社区模型的原始估计值，非官方难度；分类仅由标题中的明确算法/数据结构名称提供提示，未核对条目保留待分类。",
        updated,
    )


def leetcode(refresh=False, updated=None):
    data = fetch_json("leetcode_cn", LC_URL, refresh)
    rows = data["stat_status_pairs"]
    problems = []
    for row in rows:
        stat = row["stat"]
        if stat.get("question__hide"):
            continue
        label = str(stat["frontend_question_id"])
        title = stat["question__title"]
        topics = title_topics(title)
        problems.append(
            {
                "id": "LC-" + label,
                "source": "leetcode",
                "label": label,
                "title": title,
                "official_url": f"https://leetcode.cn/problems/{quote(stat['question__title_slug'], safe='')}/",
                "category": topics[0] if topics else "待分类",
                "categories": topics,
                "tags": topics,
                "difficulty": {1: "简单", 2: "中等", 3: "困难"}.get(
                    row["difficulty"]["level"], "未评级"
                ),
                "rating": None,
                "paid": bool(row.get("paid_only")),
                "classification": "title-hint" if topics else "unclassified",
            }
        )
    problems.sort(
        key=lambda row: (
            (0, int(row["label"])) if row["label"].isdigit() else (1, row["label"])
        )
    )
    return make_catalog(
        "leetcode",
        "LeetCode",
        "https://leetcode.cn/problemset/",
        "力扣中国站官方匿名公开题目目录",
        "api/problems/all 匿名接口公开列出的全部目录元数据，包含可公开查看标题的会员题；不收录会员题面、答案或私有测试点。",
        problems,
        int(data["num_total"]),
        "难度和会员标记来自官方公开目录。该目录未提供官方算法标签，因此分类仅作标题提示；未核对条目保留待分类。国际站接口被访问防护拒绝，未尝试绕过；使用正常可访问的中国站公开目录。",
        updated,
    )


COLLECTORS = {"codeforces": codeforces, "atcoder": atcoder, "leetcode": leetcode}


def main():
    parser = argparse.ArgumentParser(
        description="Sync public CF / AtCoder / LeetCode metadata"
    )
    parser.add_argument("--source", choices=COLLECTORS, action="append")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh successful public metadata caches",
    )
    parser.add_argument(
        "--date",
        help="Verified snapshot date override; defaults to the successful response cache date, not the rerun date",
    )
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for identity in args.source or COLLECTORS:
        catalog = COLLECTORS[identity](refresh=args.refresh, updated=args.date)
        destination = OUTPUT / f"{identity}.json"
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(catalog, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        temporary.replace(destination)
        print(
            f"{catalog['name']}: {catalog['coverage']['collected']} / {catalog['coverage']['expected_total']} public metadata records; {sum(bool(p['categories']) for p in catalog['problems'])} topic hints; {sum(p['paid'] is True for p in catalog['problems'])} premium titles",
            flush=True,
        )


if __name__ == "__main__":
    main()
