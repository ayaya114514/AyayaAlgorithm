import test from "node:test";
import assert from "node:assert/strict";
import {
  escapeHtml,
  safeUrl,
  localEndpoint,
  filterProblems,
  mergeCatalog,
} from "../src/core.js";

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
