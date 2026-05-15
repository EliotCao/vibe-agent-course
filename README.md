# Hello Agents 教学课程

一个循序渐进的 AI Agent 入门课程。每一章都是一个**独立可运行**的 Python 项目，聚焦一个核心概念。

## 课程结构

```
.
├── docs/                  # 全局教学文档
│   └── vibe-guide.md      # 用 CodeBuddy vibe 出 Agent 的逐步指南
│
├── ch01-hello-react/      # 第 1 章：智能旅行助手（ReAct：Thought-Action-Observation 循环）
├── ch02-hello-llm/        # 第 2 章：Hello LLM —— 最小可用的流式 LLM 客户端
└── ch03-hello-agents/     # 第 3 章：用 hello-agents 框架快速搭建 Agent
```

## 章节索引

| 章节 | 标题 | 核心概念 |
|------|------|---------|
| [ch01](./ch01-hello-react/) | Hello ReAct —— 智能旅行助手 | LLM 客户端 / System Prompt / Tools / ReAct Loop |
| [ch02](./ch02-hello-llm/) | Hello LLM —— 流式 LLM 客户端 | OpenAI 兼容接口 / 流式响应 / messages 协议 |
| [ch03](./ch03-hello-agents/) | Hello Agents 框架快速上手 | SimpleAgent / ReActAgent / ToolRegistry |

> 更多章节陆续添加中。

## 环境准备

本课程使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖（环境中已内置）。

整个仓库以 **uv workspace** 组织：根目录一个共享的 `.venv`，所有章节都用同一个 Python 环境。这样 IDE 只需选一次解释器即可在任意章节里正常补全、跳转到第三方库源码。

```bash
# 在仓库根目录执行一次，安装所有章节依赖
uv sync --all-packages
```

随后将 IDE 的 Python 解释器指向 `${workspaceFolder}/.venv/bin/python`（仓库已在 `.vscode/settings.json` 中预置）。

## 如何运行某一章

进入章节目录直接用 `python` 即可——CNB 云端 IDE 已为终端预激活根 `.venv`：

```bash
cd ch01-hello-react
python main.py
```

> 在本地、CI 或不确定环境是否激活时，推荐用 `uv run python main.py`。
> `uv run` 会自动使用根 `.venv`，并在依赖缺失时先 `uv sync` 再执行，跨环境最稳。

具体细节请参考各章节的 `README.md`。

## 新增一章时

1. 在根目录新建子目录 `chNN-xxx/`，里面放该章的 `pyproject.toml`（含 `[tool.uv] package = false`）和源码。
2. 把目录名追加到根 `pyproject.toml` 的 `[tool.uv.workspace].members`。
3. 在根目录运行 `uv sync --all-packages`，即可把新章节的依赖装入共享 `.venv`。
