# AI Interview 项目协作规范

本文件记录当前仓库的内容边界、数据约定、开发命令、网站构建方式和协作流程。修改仓库时应以实际代码、Schema 和自动化工作流为准；如果改变了实际做法，应在同一次修改中同步更新本文件。

## 项目定位

本项目是一个面向 Agent 应用开发岗位求职者的中文开源面试题库。

项目希望通过社区协作持续收集、修订和完善面试题及其答案，帮助求职者理解 Agent 应用开发中的核心概念、工程方法和实际问题，也为面试官提供可复用的题目参考。

当前只维护中文内容，不考虑多语言支持。

## 内容范围

题目应聚焦 Agent 应用开发层，例如：

- Agent 的基本架构、运行流程和设计取舍。
- 工具调用、状态管理、记忆和上下文管理。
- Agent 与 RAG、MCP、外部服务及业务系统的集成。
- 单 Agent、多 Agent、子 Agent 和人机协作。
- Agent 应用的测试、评估、可观测性、安全和权限控制。
- Agent 应用开发框架、工程实践、故障排查和系统设计。
- 与 Agent 应用岗位直接相关的模型适配和微调，例如为工具调用、指令遵循或特定业务场景进行微调。

项目不收录基础模型研发层的内容，例如：

- 基础模型预训练、大规模模型训练，以及与 Agent 应用岗位没有直接关系的纯训练算法。
- 模型部署、模型服务和推理引擎。
- GPU、算子优化、量化和分布式训练。
- 与 Agent 应用开发没有直接关系的通用算法题或纯模型原理题。

判断一道题是否适合本项目时，应优先考虑：它是否在考察候选人设计、实现、调试或维护 Agent 应用的能力。

## 仓库结构

```text
catalog.yaml                         # 题目分类和元数据的唯一索引
questions/<UUID>.md                  # 每道题的正文
schemas/                             # catalog 和单题元数据 Schema
scripts/create_question.py           # 交互式新建题目
scripts/validate_content.py          # 内容与索引一致性校验
tests/                               # Python 单元测试
site/                                # Astro 静态网站源码和 npm 锁文件
.github/workflows/deploy-pages.yml   # GitHub Pages 构建与发布
docs/                                # 面向贡献者的文档
Makefile                             # 本地开发命令统一入口
pyproject.toml / uv.lock             # Python 项目声明与依赖锁定
```

## 内容组织方式

项目采用索引与正文分离的两层结构。

### 第一层：题目目录

根目录的 `catalog.yaml` 是整个题库的统一索引。

它是一个以分类名称为键的对象。每个分类对应一个题目元数据数组：

```yaml
Agent 基础:
  - id: 550e8400-e29b-41d4-a716-446655440000
    title: Agent 如何决定是否调用工具？
    difficulty: medium
```

同一道题可以被多个分类引用，但不同分类中的相同 UUID 必须保持标题和难度一致。

当前 `catalog.yaml` 已经收录题目和分类。分类名称和题目数量会持续变化，不应在文档或网站代码中另行硬编码；网站构建时直接从目录计算。

### 第二层：题目正文

每道题使用一个独立的 Markdown 文件，统一放在 `questions/` 目录中：

```text
questions/<UUID>.md
```

例如：

```text
questions/550e8400-e29b-41d4-a716-446655440000.md
```

文件名中的 UUID 必须与 `catalog.yaml` 对应题目的 `id` 完全一致，并统一使用小写。UUID 一经创建不得修改、复用给另一道题或重新分配。

Markdown 文件不写 YAML Front Matter，也不重复保存元数据，只直接编写题目和回答等正文内容。

### 题目正文结构

题目 Markdown 使用一级标题划分网站中的内容区块。“问题”和“回答”是必需且不得为空的部分；“面试考察点”和“参考资料”是网站已支持的可选部分：

```markdown
# 问题

Agent 如何决定是否调用工具？

# 回答

<参考回答>

# 面试考察点

<希望候选人表现出的理解或判断能力>

# 参考资料

- [资料名称](https://example.com)
```

“# 问题”下的文字必须与 `catalog.yaml` 中的 `title` 一致。各部分内部可以使用二级及更低级标题、列表、代码块和链接。如果新增其他一级部分并希望它在网站上显示，必须同步扩展 `site/src/lib/content.ts` 和题目详情页。

## 元数据规范

单条题目元数据只包含三个必填字段：

```yaml
id: 550e8400-e29b-41d4-a716-446655440000
title: Agent 如何决定是否调用工具？
difficulty: medium
```

- `id`：标准小写 UUID，是题目的永久唯一标识。
- `title`：用于目录、检索和页面导航的题目标题。
- `difficulty`：题目难度，只能是 `easy`、`medium` 或 `hard`。

不要擅自向题目元数据中增加分类、知识点、题型、岗位、状态、贡献者或更新时间等字段。确有需要时，应先修改项目规范和对应 Schema。

## Schema

- `schemas/question-metadata.schema.json` 校验单条题目元数据。
- `schemas/catalog.schema.json` 校验完整的 `catalog.yaml`，并通过 `$ref` 复用单题元数据 Schema。

