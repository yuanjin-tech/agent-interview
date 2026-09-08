# AI Interview

一个面向 **Agent 应用开发岗位求职者** 的中文开源面试题库。

本项目通过社区协作持续收集、修订和完善 Agent 应用开发相关的面试题与参考答案，帮助求职者系统理解核心概念、工程方法和真实项目中的常见问题，同时也为面试官提供可复用的题目参考。

## 内容范围

题库聚焦于设计、实现、调试和维护 Agent 应用所需的能力，主要包括：

- Agent 的基本架构、运行流程与设计取舍
- 工具调用、状态管理、记忆与上下文管理
- Agent 与 RAG、MCP、外部服务及业务系统的集成
- 单 Agent、多 Agent、子 Agent 与人机协作
- Agent 应用的测试、评估、可观测性、安全与权限控制
- Agent 开发框架、工程实践、故障排查与系统设计
- 与 Agent 应用岗位直接相关的模型适配与微调

本项目不收录基础模型预训练、推理引擎、GPU 与算子优化、分布式训练，以及与 Agent 应用开发无直接关系的通用算法题。

## 项目结构

```text
.
├── catalog.yaml                         # 题目分类与元数据索引
├── questions/                           # 每道题的问题与回答正文
│   └── <UUID>.md
├── schemas/                             # 目录和题目元数据的 JSON Schema
├── scripts/create_question.py           # 交互式新建题目脚本
├── docs/contributing-a-question.md      # 新增题目贡献指南
├── Makefile
└── pyproject.toml
```

题库采用“索引与正文分离”的组织方式：

- `catalog.yaml` 按分类保存题目的 UUID、标题和难度。
- `questions/<UUID>.md` 保存对应题目的问题描述与参考答案。
- 同一道题可以出现在多个分类中，但始终复用同一个 UUID 和正文文件。

## 参与贡献

欢迎通过 Pull Request 新增题目、完善答案或修正错误。新增题目时，请同时更新目录索引和对应的题目正文。

具体操作请阅读：[贡献一个新问题](docs/contributing-a-question.md)。
