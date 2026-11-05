import { EditorView, basicSetup } from "codemirror";
import { Compartment } from "@codemirror/state";
import { cpp } from "@codemirror/lang-cpp";
import { python } from "@codemirror/lang-python";
import {
  createIcons,
  Code,
  BookOpen,
  Search,
  Plug,
  Check,
  ChevronRight,
  ChevronLeft,
  Upload,
  Download,
  ArrowLeft,
  FileCode,
  Play,
  Send,
  ExternalLink,
  Clock,
  Info,
  X,
  RefreshCw,
  CircleHelp,
  Sun,
  Moon,
  Eraser,
} from "lucide";
import {
  escapeHtml as e,
  safeUrl,
  localEndpoint,
  filterProblems,
  mergeCatalog,
  verdicts,
} from "./core.js";
import "./style.css";
import { createExternalView } from "./external-view.js";
import { restoreDraft } from "./drafts.js";
import { editorAppearance } from "./theme.js";
import "./layout.css";

const iconSet = {
  Code,
  BookOpen,
  Search,
  Plug,
  Check,
  ChevronRight,
  ChevronLeft,
  Upload,
  Download,
  ArrowLeft,
  FileCode,
  Play,
  Send,
  ExternalLink,
  Clock,
  Info,
  X,
  RefreshCw,
  CircleHelp,
  Sun,
  Moon,
  Eraser,
};
const app = document.querySelector("#app");
const modal = document.querySelector("#modal");
const DATA = import.meta.env.BASE_URL;
const read = (storage, key, fallback) => {
  try {
    const value = storage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
};
const save = (storage, key, value) => {
  try {
    storage.setItem(key, JSON.stringify(value));
  } catch {
    toast("浏览器存储空间不足，请导出代码备份");
  }
};
const state = {
  theme:
    read(localStorage, "ayaya.theme", "dark") === "light" ? "light" : "dark",
  builtin: [],
  problems: [],
  pat: [],
  sources: [],
  categories: [],
  category: "",
  query: "",
  difficulty: "",
  status: "",
  page: 1,
  progress: read(localStorage, "ayaya.progress", {}),
  connected: false,
  health: null,
  submissions: [],
  busy: false,
  endpoint: read(localStorage, "ayaya.endpoint", "http://127.0.0.1:8765"),
  token: read(sessionStorage, "ayaya.token", ""),
  language: read(localStorage, "ayaya.language", "cpp"),
  editor: null,
  currentProblem: null,
};
const languageConfig = new Compartment();
const editorThemeConfig = new Compartment();
const languages = { c: "C11", cpp: "C++17", python: "Python 3" };
const icon = (name) => `<i data-lucide="${name}" aria-hidden="true"></i>`;
const icons = () =>
  createIcons({ icons: iconSet, attrs: { "stroke-width": 1.7 } });
const route = () => location.hash.slice(1) || "/problems";
const badge = (status) => {
  const [label, style] = verdicts[status] || ["未作答", "neutral"];
  return `<span class="verdict ${style}">${e(status || "—")}<span>${e(label)}</span></span>`;
};
const solved = (list) =>
  list.filter((p) => state.progress[p.id] === "AC").length;
const categories = () => [
  ...new Set([...state.categories, ...state.problems.map((p) => p.category)]),
];
function toast(message) {
  const box = document.querySelector("#toast");
  box.textContent = message;
  box.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => box.classList.remove("show"), 3500);
}
function go(path) {
  if (route() === path) render();
  else location.hash = path;
}
function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  document.querySelector('meta[name="theme-color"]').content =
    state.theme === "dark" ? "#000000" : "#ffffff";
  const button = document.querySelector('[data-action="toggle-theme"]');
  if (button) {
    const label = state.theme === "dark" ? "切换浅色模式" : "切换纯黑模式";
    button.innerHTML = icon(state.theme === "dark" ? "sun" : "moon");
    button.setAttribute("aria-label", label);
    button.title = label;
    icons();
  }
  if (state.editor)
    state.editor.dispatch({
      effects: editorThemeConfig.reconfigure(editorAppearance(state.theme)),
    });
}
function connectionButton() {
  return `<span class="status-dot ${state.connected ? "online" : ""}"></span>${state.connected ? "判题已连接" : "连接判题"}`;
}
function sidebar() {
  const structure = [
    "链表",
    "栈",
    "队列",
    "堆",
    "树",
    "图",
    "哈希与集合",
    "并查集",
    "区间数据结构",
  ];
  const group = (title, names) =>
    `<div class="nav-label">${title}</div>${names.map((category) => `<button class="category ${state.category === category ? "selected" : ""}" data-action="category" data-value="${e(category)}"><span>${e(category)}</span><span class="count">${state.problems.filter((p) => p.category === category).length}</span></button>`).join("")}`;
  return `<div class="sidebar-heading"><strong>算法分类</strong></div>
    <button class="overview ${!state.category ? "selected" : ""}" data-action="category" data-value=""><strong>全部题目</strong><span>${state.problems.length}</span></button>
    <div class="category-scroll">${group(
      "数据结构",
      categories().filter((c) => structure.includes(c)),
    )}${group(
      "算法专题",
      categories().filter((c) => !structure.includes(c)),
    )}</div>`;
}
function shell(content, { problem = false, library = false } = {}) {
  app.innerHTML = `<header class="topbar"><a class="brand" href="#/problems"><span class="brand-symbol">A<span>›</span></span><strong>Ayaya <b>OJ</b></strong></a><nav class="topnav" aria-label="主导航"><a class="${route().startsWith("/problem") ? "active" : ""}" href="#/problems">练习</a><a class="${route().startsWith("/catalog") || route() === "/pat" ? "active" : ""}" href="#/catalog/luogu">题库索引</a><a class="${route() === "/submissions" ? "active" : ""}" href="#/submissions">提交记录</a><a class="${route() === "/import" ? "active" : ""}" href="#/import">导入</a></nav><div class="top-actions"><button class="connect-button" data-action="connect">${connectionButton()}</button><button class="icon-button theme-toggle" data-action="toggle-theme" aria-label="${state.theme === "dark" ? "切换浅色模式" : "切换纯黑模式"}" title="${state.theme === "dark" ? "切换浅色模式" : "切换纯黑模式"}">${icon(state.theme === "dark" ? "sun" : "moon")}</button><button class="icon-button" data-action="help" aria-label="使用说明" title="使用说明">${icon("circle-help")}</button></div></header>
    <div class="workspace ${problem ? "problem-workspace" : library ? "library-workspace" : "single-workspace"}">${library ? `<aside class="sidebar" id="sidebar" aria-label="算法分类">${sidebar()}</aside>` : ""}<main id="main" class="main ${problem ? "problem-main" : ""}">${content}</main></div>`;
  icons();
}
function renderLibrary() {
  shell(`<div class="page-heading"><h1>${e(state.category || "算法练习")}</h1><span class="heading-meta">${state.problems.length} 题 · 已通过 ${solved(state.problems)}</span></div>
    <section class="panel"><div class="filters"><label class="search-field">${icon("search")}<input id="search" type="search" placeholder="搜索题号、标题、算法" value="${e(state.query)}" aria-label="搜索题目"></label><select id="library-category" class="mobile-category" aria-label="筛选算法分类"><option value="">全部分类</option>${categories().map((c) => `<option value="${e(c)}" ${state.category === c ? "selected" : ""}>${e(c)}</option>`).join("")}</select><select id="difficulty" aria-label="筛选难度"><option value="">全部难度</option>${["入门", "基础", "进阶"].map((d) => `<option ${state.difficulty === d ? "selected" : ""}>${d}</option>`).join("")}</select><select id="status" aria-label="筛选作答状态">${[
      ["", "全部状态"],
      ["untried", "未作答"],
      ["tried", "已尝试"],
      ["AC", "已通过"],
    ]
      .map(
        ([v, l]) =>
          `<option value="${v}" ${state.status === v ? "selected" : ""}>${l}</option>`,
      )
      .join(
        "",
      )}</select><button class="text-button" data-action="reset" aria-label="清除所有筛选">重置</button></div><div id="table-results"></div></section><details class="quiet-details"><summary>关于本地题库</summary><p>这些练习使用原创题面与自建测试。洛谷、AcWing、PAT 等原站题目见<a href="#/catalog/luogu">题库索引</a>；连接本地判题后即可提交代码。</p></details>`, { library: true });
  renderTable();
  document.querySelector("#library-category").addEventListener("change", (ev) => {
    state.category = ev.target.value;
    state.page = 1;
    renderLibrary();
  });
  document.querySelector("#search").addEventListener("input", (ev) => {
    state.query = ev.target.value;
    state.page = 1;
    renderTable();
  });
  for (const key of ["difficulty", "status"])
    document.querySelector("#" + key).addEventListener("change", (ev) => {
      state[key] = ev.target.value;
      state.page = 1;
      renderTable();
    });
}
function renderTable() {
  const filtered = filterProblems(state.problems, {
    ...state,
    progress: state.progress,
  });
  const size = 15,
    pages = Math.max(1, Math.ceil(filtered.length / size));
  state.page = Math.min(state.page, pages);
  const list = filtered.slice((state.page - 1) * size, state.page * size);
  document.querySelector("#table-results").innerHTML =
    `<div class="table-scroll"><table class="problem-table library-table"><thead><tr><th class="status-column">状态</th><th>题号</th><th class="title-column">题目</th><th class="category-column">分类</th><th>难度</th></tr></thead><tbody>${
      list.length
        ? list
            .map(
              (p) =>
                `<tr><td class="status-column">${state.progress[p.id] === "AC" ? `<span class="status-check" title="已通过" aria-label="已通过">${icon("check")}</span>` : state.progress[p.id] ? `<span class="status-attempt" title="已尝试" aria-label="已尝试">·</span>` : '<span class="status-empty" aria-label="未作答">—</span>'}</td><td class="problem-id">${e(p.id.replace("OJ-", ""))}</td><td><a class="problem-title" href="#/problem/${encodeURIComponent(p.id)}" title="${e(p.tags.join(" · "))}">${e(p.title)}</a></td><td class="category-column"><button class="plain-category" data-action="category" data-value="${e(p.category)}">${e(p.category)}</button></td><td><span class="difficulty ${p.difficulty === "入门" ? "easy" : p.difficulty === "进阶" ? "hard" : ""}">${e(p.difficulty)}</span></td></tr>`,
            )
            .join("")
        : '<tr><td colspan="5"><div class="empty">没有找到题目<button class="text-button" data-action="reset">清除筛选</button></div></td></tr>'
    }</tbody></table></div><div class="pagination"><span>${filtered.length} 题</span><div><button class="page-arrow" data-action="page" data-value="${state.page - 1}" ${state.page === 1 ? "disabled" : ""} aria-label="上一页">${icon("chevron-left")}</button>${Array.from({ length: pages }, (_, i) => `<button class="page-number ${state.page === i + 1 ? "selected" : ""}" data-action="page" data-value="${i + 1}" aria-label="第 ${i + 1} 页" ${state.page === i + 1 ? 'aria-current="page"' : ""}>${i + 1}</button>`).join("")}<button class="page-arrow" data-action="page" data-value="${state.page + 1}" ${state.page === pages ? "disabled" : ""} aria-label="下一页">${icon("chevron-right")}</button></div></div>`;
  icons();
}
function renderProblem(identity) {
  const p = state.problems.find((p) => p.id === identity);
  if (!p) {
    shell(
      '<div class="empty">题目不存在，或需要先连接包含该题的本地题库。<a class="button primary" href="#/problems">返回题库</a></div>',
    );
    return;
  }
  state.currentProblem = p;
  shell(
    `<div class="problem-toolbar"><a href="#/problems">${icon("arrow-left")} 题目列表</a><button class="text-button" data-action="problem-history">${icon("clock")} 本题提交</button></div><div class="problem-split"><article class="statement-pane"><div class="statement-title"><span class="problem-id">${e(p.id)}</span><h1>${e(p.title)}</h1><div class="problem-meta"><span class="difficulty ${p.difficulty === "进阶" ? "hard" : p.difficulty === "入门" ? "easy" : ""}">${p.difficulty}</span><span>${e(p.category)}</span><span>${p.time_limit_ms} ms</span></div></div><section class="statement-block"><h2>题目描述</h2><p>${e(p.statement)}</p></section><section class="statement-block"><h2>输入格式</h2><p>${e(p.input_format)}</p></section><section class="statement-block"><h2>输出格式</h2><p>${e(p.output_format)}</p></section><section class="statement-block"><h2>数据范围</h2><p>${e(p.constraints)}</p></section>${p.samples.map((s, i) => `<section class="statement-block sample-block"><h2>输入样例 ${i + 1}<button class="copy-button" data-action="copy-sample" data-value="${i}">复制</button></h2><pre>${e(s.input) || "（空输入）"}</pre><h2>输出样例 ${i + 1}</h2><pre>${e(s.output) || "（空输出）"}</pre></section>`).join("")}<details class="problem-provenance quiet-details"><summary>来源与评测说明</summary><strong>${e(p.source)}</strong><p>${e(p.provenance)}</p>${safeUrl(p.source_url) ? `<a href="${e(safeUrl(p.source_url))}" target="_blank" rel="noopener noreferrer">来源链接 ${icon("external-link")}</a>` : ""}<p>标签：${e(p.tags.join("、"))} · 满分 ${p.score}。每个测试点限时 ${p.time_limit_ms} ms。本机耗时仅供参考，macOS 不作严格内存判定。代码以你的本机权限运行，仅运行自己信任的程序。</p></details></article><section class="editor-pane" aria-label="代码编辑与评测"><div class="editor-toolbar"><label>${icon("code")}<select id="language" aria-label="编程语言">${Object.entries(
      languages,
    )
      .map(
        ([v, l]) =>
          `<option value="${v}" ${state.language === v ? "selected" : ""}>${l}</option>`,
      )
      .join(
        "",
      )}</select></label><div><button class="icon-button" data-action="upload-code" aria-label="上传源码" title="上传源码">${icon("upload")}</button><button class="icon-button" data-action="download-code" aria-label="下载源码" title="下载源码">${icon("download")}</button><button class="icon-button" data-action="clear-code" aria-label="清空代码" title="清空代码">${icon("eraser")}</button></div></div><div id="editor" aria-label="源代码编辑器"></div><div class="editor-status"><span id="draft-status">自动保存</span><span id="language-hint"></span></div><details class="custom-input"><summary>自定义输入</summary><textarea id="stdin" aria-label="自定义测试输入" placeholder="在这里输入测试数据"></textarea><button class="button secondary" data-action="run-custom">${icon("play")} 运行自定义输入</button></details><div class="submission-actions"><button class="button secondary" data-action="run-sample">${icon("play")} 运行样例</button><button class="button primary" data-action="judge">${icon("send")} 提交评测</button></div><div id="result" class="result-panel" aria-live="polite"></div></section></div>`,
    { problem: true },
  );
  const draft = restoreDraft(
    read(localStorage, `ayaya.draft.${p.id}.${state.language}`, ""),
  );
  state.editor = new EditorView({
    doc: draft,
    extensions: [
      basicSetup,
      languageConfig.of(state.language === "python" ? python() : cpp()),
      EditorView.lineWrapping,
      EditorView.updateListener.of((update) => {
        if (update.docChanged)
          save(
            localStorage,
            `ayaya.draft.${p.id}.${state.language}`,
            update.state.doc.toString(),
          );
      }),
      editorThemeConfig.of(editorAppearance(state.theme)),
    ],
    parent: document.querySelector("#editor"),
  });
  document
    .querySelector("#language")
    .addEventListener("change", (ev) => changeLanguage(ev.target.value));
  languageHint();
  icons();
}
function languageHint() {
  const hint = document.querySelector("#language-hint");
  if (hint)
    hint.textContent =
      state.language === "cpp"
        ? "C++17 · Apple Clang"
        : "本地 " + languages[state.language];
}
function changeLanguage(value) {
  state.language = value;
  save(localStorage, "ayaya.language", value);
  const content = restoreDraft(
    read(localStorage, `ayaya.draft.${state.currentProblem.id}.${value}`, ""),
  );
  state.editor.dispatch({
    effects: languageConfig.reconfigure(value === "python" ? python() : cpp()),
    changes: { from: 0, to: state.editor.state.doc.length, insert: content },
  });
  document.querySelector("#language").value = value;
  languageHint();
}
function displayResult(submission) {
  const box = document.querySelector("#result");
  if (!box) return;
  const r = submission.result;
  if (!r) {
    box.innerHTML = `<div class="pending"><span class="spinner"></span>${badge(submission.status)}<p>本地服务正在处理本次提交…</p></div>`;
    return;
  }
  box.innerHTML = `<div class="result-heading">${badge(submission.status)}<span>${submission.mode === "judge" && r.score != null ? `${r.score} / ${state.problems.find((p) => p.id === submission.problem_id)?.score ?? "—"} 分` : "不计入通过记录"}</span><span>${r.time_ms != null ? `${r.time_ms} ms` : "—"}</span></div><p class="result-message">${e(r.message || "")}${r.total ? ` · 通过 ${r.passed} / ${r.total} 个测试点` : ""}</p>${!r.cases?.length && r.message ? `<pre class="compiler-output">${e(r.message)}</pre>` : ""}<div class="case-grid">${(r.cases || []).map((c) => `<a href="#case-${c.index}" class="case ${c.verdict === "AC" || c.verdict === "OK" ? "success" : "danger"}" data-action="case" data-value="${c.index}"><small>测试点 ${c.index}</small><strong>${e(c.verdict)}</strong><span>${c.time_ms} ms</span></a>`).join("")}</div>${(r.cases || []).map((c) => `<details class="case-detail" id="case-${c.index}"><summary>测试点 ${c.index} · ${(verdicts[c.verdict] || ["运行完成"])[0]} · 查看详情</summary>${c.input != null ? `<h4>输入</h4><pre>${e(c.input) || "（空）"}</pre><h4>预期输出</h4><pre>${e(c.expected) || "（空）"}</pre>` : ""}<h4>实际输出</h4><pre>${e(c.stdout) || "（空）"}</pre>${c.stderr ? `<h4>错误信息</h4><pre>${e(c.stderr)}</pre>` : ""}</details>`).join("")}`;
}
async function submit(mode) {
  if (!state.connected) {
    openConnection();
    return;
  }
  if (state.busy) {
    toast("上一份代码仍在评测，请稍候");
    return;
  }
  const p = state.currentProblem,
    code = state.editor.state.doc.toString();
  if (!code.trim()) {
    toast("请先输入代码");
    return;
  }
  state.busy = true;
  setBusy(true);
  try {
    const sent = await api("/api/submissions", {
      method: "POST",
      body: {
        problem_id: p.id,
        language: state.language,
        code,
        mode,
        stdin: document.querySelector("#stdin").value,
      },
    });
    let submission = { ...sent, problem_id: p.id, mode };
    displayResult(submission);
    do {
      await new Promise((resolve) => setTimeout(resolve, 400));
      submission = await api("/api/submissions/" + sent.id);
      if (state.currentProblem?.id === p.id) displayResult(submission);
    } while (["QUEUED", "RUNNING"].includes(submission.status));
    await syncHistory();
    if (document.querySelector("#sidebar")) {
      document.querySelector("#sidebar").innerHTML = sidebar();
      icons();
    }
    toast(
      mode === "judge"
        ? `${p.id}：${(verdicts[submission.status] || [submission.status])[0]}`
        : "运行已完成",
    );
  } catch (error) {
    toast(error.message);
    const box = document.querySelector("#result");
    if (box) box.innerHTML = `<div class="empty">${e(error.message)}</div>`;
  } finally {
    state.busy = false;
    setBusy(false);
  }
}
function setBusy(value) {
  document
    .querySelectorAll(
      '[data-action="judge"],[data-action="run-sample"],[data-action="run-custom"]',
    )
    .forEach((b) => {
      b.disabled = value;
    });
}
function connectionLost() {
  state.connected = false;
  const button = document.querySelector(".connect-button");
  if (button) button.innerHTML = connectionButton();
}
async function api(
  path,
  { method = "GET", body, endpoint = state.endpoint, token = state.token } = {},
) {
  const headers = {};
  if (token && path !== "/api/health")
    headers.Authorization = "Bearer " + token;
  if (body) headers["Content-Type"] = "application/json";
  let response;
  try {
    response = await fetch(endpoint + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(12000),
      targetAddressSpace: "loopback",
    });
  } catch {
    connectionLost();
    throw Error(
      "无法连接本地服务。请检查服务是否启动，并允许浏览器访问本地网络；Safari 可改用本地网页。",
    );
  }
  const data = await response.json();
  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail
              .map((x) => `${x.loc.slice(1).join(".")}：${x.msg}`)
              .join("；")
          : "请求失败";
    if (response.status === 401) connectionLost();
    throw Error(message);
  }
  return data;
}
async function syncHistory() {
  const data = await api("/api/submissions");
  state.submissions = data.submissions;
  state.progress = data.progress;
  save(localStorage, "ayaya.progress", state.progress);
}
function openConnection() {
  modal.innerHTML = `<form id="connect-form"><div class="modal-heading"><div class="modal-icon">${icon("plug")}</div><h2>连接本地判题</h2><button type="button" class="icon-button close-modal" data-action="close-modal" aria-label="关闭">${icon("x")}</button></div><p class="modal-description">启动本地判题后，粘贴连接 token。</p><label class="form-label">本地服务地址<input name="endpoint" type="url" value="${e(state.endpoint)}" required spellcheck="false"></label><label class="form-label">连接 token<input name="token" type="password" value="${e(state.token)}" placeholder="从本地服务窗口复制" required autocomplete="off" spellcheck="false"></label><details class="connection-guide"><summary>首次连接说明</summary><ol><li>双击项目中的“启动本地判题.command”。</li><li>复制终端窗口里的连接 token。</li><li>使用 GitHub Pages 时，按 README 添加网站域名；浏览器提示本地访问时选择允许。</li></ol><p>代码以本机权限运行，仅运行自己信任的程序。</p></details><p id="connect-error" class="form-error" role="alert"></p><div class="modal-actions"><a class="text-button" href="http://127.0.0.1:8765/" target="_blank" rel="noopener noreferrer">打开本地网页 ${icon("external-link")}</a><button class="button primary" type="submit">连接服务</button></div><p class="small-note">token 仅在当前浏览器会话中保存。</p></form>`;
  modal.showModal();
  icons();
  document
    .querySelector("#connect-form")
    .addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const button = ev.currentTarget.querySelector("[type=submit]");
      button.disabled = true;
      button.textContent = "连接中…";
      try {
        const form = new FormData(ev.currentTarget),
          endpoint = localEndpoint(form.get("endpoint").trim()),
          token = form.get("token").trim();
        const health = await api("/api/health", { endpoint, token: "" });
        if (health.service !== "ayaya-oj")
          throw Error("地址对应的不是 Ayaya OJ 判题服务");
        const data = await api("/api/problems", { endpoint, token });
        state.endpoint = endpoint;
        state.token = token;
        state.health = health;
        state.connected = true;
        state.problems = mergeCatalog(state.builtin, data.problems);
        save(localStorage, "ayaya.endpoint", endpoint);
        save(sessionStorage, "ayaya.token", token);
        await syncHistory();
        modal.close();
        render();
        toast("本地判题已连接");
      } catch (error) {
        document.querySelector("#connect-error").textContent = error.message;
        state.connected = false;
      } finally {
        button.disabled = false;
        button.textContent = "连接服务";
      }
    });
}
function renderHistory() {
  shell(
    `<div class="page-heading"><h1>提交记录</h1><button class="button secondary" data-action="refresh-history">${icon("refresh-cw")} 刷新</button></div>${!state.connected ? `<section class="panel empty"><p>连接本地判题，查看提交记录。</p><button class="button primary" data-action="connect">连接判题</button></section>` : `<section class="panel table-scroll"><table class="problem-table"><thead><tr><th>提交时间</th><th>题目</th><th>语言</th><th>类型</th><th>结果</th><th>得分</th><th></th></tr></thead><tbody>${state.submissions.map((s) => `<tr><td class="timestamp">${new Date(s.created_at).toLocaleString("zh-CN", { hour12: false })}</td><td><a class="problem-title" href="#/problem/${encodeURIComponent(s.problem_id)}">${e(s.title)}</a><div class="tagline">${e(s.problem_id)}</div></td><td>${languages[s.language]}</td><td>${{ judge: "正式提交", sample: "样例运行", custom: "自定义运行" }[s.mode]}</td><td>${badge(s.status)}</td><td>${s.result?.score ?? "—"}</td><td><button class="text-button" data-action="submission-detail" data-value="${e(s.id)}">详情</button></td></tr>`).join("") || '<tr><td colspan="7" class="empty">还没有提交，挑选一道题开始练习。</td></tr>'}</tbody></table><div class="pagination"><span>最近 ${state.submissions.length} 条提交</span><span>仅“正式提交”的 AC 计入通过状态</span></div></section>`}`,
  );
}
function renderImport() {
  shell(
    `<div class="page-heading"><h1>导入题目</h1><a class="button secondary" href="${DATA}import-example.json" download="import-example.json">${icon("download")} 下载 JSON 模板</a></div><div class="import-layout"><section class="panel import-panel"><label class="upload-area">${icon("file-code")}<strong>选择 JSON 文件</strong><span>单题 · 最大 2 MB</span><input id="import-file" type="file" accept=".json,application/json"></label><textarea id="import-json" spellcheck="false" aria-label="题目 JSON" placeholder='{"schema_version": 1, "id": "CUSTOM-1001", ...}'></textarea><div class="import-actions"><span id="import-filename">尚未选择文件</span><button class="button primary" data-action="import">${icon("upload")} 导入题目</button></div><p id="import-error" class="form-error" role="alert"></p></section><details class="quiet-details import-info"><summary>题目格式与导入说明</summary><ol><li><strong>题号与分类</strong><p>题号不能重复。按链表、堆、树、图等知识点分类，也可创建新分类。</p></li><li><strong>题面与输入输出</strong><p>使用纯文本题面，写清数据范围与输出要求。</p></li><li><strong>样例与测试点</strong><p>samples 用于页面展示，tests 用于正式评测。比较方式可选 tokens 或 exact。</p></li><li><strong>来源信息</strong><p>记录学校、课程、年份或官方链接，以及题面和测试数据的来源。</p></li></ol><div class="notice compact">${icon("info")}<p>导入内容仅保存在本地服务，不会自动上传到 GitHub。</p></div></details></div>`,
  );
  document
    .querySelector("#import-file")
    .addEventListener("change", async (ev) => {
      const file = ev.target.files[0];
      if (!file) return;
      if (file.size > 2000000) {
        toast("文件不能超过 2 MB");
        return;
      }
      document.querySelector("#import-json").value = await file.text();
      document.querySelector("#import-filename").textContent = file.name;
    });
}
function showHelp() {
  modal.innerHTML = `<div class="modal-heading"><h2>开始一次练习</h2><button class="icon-button close-modal" data-action="close-modal" aria-label="关闭">${icon("x")}</button></div><div class="help-content"><h3>1. 启动本地判题</h3><p>双击“启动本地判题.command”，保持窗口打开，复制连接 token。</p><h3>2. 连接网页</h3><p>点击右上角“连接判题”。GitHub Pages 首次使用需要允许浏览器访问 localhost；具体配置见项目 README。</p><h3>3. 选题与提交</h3><p>从左侧按算法分类选题，选择 C11、C++17 或 Python 3，输入完整程序，先运行样例再提交评测。</p><h3>关于浏览器</h3><p>Chrome / Edge 优先使用 Pages 网页直接连接；Safari 若连接受限，可打开本地服务提供的同一套网页。</p><h3>关于本地评测</h3><p>判题使用本机编译器与自建测试点。Apple Clang 的 C++ 环境不包含 bits/stdc++.h，请使用标准头文件。本地执行器不适合运行陌生人的代码。</p></div>`;
  modal.showModal();
  icons();
}
function render() {
  if (state.editor) {
    state.editor.destroy();
    state.editor = null;
  }
  state.currentProblem = null;
  document.title =
    "Ayaya OJ · " +
    (route().startsWith("/catalog")
      ? "多平台题库索引"
      : route() === "/pat"
        ? "PAT 官方索引"
        : route() === "/submissions"
          ? "提交记录"
          : route() === "/import"
            ? "导入题目"
            : "算法练习");
  if (route().startsWith("/problem/"))
    renderProblem(decodeURIComponent(route().slice(9)));
  else if (route().startsWith("/catalog"))
    externalView.render(route().split("/")[2] || "luogu");
  else if (route() === "/pat") go("/catalog/pat");
  else if (route() === "/submissions") renderHistory();
  else if (route() === "/import") renderImport();
  else renderLibrary();
  setBusy(state.busy);
}
function download(content, name, type = "text/plain") {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
document.addEventListener("click", async (ev) => {
  const button = ev.target.closest("[data-action]");
  if (!button || button.disabled) return;
  const action = button.dataset.action,
    value = button.dataset.value;
  if (action === "category") {
    state.category = value;
    state.nextCategory = value;
    state.page = 1;
    state.query = "";
    state.difficulty = "";
    state.status = "";
    go("/problems");
  } else if (action === "page") {
    state.page = Number(value);
    renderTable();
    document
      .querySelector(".panel")
      .scrollIntoView({ block: "start", behavior: "smooth" });
  } else if (action === "reset") {
    state.category = "";
    state.query = "";
    state.difficulty = "";
    state.status = "";
    state.page = 1;
    renderLibrary();
  } else if (action === "library") go("/problems");
  else if (action === "connect") openConnection();
  else if (action === "close-modal") modal.close();
  else if (action === "toggle-theme") {
    state.theme = state.theme === "dark" ? "light" : "dark";
    save(localStorage, "ayaya.theme", state.theme);
    applyTheme();
  } else if (action === "help") showHelp();
  else if (action === "copy-sample") {
    try {
      await navigator.clipboard.writeText(
        state.currentProblem.samples[Number(value)].input,
      );
      toast("样例已复制");
    } catch {
      toast("请手动选择样例复制");
    }
  } else if (action === "run-sample") submit("sample");
  else if (action === "judge") submit("judge");
  else if (action === "run-custom") submit("custom");
  else if (action === "case") {
    ev.preventDefault();
    const detail = document.querySelector("#case-" + value);
    if (detail) {
      detail.open = !detail.open;
      detail.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  } else if (action === "upload-code") {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".c,.cpp,.cc,.cxx,.py,.txt";
    input.onchange = async () => {
      const file = input.files[0];
      if (!file) return;
      if (file.size > 100000) {
        toast("源码文件最多 100 KB");
        return;
      }
      const extension = file.name.split(".").pop().toLowerCase();
      const lang =
        extension === "py"
          ? "python"
          : extension === "c"
            ? "c"
            : ["cpp", "cc", "cxx"].includes(extension)
              ? "cpp"
              : state.language;
      if (lang !== state.language) changeLanguage(lang);
      state.editor.dispatch({
        changes: {
          from: 0,
          to: state.editor.state.doc.length,
          insert: await file.text(),
        },
      });
      toast("源码已载入");
    };
    input.click();
  } else if (action === "download-code")
    download(
      state.editor.state.doc.toString(),
      state.currentProblem.id +
        "." +
        { c: "c", cpp: "cpp", python: "py" }[state.language],
    );
  else if (action === "clear-code") {
    if (
      state.editor.state.doc.length &&
      confirm("清空当前代码？本题当前语言的草稿也会被清空。")
    )
      state.editor.dispatch({
        changes: {
          from: 0,
          to: state.editor.state.doc.length,
          insert: "",
        },
      });
  } else if (action === "refresh-history") {
    if (!state.connected) {
      openConnection();
      return;
    }
    try {
      await syncHistory();
      renderHistory();
      toast("记录已更新");
    } catch (err) {
      toast(err.message);
    }
  } else if (action === "problem-history") {
    if (!state.connected) {
      openConnection();
      return;
    }
    try {
      await syncHistory();
      const list = state.submissions.filter(
        (s) => s.problem_id === state.currentProblem.id,
      );
      modal.innerHTML = `<div class="modal-heading"><h2>本题最近提交</h2><button class="icon-button close-modal" data-action="close-modal" aria-label="关闭">${icon("x")}</button></div><div class="history-list">${list.map((s) => `<button data-action="submission-detail" data-value="${s.id}"><span>${new Date(s.created_at).toLocaleString("zh-CN")}</span>${badge(s.status)}<span>${languages[s.language]}</span></button>`).join("") || "<p>还没有本题的提交记录。</p>"}</div>`;
      modal.showModal();
      icons();
    } catch (err) {
      toast(err.message);
    }
  } else if (action === "submission-detail") {
    try {
      const s = await api("/api/submissions/" + value);
      modal.innerHTML = `<div class="modal-heading"><h2>${e(s.problem_id)} · 提交详情</h2><button class="icon-button close-modal" data-action="close-modal" aria-label="关闭">${icon("x")}</button></div><div class="submission-detail">${badge(s.status)}<p>${e(s.result?.message || "")} · ${languages[s.language]} · ${s.result?.time_ms ?? "—"} ms</p>${s.result?.cases ? `<p>测试点：${s.result.cases.map((c) => `${c.index}: ${c.verdict}`).join(" / ")}</p>` : ""}<h3>提交源码</h3><pre>${e(s.code)}</pre></div>`;
      if (!modal.open) modal.showModal();
      icons();
    } catch (err) {
      toast(err.message);
    }
  } else if (action === "import") {
    if (!state.connected) {
      openConnection();
      return;
    }
    const text = document.querySelector("#import-json").value;
    try {
      if (new TextEncoder().encode(text).length > 2000000)
        throw Error("题目文件超过 2 MB");
      const data = JSON.parse(text);
      const p = await api("/api/import", { method: "POST", body: data });
      state.problems = mergeCatalog(state.problems, [p]);
      toast(`已导入 ${p.id}`);
      state.category = p.category;
      go("/problem/" + p.id);
    } catch (error) {
      document.querySelector("#import-error").textContent = error.message;
    }
  }
});
window.addEventListener("hashchange", () => {
  state.page = 1;
  state.query = "";
  state.category = route() === "/problems" ? (state.nextCategory ?? "") : "";
  delete state.nextCategory;
  state.difficulty = "";
  state.status = "";
  render();
  window.scrollTo(0, 0);
});
modal.addEventListener("click", (ev) => {
  if (ev.target === modal) {
    const r = modal.getBoundingClientRect();
    if (
      ev.clientX < r.left ||
      ev.clientX > r.right ||
      ev.clientY < r.top ||
      ev.clientY > r.bottom
    )
      modal.close();
  }
});
async function start() {
  try {
    const [catalog, pat, sources] = await Promise.all([
      fetch(DATA + "data/catalog.json").then((r) => {
        if (!r.ok) throw Error("题库读取失败");
        return r.json();
      }),
      fetch(DATA + "data/pat.json").then((r) => {
        if (!r.ok) throw Error("PAT 索引读取失败");
        return r.json();
      }),
      fetch(DATA + "data/sources/index.json").then((r) => {
        if (!r.ok) throw Error("多平台目录读取失败");
        return r.json();
      }),
    ]);
    state.sources = sources.sources;
    state.builtin = catalog.problems;
    state.problems = catalog.problems;
    state.categories = catalog.categories;
    state.pat = pat.problems;
    if (
      ["localhost", "127.0.0.1"].includes(location.hostname) &&
      !["5173", "4173"].includes(location.port)
    )
      state.endpoint = location.origin;
    render();
  } catch (error) {
    app.innerHTML = `<div class="startup-error"><h1>题库暂时无法加载</h1><p>${e(error.message)}</p><button onclick="location.reload()">重新加载</button></div>`;
  }
}
const externalView = createExternalView({
  state,
  DATA,
  icon,
  e,
  safeUrl,
  icons,
  shell,
  go,
});
applyTheme();
start();
