# Ayaya OJ

一个 PTA 风格的个人算法练习平台。GitHub Pages 托管前端，自己的 Mac 负责 C、C++、Python 本地判题，不需要 VPS。

- 网站：<https://ayaya114514.github.io/AyayaAlgorithm/>
- 51 道可本地判题的原创经典练习，17 个算法分类、250 个自建测试点。
- PAT 官方索引：乙级 125 题、甲级 179 题（2026-11-04 快照）。仅包含题号、标题、分数、官方链接；216 条有本站分类提示，其余保留待分类。
- 分类筛选、题号导航、难度/状态筛选、CodeMirror 编辑器、草稿自动保存、源码上传和下载。
- 样例运行、自定义输入、正式评测、分测试点结果、部分得分和 SQLite 提交历史。
- JSON 题目导入，预留 `schema_version`；第一版只实现完整程序的编程题。

## 日常使用

本机环境已按 Python 3.10 的 `ai_env` 配置依赖。进入本项目目录，双击 **启动本地判题.command**。

1. 保持终端窗口打开，复制其中的连接 token。
2. 打开 GitHub Pages 网站，点击右上角 **连接本地判题**。
3. 地址使用 `http://127.0.0.1:8765`，粘贴 token。
4. 浏览器请求本地网络访问权限时选择允许，然后选题、编辑、提交。

只有 `judge` 正式提交的 AC 计入通过状态，样例和自定义运行不会误标为已通过。已有 AC 后再提交 WA，不会清除通过状态。

### Safari 备用方式

若 Safari 阻止 HTTPS 网页连接本机 HTTP 服务，先运行 `npm run build`，再启动本地服务，打开：

<http://127.0.0.1:8765/>

这里是同一套前端、题库和编辑器，与判题 API 同源。仍然需要连接 token。GitHub Pages 题目浏览不依赖本地服务。

### 第一次在另一台电脑安装

```sh
conda activate ai_env
mamba install -c conda-forge fastapi uvicorn
npm ci
npm run build
python scripts/start.py --origin https://ayaya114514.github.io
```

没有 mamba 时可使用 conda；还可使用 `python -m pip install -r requirements.txt`。C/C++ 编译器使用 Xcode Command Line Tools 的 `clang` / `clang++`。

`--origin` 会保存到 `.local/settings.json`。Origin 只包含协议和域名，**不包含** `/AyayaAlgorithm/` 仓库路径。更换 Pages 域名时重新运行该命令即可。默认端口 8765，可用 `--port` 修改。

## 题库

分类包括：入门与模拟、数组与双指针、链表、栈、队列、堆、树、图、排序与查找、哈希与集合、字符串、动态规划、贪心、搜索与回溯、并查集、数学与数论、区间数据结构。

