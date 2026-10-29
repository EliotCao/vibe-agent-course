<p align="center">
  <img src="./assets/banner.png" alt="从零亲手搭一个 Coding Agent —— 不调用任何框架，每一块零件你都看得见" width="100%">
</p>

# Vibe Agent — 从零搭建 Coding Agent

> 从"跟 AI 聊天"到"AI 在你仓库里干活"，亲手搭完每一块零件。

---

## 📦 如何使用本仓库

推荐「**先 Fork，再用云原生开发环境学习实践**」，开始之前请先看一遍 [准备工作（PREPARE.md）](./PREPARE.md)：为何无需本地环境、以及学习所需 token（积分）的获取方式。

1. **Fork** 到自己的命名空间（点右上角「Fork」），笔记与进度都存在你自己的仓库里。
2. 在你的仓库点 **「云原生开发」**，拉起云端 VSCode（首次自动 `uv sync`），无需本地配环境。
3. 在云端 IDE 里读讲义、跑 Demo、做笔记，改完直接提交回仓库。

---

## 🚀 课程学习中心 · 在浏览器里读讲义 + 一键跑 Demo

| | |
|:---|:---|
| 📚 **三栏阅读** | 自动生成大纲、Markdown 讲义、按节笔记 |
| 🐍 **一键运行** | 每节 Python Demo 流式输出，可交互输入 stdin |
| ✎ **可编辑代码** | 直接修改源码并保存重跑（⌘S / ⌘+Enter） |
| ☁ **笔记同步** | 一键提交到仓库 `notes/`，跨设备共享 |

**两步进入：**

1. 点右上角 **「云原生开发」** 进入 VSCode WebIDE（首次启动会自动 `uv sync` 装好课程依赖）
2. 在终端里执行 ↓（或 `cd course-ui && bash run.sh`），然后浏览器打开端口转发面板的 **8765**

```bash
bash course-ui/run.sh
```

> 想本地跑：`python3 course-ui/server.py`，然后访问 <http://127.0.0.1:8765> 。零依赖，纯 Python 标准库。
> 详细文档见 [`course-ui/README.md`](./course-ui/README.md)。

---

## 项目目标

完成后你能做到：

1. 理解 LLM 的工作原理（next-token prediction、token、向量、幻觉）
2. 用 Python 流式调用 LLM、设计 prompt、估算 token
3. 实现工具注册系统 + Agent 主循环（Function Calling）
4. 区分并实现 ReAct、Plan-and-Solve、Reflection 三种 Agent 范式
5. 从零实现上下文管理与向量记忆系统
6. 搭建完整的 Coding Agent（5 个核心工具）并整合所有模块为可运行的 Agent
7. 扩展 Skills，部署为 CNB 仓库 NPC

## 内容总览

| 模块 | 主题 | 知识点 | 你的产出 |
|------|------|--------|---------|
| 01 | [认识你的 AI](./01-meet-your-ai/) | Next-token prediction · Token 与向量 · Messages 协议（system/user/assistant） · 上下文窗口与成本 · 幻觉 | `my-agent/llm.py` — LLMClient 类 |
| 02 | [Function Calling 与最小 Agent](./02-tools-and-agent-loop/) | Chatbot vs Agent · Function Calling 协议 · ToolRegistry（自动生成 JSON schema） · 最小 Agent Loop | `my-agent/tools.py` — ToolRegistry 类 |
| 03 | [Agent 范式](./03-agent-patterns/) | ReAct（边想边做） · Plan-and-Solve（先规划再执行） · Reflection（起草→评审→修订） · 范式选型 | `my-agent/agent.py` — Agent 主循环 |
| 04 | [上下文与记忆](./04-context-and-memory/) | 上下文爆炸问题 · 管理策略（keep_last + 摘要压缩） · 向量记忆（Embedding + 余弦相似度） · Agent v2 整合 | `my-agent/context.py` + `memory.py` |
| 05 | [Coding Agent 工具集与整合](./05-coding-agent-tools/) | 5 阶段工作流（理解→定位→修改→验证→汇报） · 工具设计哲学 · 5 个核心工具（read/write/edit/list_dir/bash） · 模块协作架构 · REPL/Solo/WebUI 形态 | `my-agent/coding_tools/` — 5 个工具 + `my-agent/main.py` 整合 |
| 06 | [Skills 扩展 + NPC 上线](./06-skills-and-npc/) | Skills 系统（SKILL.md） · Skills vs Tool Call · NPC 概念 · CNB 上 NPC 用法 · 自定义 NPC（Docker 打包课后实验） | 自定义 Skills + 仓库 NPC |

## 动手练习

各模块的代码填空（`my-agent/` 各文件 + 自动化测试）与配套练习已迁移到独立的**练习仓库**，按章节完成实践：

> 📦 **练习仓库**：<https://cnb.cool/opencamp/learning-agent/vibe-agent-exercise>

## 先修要求

- Python 基础（函数、类、字典、文件读写）
- 命令行基本使用（`cd` / `ls` / `cat` / 环境变量）
- 一台能联网的电脑

## 补充基础知识（Git / Docker）

本课程会用到 Git 协作与 Docker 交付。如果这两块还不熟，推荐先过一遍这份从零讲起的配套教程：

> 📚 **参考教程**：<https://cnb.cool/whut1/ai-engineering-course>

| 章节 | 内容 | 你会学到 |
|------|------|---------|
| [Git 原理与使用](https://cnb.cool/whut1/ai-engineering-course) | 版本控制思想 · Git 对象模型 · 分支与远程协作 | 独立完成一次完整的分支协作流程 |
| [Docker 与 Dockerfile](https://cnb.cool/whut1/ai-engineering-course) | 镜像/容器概念 · Dockerfile 编写 · 端口映射 | 编写 Dockerfile 并构建运行自己的镜像 |

> 💡 这两块都从零讲起、无需提前掌握；遇到不懂的概念随时回来查阅即可。
