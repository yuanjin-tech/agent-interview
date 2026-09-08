# AI Interview 项目协作规范

## 约束

**非常重要：**

1. 当用户提问时，不能修改任何东西，不能新增任何东西，不能删除任何东西，仅回答用户问题即可
2. 回答问题要言简意赅，不要长篇大论，用户有不明白的地方会自行追问
3. 除非用户特别要求，否则不允许修改`README.md`和`Agents.md`文件

## 项目定位

本项目是一个面向 Agent 应用开发岗位求职者的中文开源面试题库。

项目希望通过社区协作持续收集、修订和完善面试题及其答案，帮助求职者理解 Agent 应用开发中的核心概念、工程方法和实际问题，也为面试官提供可复用的题目参考。

当前只维护中文内容，不考虑多语言支持。

## 项目运作方式

- `pyproject.toml`

  工程使用`uv`进行管理

- `catalog.yaml`

  文件中记录了所有题目的元信息。该文件使用`schemas/catalog.schema.json`作为`schema`

- `questions`

  目录中包含所有问题的详细信息和回答。每个问题一个文件，文件名对应到`catalog.yaml`元信息中的id。

- `site/`

  Astro 静态网站源码。该网站会读取到`catalog.yaml`和`questions`下面的所有文件，并在打包时将它们打包为静态页面，最终部署到`github pages`。

- `Makefile`

  提供常用命令

- `scripts/create_question.py`

  这是给需要新增面试题的开源贡献者提供的脚本。贡献者会运行该脚本，以交互式命令的方式完成新的面试题的添加。

- `scripts/validate_content.py`

  该脚本用于验证内容是否合法。

- `.github`

  提供`github flow`

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
