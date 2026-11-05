import test from "node:test";
import assert from "node:assert/strict";
import { restoreDraft } from "../src/drafts.js";
import {
  difficultyChoice,
  filterExternalProblems,
  normalizePat,
  paginationNumbers,
  validateSourceCatalog,
} from "../src/catalog.js";
import {
  escapeHtml,
  safeUrl,
  localEndpoint,
  filterProblems,
  mergeCatalog,
} from "../src/core.js";

test("new editors start empty and real user drafts are preserved verbatim", () => {
  for (const value of [undefined, null, "", 42])
    assert.equal(restoreDraft(value), "");
  const code = '\n#include <stdio.h>\nint main(void) { puts("hello"); }\n';
  assert.equal(restoreDraft(code), code);
  assert.equal(restoreDraft("print(7)\n"), "print(7)\n");
});
test("untouched legacy starter code does not reappear as a saved draft", () => {
  const legacy =
    "#include <stdio.h>\r\n\r\nint main(void) {\r\n    // 在这里编写你的程序\r\n    return 0;\r\n}\r\n";
  assert.equal(restoreDraft(legacy), "");
  const edited = legacy.replace("return 0;", 'puts("mine"); return 0;');
  assert.equal(restoreDraft(edited), edited);
});

test("external categories search all tags and keep unknown access distinct from free", () => {
  const problems = [
    {
      id: "LG-P1",
      source: "luogu",
      label: "P1",
      title: "区间查询",
      categories: ["树", "区间数据结构"],
      tags: ["线段树"],
      difficulty: "进阶",
      paid: null,
    },
    {
      id: "LC-1",
      source: "leetcode",
      label: "1",
      title: "Two Sum",
      categories: ["哈希与集合"],
      tags: [],
      difficulty: "简单",
      paid: false,
    },
    {
      id: "LC-2",
      source: "leetcode",
      label: "2",
      title: "Premium",
      categories: [],
      category: "待分类",
      tags: [],
      difficulty: "中等",
      paid: true,
    },
    {
      id: "ACW-3",
      source: "acwing",
      label: "3",
      title: "Unclassified",
      categories: ["待分类"],
      tags: [],
      difficulty: "简单",
      paid: null,
    },
  ];
  assert.equal(
    filterExternalProblems(problems, {
      category: "区间数据结构",
      query: "P1 线段树",
    })[0].id,
    "LG-P1",
  );
  assert.equal(filterExternalProblems(problems, { access: "free" }).length, 1);
  assert.equal(
    filterExternalProblems(problems, { access: "paid" })[0].id,
    "LC-2",
  );
  assert.equal(
    filterExternalProblems(problems, { category: "待分类" }).length,
    2,
  );
  assert.equal(
    filterExternalProblems(problems, { difficulty: "leetcode|简单" })[0].id,
    "LC-1",
  );
});
test("AtCoder difficulty bands preserve boundaries and separate unrated problems", () => {
  const rated = (rating) => ({
    source: "atcoder", rating, difficulty: `估计 ${rating}`, categories: [],
  });
  const problems = [-200, 399, 400, 799, 800, 3199, 3200, 4500].map(rated);
  problems.push({ source: "atcoder", rating: null, difficulty: "未评级" });
  problems.push({ source: "codeforces", rating: 400, difficulty: "400" });
  assert.deepEqual(
    filterExternalProblems(problems, { difficulty: difficultyChoice(rated(400)).key }).map((p) => p.rating),
    [400, 799],
  );
  assert.deepEqual(
    filterExternalProblems(problems, { difficulty: difficultyChoice(rated(-200)).key }).map((p) => p.rating),
    [-200, 399],
  );
  assert.equal(filterExternalProblems(problems, { difficulty: "atcoder|rating:3200+" }).length, 2);
  assert.equal(filterExternalProblems(problems, { difficulty: "atcoder|未评级" }).length, 1);
  assert.equal(new Set(Array.from({ length: 7000 }, (_, i) => difficultyChoice(rated(i - 1500)).key)).size, 9);
});