修改目录结构或元数据格式时，必须同步更新相应 Schema、创建脚本、校验脚本、网站内容加载逻辑和测试。

## 内容校验

`scripts/validate_content.py` 是题库的统一校验入口，执行：

```bash
make validate
```

当前校验内容包括：

- `catalog.yaml` 能否解析，分类是否为非空题目数组。
- 元数据是否符合 `question-metadata.schema.json`，是否只包含允许的字段。
- UUID 是否是标准小写格式，以及同一分类内是否重复。
- 同一 UUID 跨分类出现时，标题和难度是否一致。
- 每条目录记录是否存在对应正文，以及是否存在未加入目录的孤立正文。
- 题目文件名是否为小写 `UUID.md`，“问题”和“回答”部分是否非空。
- 正文问题文字是否与目录标题一致，Markdown 中的本地文件链接是否存在且没有超出项目目录。

校验失败时脚本以非零状态退出，网站构建和发布不应继续。修改校验规则时，在 `tests/test_validate_content.py` 中增加或更新对应测试。

## 交互式新建题目命令

新增题目的推荐入口是根目录 `Makefile` 中的命令：

```bash
make new
```

该命令实际执行：

```bash
uv run python scripts/create_question.py
```

工程使用 uv 管理 Python 环境和依赖。交互界面使用 `questionary`，YAML 读写使用 `ruamel.yaml`；依赖声明在 `pyproject.toml` 中，具体版本记录在 `uv.lock` 中。

命令按照以下顺序与用户交互：

1. 要求输入面试题标题，标题不能为空。
2. 要求选择题目难度，不接受自由输入。中文选项“初级”“中级”“高级”分别写入 `easy`、`medium`、`hard`。
3. 要求选择题目分类。用户可以选择 `catalog.yaml` 中的现有分类，也可以选择“新建分类”并输入新的分类名称；分类名称不能为空。
4. 自动生成一个新的 UUID，并确保它没有出现在当前 `catalog.yaml` 中；创建正文时使用排他新建，避免覆盖已有文件。
5. 将 `id`、`title` 和 `difficulty` 写入 `catalog.yaml` 的相应分类。
6. 创建 `questions/<UUID>.md`，写入“问题”和“回答”的基础正文模板，不写元数据。
7. 创建成功后，在终端提示用户接下来需要编辑的 Markdown 文件路径。

用户在完成输入前取消命令时，不应修改目录或创建题目文件。更新目录时应继续采用临时文件加原子替换的方式；如果目录写入失败，应清理由本次命令新建的题目文件，避免产生不完整数据。

修改交互脚本后，至少运行内容校验和全部 Python 单元测试：

```bash
make validate
make test
```

## 工具链与常用命令

项目包含两套彼此配合的工具链：

- Python 3.11 或更高版本：负责交互式新建题目、内容校验和单元测试，使用 uv 管理依赖。
- Node.js 22.19 或更高版本：负责 Astro 网站的本地预览和静态构建，使用 npm 管理依赖。

首次开发时安装依赖：

```bash
uv sync
make site-install
```

根目录 `Makefile` 是日常操作的统一入口：

| 命令 | 作用 |
| --- | --- |
| `make new` | 交互式创建题目 |
| `make validate` | 校验题库元数据、正文和链接 |
| `make test` | 运行 `tests/` 中的 Python 单元测试 |
| `make site-install` | 安装或更新 `site/` 的 npm 依赖 |
| `make site-dev` | 先校验内容，再启动 Astro 本地开发服务器 |
| `make site-build` | 先校验内容，再生成可部署的静态网站 |

`uv.lock` 和 `site/package-lock.json` 都必须提交。修改依赖声明后应同步更新对应锁文件。`.venv/`、`site/node_modules/`、`site/.astro/` 和 `site/dist/` 是本地或构建产物，不得提交。

## 可视化网站

`site/` 是 Astro 纯静态网站。它没有独立的题目数据库，构建时直接读取根目录的 `catalog.yaml` 和 `questions/*.md`：

- `site/src/lib/content.ts` 负责读取目录、合并跨分类引用、分割 Markdown 区块并生成搜索文本。
- `site/src/pages/index.astro` 是题目索引页，提供全文搜索、分类筛选和难度筛选。
- `site/src/pages/questions/[id].astro` 在构建时为每个 UUID 生成独立详情页。
- `site/src/styles/global.css` 维护全局视觉、响应式布局、焦点状态和减少动画偏好适配。
- Markdown 渲染默认禁用原始 HTML，外部链接在新标签页打开并添加 `noopener noreferrer`。

新增题目后不需要手工创建网页。修改题库数据结构、Markdown 章节规则或网站路由时，必须同时检查首页、题目详情页、搜索索引和 GitHub Pages 子路径。

网站修改的最低验证要求是：

```bash
make test
make site-build
```

涉及布局、样式或交互的修改，还应通过真实浏览器检查桌面端和窄屏移动端，并验证搜索、筛选、题目跳转和控制台错误。

