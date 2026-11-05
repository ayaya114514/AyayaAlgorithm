# Ayaya OJ

一个 PTA 风格的个人算法练习平台。GitHub Pages 托管前端，自己的 Mac 负责 C、C++、Python 本地判题，不需要 VPS。

- 网站：<https://ayaya114514.github.io/AyayaAlgorithm/>
- 101 道可本地判题的原创经典练习，17 个算法分类、492 个自建测试点。
- 多平台索引：51,258 条公开元数据，支持平台、算法、原站难度、会员标记筛选和题号/标题搜索，按平台加载。
- PAT 官方索引：乙级 125 题、甲级 179 题（2026-11-04 快照）。仅包含题号、标题、分数、官方链接；216 条有本站分类提示，其余保留待分类。
- 单层导航、分类/难度/状态筛选、CodeMirror 编辑器、草稿自动保存、源码上传和下载。来源与操作说明按需展开，窄屏通过分类下拉选题。
- 默认纯黑背景 dark mode，可在右上角切换浅色；选择保存在当前浏览器中，编辑器与页面同步切换。
- C、C++、Python 编辑器初始均为空白，不预填任何头文件、main 或注释。保留自己写的草稿；仅迁移旧版未改动的自动模板。“清空代码”可重新从零开始。
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

内置经典题为原创题面和自建测试数据，并非原平台题面或官方判题数据。索引题目在原站作答；“同类本地练习”按算法关联，不保证输入格式与原题相同，也不代表官方评测通过。

### 多平台收录范围

以下为 2026-11-04 公开目录快照，按来源计数，跨平台同题不做全局去重。

| 来源 | 条目数 | 范围与来源 |
| --- | ---: | --- |
| 洛谷 | 17,889 | 官方主站 type=luogu 的全部 358 页；不重复抓取远程 OJ 镜像列表 |
| AcWing | 7,203 | 官方公开题库全部 145 页，保留显示题号与真实 content URL 的对应关系 |
| Codeforces | 11,488 | 官方 problemset API 全部返回记录，不含 Gym |
| AtCoder | 9,885 | AtCoder Problems 社区维护数据集全部条目；作答链接指向 AtCoder 官方站 |
| LeetCode | 4,489 | 中国站匿名公开目录，包括 789 条已公开标题的会员题；会员题面和答案不收录 |
| PAT | 304 | 乙级 125、甲级 179；保留原索引 |

每个平台的完整性仅针对上述明确范围，不代表所有历史比赛、私有题库或已删除题目。元数据包含题号、标题、原站链接、已公开标签和难度；不包含题面、答案或测试数据。题库索引无需启动本地服务。

洛谷、AcWing、Codeforces 的公开算法标签映射到本站分类；未公开完整标签的 AtCoder、LeetCode 条目仅在题名有明确提示时分类，其余保留待分类。PAT 分类仍为本站整理。AtCoder rating 来自社区估计，可能为负；不同平台难度不直接比较。会员状态不明确的条目不推测为免费。

### 手动更新索引

```sh
conda activate ai_env
python scripts/sync_catalogs.py
python scripts/sync_catalogs.py --source luogu --source acwing --refresh
python scripts/build_sources.py
npm run build
```

默认重用 `.local/catalog-cache/` 成功缓存；`--refresh` 才向原站重新请求。请求按平台限速，遇到 403/429 或列表结构变化停止，已有完整快照不会因本次失败被覆盖。缓存重建保留实际获取日期，不把旧数据伪装成当天更新。PAT 保留原快照，未由上述命令刷新。

索引来源：[洛谷](https://www.luogu.com.cn/problem/list?type=luogu)、[AcWing](https://www.acwing.com/problem/)、[Codeforces API](https://codeforces.com/apiHelp/methods#problemset.problems)、[AtCoder Problems 数据文档](https://github.com/kenkoooo/AtCoderProblems/blob/main/doc/api.md)、[LeetCode 中国站](https://leetcode.cn/problemset/)、[PAT](https://pintia.cn/problem-sets/dashboard)。

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

后端测试实际编译 C、C++，运行全部 101 个 Python 参考程序，检查 AC / WA / CE / RE / TLE / OLE、请求鉴权、来源限制、导入校验、记录持久化、样例不计通过、已有 AC 不被 WA 覆盖。新增独立算法核对：线段树对照直接数组操作、最大流对照枚举最小割、SCC 对照可达关系、LCA 对照祖先链。索引测试覆盖数量、唯一 ID、公开字段、来源和 AcWing 错位编号；前端测试覆盖多标签、会员状态、分页、PAT 兼容和原有安全处理。

## GitHub Pages 部署

`.github/workflows/pages.yml` 在 push 到 `main` 时运行前端检查与构建，再把 `dist/` 发布到 GitHub Pages。仓库 Pages 设置使用 **GitHub Actions**。

使用相对资源路径及 hash 路由，可部署到 `/AyayaAlgorithm/` 子路径。网站中不包含 API token，不使用付费判题服务。

浏览器本地访问规则参考：[Chrome Local Network Access](https://developer.chrome.com/docs/modern-web-guidance/guides/security/local-network-access)、[MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)。