test("pagination stays bounded for tens of thousands of indexed problems", () => {
  const pages = paginationNumbers(450, 1200);
  assert.ok(pages.length <= 9);
  assert.equal(pages[0], 1);
  assert.equal(pages.at(-1), 1200);
  assert.ok(pages.includes(450));
  assert.deepEqual(paginationNumbers(1, 1), [1]);
  assert.ok(paginationNumbers(1, 4).includes(4));
});
test("legacy PAT metadata retains official links without claiming local judgement", () => {
  const p = normalizePat({
    problems: [
      {
        id: "PAT-B1001",
        label: "1001",
        level: "B",
        category: "待分类",
        title: "Example",
        tags: [],
        official_url: "https://pintia.cn/",
      },
    ],
  })[0];
  assert.equal(p.source, "pat");
  assert.equal(p.difficulty, "乙级");
  assert.deepEqual(p.categories, []);
  assert.equal(p.paid, null);
  assert.equal(p.official_url, "https://pintia.cn/");
  assert.equal(
    normalizePat([{ ...p, level: "B", label: "1001" }])[0].source,
    "pat",
  );
});
test("source catalogs reject duplicate IDs, wrong sources and mismatched counts", () => {
  const item = { id: "CF-1A", source: "codeforces", title: "A" };
  const data = {
    source_id: "codeforces",
    coverage: { collected: 1 },
    problems: [item],
  };
  assert.equal(validateSourceCatalog(data, "codeforces"), data);
  assert.throws(() =>
    validateSourceCatalog({ ...data, problems: [item, item] }, "codeforces"),
  );
  assert.throws(() => validateSourceCatalog(data, "leetcode"));
  assert.throws(() =>
    validateSourceCatalog(
      { ...data, coverage: { collected: 2 } },
      "codeforces",
    ),
  );
});

test("untrusted problem text is escaped and source links reject executable schemes", () => {
  assert.equal(
    escapeHtml('<img onerror="alert(1)">'),
    "&lt;img onerror=&quot;alert(1)&quot;&gt;",
  );
  assert.equal(safeUrl("javascript:alert(1)"), "");
  assert.equal(safeUrl("https://pintia.cn/"), "https://pintia.cn/");
});
test("tokens can only be sent to explicit loopback services", () => {
  assert.equal(
    localEndpoint("http://127.0.0.1:8765/"),
    "http://127.0.0.1:8765",
  );
  for (const url of [
    "http://example.com",
    "http://127.0.0.1.evil.test",
    "http://user@localhost:8765",
    "http://localhost:8765/path",
    "file:///etc/passwd",
  ])
    assert.throws(() => localEndpoint(url));
});
test("classification, tag search, difficulty, and actual progress combine correctly", () => {
  const problems = [
    {
      id: "1",
      title: "最小堆",
      category: "堆",
      tags: ["优先队列"],
      difficulty: "基础",
    },
    { id: "2", title: "树高", category: "树", tags: [], difficulty: "入门" },
  ];
  assert.deepEqual(
    filterProblems(problems, { query: "优先 队列" }).map((p) => p.id),
    ["1"],
  );
  assert.deepEqual(
    filterProblems(problems, {
      category: "堆",
      status: "AC",
      progress: { 1: "AC" },
    }).map((p) => p.id),
    ["1"],
  );
  assert.equal(
    filterProblems(problems, {
      status: "tried",
      progress: { 1: "AC", 2: "WA" },
    })[0].id,
    "2",
  );
  assert.equal(
    filterProblems(problems, {
      difficulty: "入门",
      status: "untried",
      progress: { 1: "AC" },
    })[0].id,
    "2",
  );
});
test("imported problem metadata merges by stable problem ID", () => {
  assert.deepEqual(
    mergeCatalog(
      [{ id: "1", title: "a" }],
      [
        { id: "1", title: "b" },
        { id: "2", title: "c" },
      ],
    ).map((p) => p.title),
    ["b", "c"],
  );
});
