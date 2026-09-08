# 贡献一个新问题

本项目通过交互式命令创建新问题。

## 1. 获取仓库

先 Fork 本仓库，然后将你的 Fork 克隆到本地并进入项目目录：

```bash
git clone <你的 Fork 仓库地址>
cd ai-interview
```

## 2. 运行交互式命令

你可以任选下面一种方式运行新建问题命令。

### 方式一：使用 uv

先[安装 uv](https://docs.astral.sh/uv/getting-started/installation/)，再将项目依赖安装到虚拟环境：

```bash
uv sync
```

然后运行：

```bash
uv run python scripts/create_question.py
```

### 方式二：直接使用 Python

请先确保当前 Python 环境为 Python 3.11 或更高版本，并已安装项目依赖：

```bash
python -m pip install questionary ruamel.yaml
python scripts/create_question.py
```

如果你的系统使用 `python3` 命令，请将上面的 `python` 替换为 `python3`。

### 方式三：使用 Make

请先安装 uv，并执行一次 `uv sync` 安装依赖，然后运行：

```bash
make new
```

## 3. 填写问题信息

命令会依次要求你填写或选择三项信息：

1. 问题标题。
2. 问题难度：初级、中级或高级。
3. 问题分类：选择已有分类，或者新建一个分类。

完成后，命令会在终端中显示需要继续编辑的问题文件路径。

## 4. 完善问题和回答

打开命令提示的 `questions/<UUID>.md` 文件：

```markdown
# 问题

<在这里更详细的描述问题>

# 回答

<在这里详细的描述问题答案>

# <可以自由添加更多章节>
```

提交前，请确认：

- 问题属于 Agent 应用开发范畴。
- 问题标题、难度和分类填写正确。
- 回答内容完整、准确且易于理解。
- `catalog.yaml` 和对应的 Markdown 文件都已包含在本次修改中。

## 5. 通过 Pull Request 提交

创建分支并提交修改：

```bash
git switch -c add-question/<简短名称>
git add catalog.yaml questions/
git commit -m "添加问题：<问题标题>"
git push -u origin add-question/<简短名称>
```

最后，在代码托管平台上从该分支向本仓库发起 Pull Request，并在描述中简要说明新增问题的内容。维护者审核通过后，问题就会被收录到题库中。