## GitHub Pages 发布

`.github/workflows/deploy-pages.yml` 是当前唯一的自动发布工作流，在以下情况运行：

- 推送到 `main` 分支。
- 在 GitHub Actions 页面手动触发 `workflow_dispatch`。

工作流使用 Python 3.13 执行内容校验和单元测试，使用 Node.js 24 安装网站依赖并构建 `site/dist/`，然后通过 GitHub Pages artifact 发布。不使用 `gh-pages` 分支，也不应将 `site/dist/` 提交到仓库。

Astro 配置会根据 `GITHUB_REPOSITORY` 自动处理项目站点的 `/<repository>/` 基础路径；仓库名为 `<owner>.github.io` 时使用根路径。首次发布前，仓库管理员需要在 **Settings → Pages → Build and deployment** 中将 Source 设为 **GitHub Actions**。

当前工作流没有监听 `pull_request`，因此 PR 上不会由这个工作流自动生成校验状态；贡献者必须在提交 PR 前运行本文规定的本地检查。如果以后增加独立 PR CI，应同步更新本节。

## GitHub Flow

本项目使用以 `main` 为唯一长期分支的 GitHub Flow。`main` 同时是 GitHub Pages 自动发布的触发分支，因此应始终保持可校验、可测试、可构建。

### 1. 从最新 `main` 创建短生命分支

不要在过时分支上继续新工作。分支名应简短且表达意图，例如：

```text
add-question/tool-selection
fix-question/mcp-auth
site/improve-mobile-filter
chore/content-validator
```

### 2. 实现并提交可审查的小批量改动

一个分支和 Pull Request 应聚焦一个主题。不要把题目内容、不相关的前端重构和大批量格式化混在同一个 PR 中。提交信息应描述实际变更，例如：

```text
添加问题：Agent 如何选择工具
修复题目：明确 MCP 授权边界
feat(site): 优化移动端筛选
```

### 3. 推送前按改动范围验证

- 仅修改题目或目录：运行 `make validate`。
- 修改 Python 脚本、Schema 或测试：运行 `make validate` 和 `make test`。
- 修改网站内容加载、页面、样式或工作流：运行 `make test` 和 `make site-build`；涉及 UI 时再完成浏览器检查。
- 修改 Python 或 npm 依赖：确认对应锁文件已更新。

提交 PR 前检查 `git diff` 和 `git status`，不得包含密钥、个人配置、缓存、依赖目录或构建产物。

### 4. 通过 Pull Request 讨论和审查

将分支推送到自己的 Fork 或有权限的远程仓库，然后向 `main` 发起 Pull Request。PR 描述至少说明：

- 修改了什么，为什么要改。
- 如何验证，实际运行了哪些命令。
- 网站视觉变更的桌面端和移动端截图。
- 未完成的验证、已知限制或需要审查者特别关注的地方。

根据审查意见继续向同一分支提交，PR 会自动更新。合并前应解决审查对话和合并冲突。

### 5. 合并、发布与清理

PR 通过审查且要求的检查全部通过后才合并到 `main`。合并后 GitHub Pages 工作流会自动发布；维护者应确认 Actions 任务成功和线上网站可访问。工作完成后删除已合并的短生命分支，不要在旧分支上开始新任务。

### 远程仓库建议配置

下列项目属于 GitHub 仓库设置，无法仅通过当前代码确认是否已启用。维护者应为 `main` 配置 branch protection 或 ruleset：

- 要求通过 Pull Request 合并，限制直接推送。
- 要求必要的审查批准并解决全部审查对话。
- 在增加 PR CI 后，将其校验任务设为 required status check。
- 禁止强制推送和删除 `main`。

流程原则参考 [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)；远程保护规则参考 [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)。

## 贡献原则

这是一个社区共同维护的开源项目。贡献者可以通过 Pull Request 直接新增或修改题目，也可以通过 Issue 提交题目、答案建议或错误反馈，再由维护者整理为 Pull Request。

新增题目时应同时完成以下工作：

1. 生成一个新的 UUID。
2. 在 `catalog.yaml` 的至少一个分类中添加题目元数据。
3. 在 `questions/` 中创建同名 Markdown 文件。
4. 确保元数据符合 Schema。

优先使用交互式命令完成上述步骤：

```bash
make new
```

修改已有题目的正文时，不要更换 UUID。移动分类时只修改 `catalog.yaml`，不要复制题目正文。

题目和答案应准确、清楚，并以真实的 Agent 应用开发能力为考察目标。涉及具体框架或产品行为时，应避免把可能过时的实现细节描述成永久规则。

## 许可证边界

许可证适用范围以根目录 `LICENSE` 和 `LICENSE-CODE` 为准：

- `README.md`、`docs/`、`questions/` 和 `catalog.yaml` 等题库与文档内容使用 CC BY 4.0。
- `scripts/`、`schemas/`、`tests/`、`site/`、工作流和工程配置等软件与工程文件使用 MIT License。
- 引用或引入的第三方材料仍遵循其自身许可条款。
