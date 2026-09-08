# 修改一个问题

如果你发现已有问题的标题、难度、问题描述或回答需要调整，可以选择以下任一方式反馈。

## 方式一：提交 Issue

如果你不方便直接修改代码，可以[提交 Issue](https://github.com/yuanjin-tech/agent-interview/issues/new)，由维护者确认并完成修改。

Issue 中请尽量说明：

- 要修改的问题标题或 `id`。
- 当前内容存在什么问题。
- 建议如何修改；如果涉及事实或技术结论，请附上参考资料。

## 方式二：提交 Pull Request

如果你希望直接完成修改，可以 Fork 本仓库，在自己的分支中修改后提交 Pull Request。

### 1. 找到问题

在 `catalog.yaml` 中找到目标问题。例如：

```yaml
- id: 04253a46-dc2a-4622-87b7-232023f37053
  title: 使用 LLM-as-a-Judge 评测 Agent 有哪些风险，如何降低偏差？
  difficulty: hard
```

对应的问题文件是：

```text
questions/04253a46-dc2a-4622-87b7-232023f37053.md
```

题目 `id` 与文件名一一对应，请通过 `id` 确认自己修改的是正确文件。

### 2. 明确可以修改的内容

在 `catalog.yaml` 中，只能修改目标问题的以下字段：

- `title`：问题标题。
- `difficulty`：问题难度，只能填写 `easy`、`medium` 或 `hard`。

如果同一个 `id` 出现在多个分类中，修改标题或难度时必须同步修改它的所有条目，保持元数据一致。

你还可以修改对应的 `questions/<id>.md` 文件，包括：

- `# 问题` 下的问题描述。
- `# 回答` 下的回答内容。
- 该文件中的其他补充章节，例如面试考察点。

如果修改了 `catalog.yaml` 中的标题，也应同步检查并修改题目文件中 `# 问题` 下的文字，避免标题与问题描述不一致。

### 3. 不允许修改的内容

- 不得修改问题的 `id`。
- 不得重命名对应的 `questions/<id>.md` 文件。
- 不得将问题移动到其他分类，也不得修改分类名称。
- 不得删除题目在 `catalog.yaml` 中的条目或对应的问题文件。
- 不得在同一个 Pull Request 中修改与该问题无关的题目或项目文件。

如果你认为问题需要更换 `id`、移动分类或删除，请先提交 Issue，由维护者处理。

### 4. 修改问题文件

问题文件必须至少保留以下两个非空章节：

```markdown
# 问题

<问题描述>

# 回答

<问题答案>
```

修改时请确保内容仍属于 Agent 应用开发范畴，结论准确、表达清楚，并保留有效的本地链接。

### 5. 验证修改

提交前运行：

```bash
make validate
make test
```

然后检查 `git diff` 和 `git status`，确认本次提交只包含目标问题所需的修改。

### 6. 提交 Pull Request

创建分支并提交修改：

```bash
git switch -c fix-question/<简短名称>
git add catalog.yaml questions/<问题 ID>.md
git commit -m "修复问题：<问题标题>"
git push -u origin fix-question/<简短名称>
```

如果只修改了问题文件，不需要将未改动的 `catalog.yaml` 加入提交。

最后，从该分支向本仓库的 `main` 分支发起 Pull Request。PR 描述应说明修改了哪个问题、为什么修改、具体修改了什么，以及实际运行了哪些验证命令。