内置经典题为原创题面和自建测试数据，并非 PAT 原题或官方判题数据。PAT 列表从[官方公开目录](https://pintia.cn/problem-sets/dashboard)整理，点击后跳转 PTA。分类是本站学习提示，不是官方标签。没有声称已收录全部经典题或大学试卷；这是可以继续补充的第一批题库。

### 导入题目

在网站中打开 **导入题目**，下载模板，填写后上传单个 JSON 文件。导入需要已连接本地服务。

```json
{
  "schema_version": 1,
  "id": "CUSTOM-1001",
  "title": "整数求和",
  "category": "入门与模拟",
  "tags": ["输入输出"],
  "difficulty": "入门",
  "score": 15,
  "statement": "给定两个整数，计算它们的和。",
  "input_format": "一行两个整数 a b。",
  "output_format": "输出 a+b。",
  "constraints": "整数之和在 64 位有符号范围内。",
  "samples": [{"input": "3 5\n", "output": "8\n"}],
  "tests": [
    {"input": "3 5\n", "output": "8\n"},
    {"input": "-7 3\n", "output": "-4\n"}
  ],
  "time_limit_ms": 2000,
  "memory_limit_mb": 256,
  "comparator": "tokens",
  "source": "个人练习",
  "source_url": "",
  "provenance": "自编题面与测试数据"
}
```

- 题号只能包含字母、数字、`-`、`_`，不能与现有题号重复。
- `tokens` 忽略空白差异；`exact` 保留空格，仅统一换行并忽略末尾换行。
- 单题文件最多 2 MB，1–100 个测试点；每个输入/输出最多 262144 字符，总测试数据最多 1.5 MB。
- 题面与字段按纯文本展示，不执行 HTML。
- 导入内容只保存在本机 `.local/problems/`，不会自动更新 GitHub Pages。其他浏览器/设备连接同一个本地服务后可以读取它们。
- 有权限使用的课程/考试资料可按“学校 / 课程 / 年份”填写 source，真实题号或链接填入 source_url；没有资料时保留来源说明，避免误称为官方原题。

内置题库维护源为 `scripts/generate_bank.py`，包含手工指定的样例答案和自建用例。修改后执行：

```sh
conda activate ai_env
python scripts/generate_bank.py
npm run build
```

生成器会核对所有样例的手工答案；`bank/references/` 为测试参考程序，不进入网站构建产物，但会随公开源码发布。初版测试集侧重基本正确性和边界，不保证排除全部错误算法或验证所有复杂度上界。

## 本地执行的边界

这是运行**自己信任代码**的个人工具，不是面向陌生提交者的多用户代码沙箱。

- 服务仅绑定 `127.0.0.1`；所有题库、提交、导入 API 都需要 Bearer token。
- 校验 Host 和 Origin，CORS 使用明确域名白名单；CORS 不是独立的鉴权手段。
- token 位于 `.local/token`，创建权限为 0600，网页只在当前 sessionStorage 会话保存 token。
- 提交串行执行，队列最多 12 个任务。源码、输入、输出、运行时间和编译时间有上限；超时会终止进程组，输出使用受限文件收集。
- 提交进程去除服务环境变量，但仍有本机文件和网络访问能力。不要用于运行网上下载的未知程序。
- macOS 显示的是包含进程启动开销的 wall time，不是标准竞赛机 CPU 时间；不提供严格内存判定。Linux 可设置地址空间上限，但当前没有独立 MLE 结论。
- C++ 使用 C++17 与 Apple Clang 标准库，**不包含 `bits/stdc++.h`**。改用 `iostream`、`vector`、`algorithm` 等标准头文件。
- 打开网页的设备与运行服务的设备需要一致。手机上的 localhost 指向手机，不会自动连接 Mac。

本地数据在 `.local/`，包含 token、导入题目、SQLite 记录；整个目录已加入 `.gitignore`。网站仅发布 `dist/`，不发布本地服务、测试参考答案或本地记录。

## 开发与验证

```sh
npm ci
npm run dev
```

前端开发预览：<http://127.0.0.1:5173/>。另开终端启动 `python scripts/start.py`。

```sh
conda activate ai_env
mamba install -c conda-forge httpx pytest
python -m pytest -q
npm test
npm run build
```

后端测试实际编译 C、C++，运行全部 51 个 Python 参考程序，检查 AC / WA / CE / RE / TLE / OLE、请求鉴权、来源限制、导入校验、记录持久化、样例不计通过、已有 AC 不被 WA 覆盖。前端测试覆盖筛选、来源链接、HTML 转义和 loopback 地址限制。

## GitHub Pages 部署

`.github/workflows/pages.yml` 在 push 到 `main` 时运行前端检查与构建，再把 `dist/` 发布到 GitHub Pages。仓库 Pages 设置使用 **GitHub Actions**。

使用相对资源路径及 hash 路由，可部署到 `/AyayaAlgorithm/` 子路径。网站中不包含 API token，不使用付费判题服务。

浏览器本地访问规则参考：[Chrome Local Network Access](https://developer.chrome.com/docs/modern-web-guidance/guides/security/local-network-access)、[MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)。
