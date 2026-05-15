# Hello Agents 教学课程

一个循序渐进的 AI Agent 入门课程。每一章都是一个**独立可运行**的 Python 项目，聚焦一个核心概念。

## 课程结构

```
.
├── docs/                  # 全局教学文档
│   └── vibe-guide.md      # 用 CodeBuddy vibe 出 Agent 的逐步指南
│
└── ch01-hello-agent/      # 第 1 章：智能旅行助手（Thought-Action-Observation 循环）
```

## 章节索引

| 章节 | 标题 | 核心概念 |
|------|------|---------|
| [ch01](./ch01-hello-agent/) | Hello Agent —— 智能旅行助手 | LLM 客户端 / System Prompt / Tools / Agent Loop |

> 更多章节陆续添加中。

## 环境准备

本课程使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖。如未安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 如何运行某一章

每章都是独立的 Python 项目，进入对应目录即可：

```bash
cd ch01-hello-agent
uv sync                  # 读取 pyproject.toml，自动创建 .venv 并安装依赖
uv run python main.py    # 在项目环境中运行
```

具体细节请参考各章节的 `README.md`。
