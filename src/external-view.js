import {
  filterExternalProblems,
  normalizePat,
  paginationNumbers,
  validateSourceCatalog,
} from "./catalog.js";
import "./external.css";

export function createExternalView({
  state,
  DATA,
  icon,
  e,
  safeUrl,
  icons,
  shell,
  footer,
  go,
}) {
  const cache = new Map(),
    pending = new Map();
  let active = "luogu",
    query = "",
    category = "",
    difficulty = "",
    access = "",
    page = 1;
  const number = (n) => Number(n || 0).toLocaleString("zh-CN");
  const sourceName = (id) =>
    state.sources.find((s) => s.source_id === id)?.name || id;
  const selectedSources = () =>
    active === "all"
      ? state.sources
      : state.sources.filter((s) => s.source_id === active);
  const selectedProblems = () =>
    selectedSources().flatMap((s) => cache.get(s.source_id) || []);
  const current = () => location.hash.startsWith("#/catalog");
  const ready = () => selectedSources().every((s) => cache.has(s.source_id));
  const total = () =>
    state.sources.reduce((sum, s) => sum + s.coverage.collected, 0);
  const categoryCounts = () => {
    const counts = new Map();
    for (const p of selectedProblems())
      for (const c of p.categories?.length ? p.categories : ["待分类"])
        counts.set(c, (counts.get(c) || 0) + 1);
    return [...counts].sort(([a], [b]) =>
      a === "待分类" ? 1 : b === "待分类" ? -1 : a.localeCompare(b, "zh-CN"),
    );
  };
  function sidebar() {
    return `<div class="source-sidebar"><div class="source-sidebar-title">收录平台</div><button class="${active === "all" ? "selected" : ""}" data-action="cat-source" data-value="all"><span>全部平台</span><small>${number(total())}</small></button>${state.sources.map((s) => `<button class="${active === s.source_id ? "selected" : ""}" data-action="cat-source" data-value="${e(s.source_id)}"><span>${e(s.name)}</span><small>${number(s.coverage.collected)}</small></button>`).join("")}<h3>算法分类 · 可多标签关联</h3><div class="catalog-categories"><button class="${!category ? "selected" : ""}" data-action="cat-category" data-value=""><span>全部分类</span><small>${ready() ? number(selectedProblems().length) : "…"}</small></button>${categoryCounts()
      .map(
        ([c, n]) =>
          `<button class="${category === c ? "selected" : ""}" data-action="cat-category" data-value="${e(c)}"><span>${e(c)}</span><small>${number(n)}</small></button>`,
      )
      .join(
        "",
      )}</div><div class="catalog-index-total"><strong>${number(total())}</strong>条公开题目索引 · ${state.sources.length} 个来源</div><p class="source-aside-note">这里只展示题号、标题、标签、难度与原站链接。<br>未公开算法标签的条目保留待分类，收录范围详见页面底部。</p></div>`;
  }
  async function load(source) {
    if (cache.has(source.source_id)) return;
    if (pending.has(source.source_id)) return pending.get(source.source_id);
    const promise = (async () => {
      let problems;
      if (source.source_id === "pat") problems = normalizePat(state.pat);
      else {
        const response = await fetch(
          DATA +
            "data/" +
            source.path +
            "?v=" +
            encodeURIComponent(source.revision || source.updated_at),
        );
        if (!response.ok)
          throw Error(`${source.name} 目录读取失败（${response.status}）`);
        const data = validateSourceCatalog(
          await response.json(),
          source.source_id,
        );
        if (data.problems.length !== source.coverage.collected)
          throw Error("目录与索引版本不一致，请刷新页面后重试");
        problems = data.problems;
      }
      for (const p of problems)
        p.search_text = [
          p.id,
          p.label,
          p.title,
          p.translated_title || "",
          p.category,
          ...(p.categories || []),
          ...(p.tags || []),
        ]
          .join(" ")
          .toLowerCase();
      cache.set(source.source_id, problems);
    })();
    pending.set(source.source_id, promise);
    try {
      await promise;
    } finally {
      pending.delete(source.source_id);
    }
  }
  function render(sourceId) {
    const next =
      sourceId === "all" || state.sources.some((s) => s.source_id === sourceId)
        ? sourceId
        : "luogu";
    if (active !== next) {
      active = next;
      query = category = difficulty = access = "";
      page = 1;
    }
    const wanted = active;
    const selected = selectedSources();
    shell(
      `<div class="breadcrumb">题目集 ${icon("chevron-right")} <span>多平台题库索引</span></div><div class="page-heading"><div><div class="eyebrow">OPEN PROBLEM DIRECTORY</div><h1>多平台题库索引</h1><p>优先整理洛谷与 AcWing，汇集竞赛、面试和课程练习。</p></div><button class="catalog-heading-total" data-action="cat-source" data-value="all"><strong>${number(total())}</strong> 条索引 · 查看全部</button></div><div class="source-grid">${state.sources.map((s) => `<button class="source-card ${active === s.source_id ? "selected" : ""}" data-action="cat-source" data-value="${e(s.source_id)}"><strong>${e(s.name)}</strong><span class="source-count">${number(s.coverage.collected)}</span><small>更新 ${e(s.updated_at)} · ${e(s.scope_short || "公开题目目录")}</small><span class="source-status ${s.coverage.status === "complete" ? "" : "partial"}">${s.coverage.status === "complete" ? "目录已同步" : "部分收录"}</span></button>`).join("")}</div><div class="catalog-notice"><strong>原站作答与本地练习分开展示。</strong> 索引中的题目在原平台提交；“同类本地练习”按算法关联，使用本站原创题面与自建测试，题目格式和测试点可能不同。会员题仅收录公开元数据。</div><section class="panel"><div class="catalog-toolbar"><h2>${active === "all" ? "全部平台" : e(sourceName(active))} · 公开题目目录</h2><small>${selected
        .map((s) => e(s.updated_at))
        .filter((v, i, a) => a.indexOf(v) === i)
        .join(
          " / ",
        )} 快照</small></div><div class="catalog-filterbar"><label class="search-field">${icon("search")}<input id="catalog-search" type="search" placeholder="搜索题号、标题或算法标签" aria-label="搜索多平台题目" value="${e(query)}"></label><select id="catalog-category" aria-label="筛选索引算法分类"><option value="">全部分类</option></select><select id="catalog-difficulty" aria-label="筛选原站难度"><option value="">全部原站难度</option></select><select id="catalog-access" aria-label="筛选会员标记"><option value="">全部权限标记</option><option value="free" ${access === "free" ? "selected" : ""}>已标明非会员题</option><option value="paid" ${access === "paid" ? "selected" : ""}>已标明会员题</option></select><button class="text-button" data-action="cat-reset">重置</button><span class="catalog-filter-caption">各平台难度体系分别保留</span></div><div id="catalog-results"><div class="catalog-loading"><span class="spinner"></span>正在载入所选平台目录…</div></div><details class="coverage-details"><summary>查看数据来源、完整性与分类说明</summary><ul>${selected.map((s) => `<li><strong>${e(s.name)} · ${number(s.coverage.collected)} / ${s.coverage.expected_total == null ? "未知总数" : number(s.coverage.expected_total)}</strong><br>${e(s.metadata_provider)}<br>范围：${e(s.scope)}<br>${e(s.coverage.note)} <a href="${e(safeUrl(s.source_url))}" target="_blank" rel="noopener noreferrer">来源入口 ${icon("external-link")}</a></li>`).join("")}</ul></details></section><div class="catalog-performance-note">目录按平台加载；搜索支持空格分隔的多个关键词。算法分类可能重叠；按来源计数，跨平台同题不做全局去重。</div>${footer()}`,
    );
    document
      .querySelector("#catalog-search")
      .addEventListener("input", (ev) => {
        query = ev.target.value;
        page = 1;
        clearTimeout(render.timer);
        render.timer = setTimeout(rows, 130);
      });
    for (const [id, setter] of [
      ["catalog-category", (v) => (category = v)],
      ["catalog-difficulty", (v) => (difficulty = v)],
      ["catalog-access", (v) => (access = v)],
    ])
      document.querySelector("#" + id).addEventListener("change", (ev) => {
        setter(ev.target.value);
        page = 1;
        rows();
        refreshSidebar();
      });
    if (ready()) {
      filters();
      rows();
    } else
      Promise.all(selected.map(load))
        .then(() => {
          if (
            current() &&
            active === wanted &&
            (location.hash.split("/")[2] || "luogu") === active
          ) {
            filters();
            rows();
            refreshSidebar();
          }
        })
        .catch((error) => {
          if (current() && active === wanted)
            document.querySelector("#catalog-results").innerHTML =
              `<div class="empty">${e(error.message)}<button class="button secondary" data-action="cat-retry">重新加载</button></div>`;
        });
  }
  function refreshSidebar() {
    const node = document.querySelector("#sidebar");
    if (node && current()) {
      node.innerHTML = sidebar();
      icons();
    }
  }
  function filters() {
    const node = document.querySelector("#catalog-category");
    if (!node) return;
    node.innerHTML = `<option value="">全部分类</option>${categoryCounts()
      .map(
        ([c, n]) =>
          `<option value="${e(c)}" ${category === c ? "selected" : ""}>${e(c)} (${number(n)})</option>`,
      )
      .join("")}`;
    const choices = [
      ...new Map(
        selectedProblems().map((p) => [
          `${p.source}|${p.difficulty}`,
          `${sourceName(p.source)} · ${p.difficulty}`,
        ]),
      ).entries(),
    ].sort((a, b) => a[1].localeCompare(b[1], "zh-CN", { numeric: true }));
    document.querySelector("#catalog-difficulty").innerHTML =
      `<option value="">全部原站难度</option>${choices.map(([key, label]) => `<option value="${e(key)}" ${difficulty === key ? "selected" : ""}>${e(label)}</option>`).join("")}`;
  }
  function rows() {
    const node = document.querySelector("#catalog-results");
    if (!node || !current() || !ready()) return;
    const result = filterExternalProblems(selectedProblems(), {
        query,
        category,
        difficulty,
        access,
      }),
      size = 50,
      pages = Math.max(1, Math.ceil(result.length / size));
    page = Math.max(1, Math.min(pages, page));
    const visible = result.slice((page - 1) * size, page * size);
    node.innerHTML = `<div class="table-scroll"><table class="problem-table catalog-table"><thead><tr><th>来源 / 题号</th><th class="title-column">标题</th><th>算法分类</th><th>原站难度</th><th>作答 / 关联练习</th></tr></thead><tbody>${
      visible
        .map((p) => {
          const local = (p.categories || []).find((c) =>
            state.problems.some((lp) => lp.category === c),
          );
          const method =
            p.classification === "official-tags"
              ? "官方算法标签"
              : p.classification === "unclassified"
                ? "原站标签未公开或未匹配"
                : p.classification === "curated-hint"
                  ? "本站整理提示"
                  : "按题名提示";
          const displayDifficulty =
            p.source === "atcoder" && p.rating != null
              ? `社区估计 ${p.rating}`
              : p.difficulty;
          return `<tr><td><span class="source-pill">${e(sourceName(p.source))}</span><div class="problem-id">${e(p.label)}</div></td><td><a class="catalog-title" href="${e(safeUrl(p.official_url))}" target="_blank" rel="noopener noreferrer">${e(p.title)}${p.paid === true ? '<span class="paid-pill">会员题</span>' : ""}</a><div class="tagline">${p.tags
            .slice(0, 4)
            .map((t) => `<span>${e(t)}</span>`)
            .join("")}</div></td><td>${
            p.categories?.length
              ? p.categories
                  .slice(0, 2)
                  .map(
                    (c) =>
                      `<button class="category-tag" data-action="cat-category" data-value="${e(c)}">${e(c)}</button>`,
                  )
                  .join(" ")
              : '<span class="catalog-unclassified">待分类</span>'
          }<div class="category-classification">${method}</div></td><td><span class="difficulty">${e(displayDifficulty)}</span></td><td class="catalog-row-actions"><a class="external-action" href="${e(safeUrl(p.official_url))}" target="_blank" rel="noopener noreferrer">原站作答 ${icon("external-link")}</a>${local ? `<button class="local-related" data-action="category" data-value="${e(local)}">同类本地练习 ${icon("chevron-right")}</button>` : ""}</td></tr>`;
        })
        .join("") ||
      '<tr><td colspan="5" class="empty">没有找到符合条件的题目<button class="text-button" data-action="cat-reset">清除筛选</button></td></tr>'
    }</tbody></table></div><div class="pagination"><span>显示 ${number(result.length ? (page - 1) * size + 1 : 0)}–${number(Math.min(page * size, result.length))} 条，共 ${number(result.length)} 条</span><div class="catalog-page-controls"><button class="page-arrow" data-action="cat-page" data-value="${page - 1}" ${page === 1 ? "disabled" : ""} aria-label="上一页">${icon("chevron-left")}</button>${paginationNumbers(
      page,
      pages,
    )
      .map((n) =>
        n === "…"
          ? '<span class="page-ellipsis">…</span>'
          : `<button class="page-number ${page === n ? "selected" : ""}" data-action="cat-page" data-value="${n}">${number(n)}</button>`,
      )
      .join(
        "",
      )}<button class="page-arrow" data-action="cat-page" data-value="${page + 1}" ${page === pages ? "disabled" : ""} aria-label="下一页">${icon("chevron-right")}</button><label class="catalog-jump">跳至<input id="catalog-page" type="number" min="1" max="${pages}" value="${page}" aria-label="跳转索引页码"><button class="text-button" data-action="cat-jump">页</button></label></div></div>`;
    icons();
    document
      .querySelector("#catalog-page")
      .addEventListener("keydown", (ev) => {
        if (ev.key === "Enter") {
          page = Number(ev.target.value) || 1;
          rows();
        }
      });
  }
  document.addEventListener("click", (ev) => {
    const button = ev.target.closest('[data-action^="cat-"]');
    if (!button || button.disabled) return;
    const action = button.dataset.action,
      value = button.dataset.value;
    if (action === "cat-source") go("/catalog/" + value);
    else if (action === "cat-category") {
      category = value;
      page = 1;
      filters();
      rows();
      refreshSidebar();
    } else if (action === "cat-page") {
      page = Number(value);
      rows();
      document
        .querySelector(".panel")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (action === "cat-jump") {
      page = Number(document.querySelector("#catalog-page").value) || 1;
      rows();
    } else if (action === "cat-reset") {
      query = category = difficulty = access = "";
      page = 1;
      render(active);
    } else if (action === "cat-retry") render(active);
  });
  return { sidebar, render };
}
