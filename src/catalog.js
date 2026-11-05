/** Public directory helpers. These entries never claim local judge support. */
export function normalizePat(pat) {
  const problems = Array.isArray(pat) ? pat : pat.problems;
  return problems.map((p) => ({
    ...p,
    source: "pat",
    label: `${p.level}${p.label}`,
    categories: p.category === "待分类" ? [] : [p.category],
    difficulty: p.level === "B" ? "乙级" : "甲级",
    rating: null,
    paid: null,
    classification: p.category === "待分类" ? "unclassified" : "curated-hint",
  }));
}

export function filterExternalProblems(
  problems,
  { query = "", category = "", difficulty = "", access = "" } = {},
) {
  const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return problems.filter(
    (p) =>
      (!category ||
        (category === "待分类"
          ? !p.categories?.length ||
            p.categories.includes("待分类") ||
            p.category === "待分类"
          : (p.categories || [p.category]).includes(category))) &&
      (!difficulty || `${p.source}|${p.difficulty}` === difficulty) &&
      (!access || (access === "paid" ? p.paid === true : p.paid === false)) &&
      words.every((word) =>
        (
          p.search_text ||
          [
            p.id,
            p.label,
            p.title,
            p.translated_title || "",
            p.category,
            ...(p.categories || []),
            ...(p.tags || []),
          ]
            .join(" ")
            .toLowerCase()
        ).includes(word),
      ),
  );
}

export function paginationNumbers(current, total) {
  const numbers = new Set([1, total]);
  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++)
    numbers.add(i);
  const result = [];
  for (const n of [...numbers].sort((a, b) => a - b)) {
    if (result.length && n - result.at(-1) > 1) result.push("…");
    result.push(n);
  }
  return result;
}

export function validateSourceCatalog(catalog, sourceId) {
  if (catalog.source_id !== sourceId || !Array.isArray(catalog.problems))
    throw Error("题目目录格式不正确");
  const ids = new Set();
  for (const p of catalog.problems) {
    if (!p.id || !p.title || p.source !== sourceId || ids.has(p.id))
      throw Error("目录存在重复题号或来源不一致");
    ids.add(p.id);
  }
  if (catalog.coverage.collected !== ids.size) throw Error("目录数量校验失败");
  return catalog;
}
