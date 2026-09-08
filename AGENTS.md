# 项目说明

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

## 内容组织方式

项目采用索引与正文分离的两层结构。

### 第一层：题目目录

根目录的 `catalog.yaml` 是整个题库的统一索引。

它是一个以分类名称为键的对象。每个分类对应一个题目元数据数组：

```yaml
Agent 基础:
  - id: 550e8400-e29b-41d4-a716-446655440000
    title: Agent 如何决定是否调用工具？
    difficulty: intermediate
```

同一道题可以被多个分类引用，但不同分类中的相同 UUID 必须保持标题和难度一致。

当前 `catalog.yaml` 为空，正式收录第一道题后再建立实际分类。

### 第二层：题目正文

每道题使用一个独立的 Markdown 文件，统一放在 `questions/` 目录中：

```text
questions/<UUID>.md
```

例如：

```text
questions/550e8400-e29b-41d4-a716-446655440000.md
```

文件名中的 UUID 必须与 `catalog.yaml` 对应题目的 `id` 完全一致。UUID 一经创建不得修改或重新分配。

Markdown 文件不写 YAML Front Matter，也不重复保存元数据，只直接编写题目和回答等正文内容。

## 元数据规范

单条题目元数据只包含三个必填字段：

```yaml
id: 550e8400-e29b-41d4-a716-446655440000
title: Agent 如何决定是否调用工具？
difficulty: intermediate
```

- `id`：标准 UUID，是题目的永久唯一标识。
- `title`：用于目录、检索和页面导航的题目标题。
- `difficulty`：题目难度，只能是 `beginner`、`intermediate` 或 `advanced`。

不要擅自向题目元数据中增加分类、知识点、题型、岗位、状态、贡献者或更新时间等字段。确有需要时，应先修改项目规范和对应 Schema。

## Schema

- `schemas/question-metadata.schema.json` 校验单条题目元数据。
- `schemas/catalog.schema.json` 校验完整的 `catalog.yaml`，并通过 `$ref` 复用单题元数据 Schema。

修改目录结构或元数据格式时，必须同步更新相应 Schema。Schema 只能校验数据结构；UUID 对应的 Markdown 文件是否存在、文件是否遗漏索引，以及跨分类元数据是否一致，需要由后续校验脚本负责。

## 交互式新建题目命令

新增题目的推荐入口是根目录 `Makefile` 中的命令：

```bash
make new-question
```

该命令实际执行：

```bash
uv run python scripts/create_question.py
```

工程使用 uv 管理 Python 环境和依赖。交互界面使用 `questionary`，YAML 读写使用 `ruamel.yaml`；依赖声明在 `pyproject.toml` 中，具体版本记录在 `uv.lock` 中。

命令按照以下顺序与用户交互：

1. 要求输入面试题标题，标题不能为空。
2. 要求选择题目难度，不接受自由输入。中文选项“初级”“中级”“高级”分别写入 `beginner`、`intermediate`、`advanced`。
3. 要求选择题目分类。用户可以选择 `catalog.yaml` 中的现有分类，也可以选择“新建分类”并输入新的分类名称；分类名称不能为空。
4. 自动生成一个新的 UUID，并确保它没有出现在当前目录中。
5. 将 `id`、`title` 和 `difficulty` 写入 `catalog.yaml` 的相应分类。
6. 创建 `questions/<UUID>.md`，写入“问题”和“回答”的基础正文模板，不写元数据。
7. 创建成功后，在终端提示用户接下来需要编辑的 Markdown 文件路径。

用户在完成输入前取消命令时，不应修改目录或创建题目文件。更新目录时应继续采用临时文件加原子替换的方式；如果目录写入失败，应清理由本次命令新建的题目文件，避免产生不完整数据。

修改交互脚本后，运行以下测试：

```bash
uv run python -m unittest discover -s tests -v
```

## 贡献原则

这是一个社区共同维护的开源项目。贡献者可以通过 Pull Request 直接新增或修改题目，也可以通过 Issue 提交题目、答案建议或错误反馈，再由维护者整理为 Pull Request。

新增题目时应同时完成以下工作：

1. 生成一个新的 UUID。
2. 在 `catalog.yaml` 的至少一个分类中添加题目元数据。
3. 在 `questions/` 中创建同名 Markdown 文件。
4. 确保元数据符合 Schema。

优先使用交互式命令完成上述步骤：

```bash
make new-question
```

修改已有题目的正文时，不要更换 UUID。移动分类时只修改 `catalog.yaml`，不要复制题目正文。

题目和答案应准确、清楚，并以真实的 Agent 应用开发能力为考察目标。涉及具体框架或产品行为时，应避免把可能过时的实现细节描述成永久规则。
