<p align="center">
  <img src="./assets/banner.png" alt="从零亲手搭一个 Coding Agent —— 不调用任何框架，每一块零件你都看得见" width="100%">
</p>

# Vibe Agent — 从零搭建 Coding Agent

> 从"跟 AI 聊天"到"AI 在你仓库里干活"，亲手搭完每一块零件。

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

1. 用 VibeCoding 快速做出一个能跑的小项目，并推到 CNB 云原生环境运行
2. 理解 LLM 的工作原理（next-token prediction、token、向量、幻觉）
3. 用 Python 流式调用 LLM、设计 prompt、估算 token
4. 实现工具注册系统 + Agent 主循环（Function Calling）
5. 区分并实现 ReAct、Plan-and-Solve、Reflection 三种 Agent 范式
6. 从零实现上下文管理与向量记忆系统
7. 搭建完整的 Coding Agent（5 个核心工具）
8. 整合所有模块，部署为 CNB 仓库 NPC

## 内容总览

| 模块 | 主题 | 知识点 | 你的产出 |
|------|------|--------|---------|
| 01 | [VibeCoding 入门](./01-vibecoding-intro/) | VibeCoding 是什么 · 跟 AI 协作的节奏 · vibe 一个小游戏 · 推到 CNB · 云原生开发环境运行 | 一个你 vibe 出来、跑在 CNB 上的小游戏 |
| 02 | [认识你的 AI](./02-meet-your-ai/) | Next-token prediction · Token 与向量 · Messages 协议（system/user/assistant） · 上下文窗口与成本 · 幻觉 | `my-agent/llm.py` — LLMClient 类 |
| 03 | [Function Calling 与最小 Agent](./03-tools-and-agent-loop/) | Chatbot vs Agent · Function Calling 协议 · ToolRegistry（自动生成 JSON schema） · 最小 Agent Loop | `my-agent/tools.py` — ToolRegistry 类 |
| 04 | [Agent 范式](./04-agent-patterns/) | ReAct（边想边做） · Plan-and-Solve（先规划再执行） · Reflection（起草→评审→修订） · 范式选型 | `my-agent/agent.py` — Agent 主循环 |
| 05 | [上下文与记忆](./05-context-and-memory/) | 上下文爆炸问题 · 管理策略（keep_last + 摘要压缩） · 向量记忆（Embedding + 余弦相似度） · Agent v2 整合 | `my-agent/context.py` + `memory.py` |
| 06 | [Coding Agent 工具集](./06-coding-agent-tools/) | 5 阶段工作流（理解→定位→修改→验证→汇报） · 工具设计哲学 · 5 个核心工具（read/write/edit/list_dir/bash） | `my-agent/coding_tools/` — 5 个工具 |
| 07 | [整合：完整 Coding Agent](./07-coding-agent-integration/) | 模块协作架构 · REPL 交互界面 · 端到端调试 · 真实任务闭环 | `my-agent/main.py` — 零件拼装 |
| 08 | [Skills 扩展 + NPC 上线 + 大作业](./08-skills-and-npc/) | Skills 系统（SKILL.md） · NPC 概念 · Docker 打包 · CNB Pipeline + NPC 部署 · 结课大作业 | 自定义 Skills + 仓库 NPC + 大作业 |

## 核心产出：my-agent

逐步实现各模块，最终在模块 07 拼装成完整 Agent：

```
my-agent/
├── llm.py              # 模块02：LLM 客户端
├── tools.py            # 模块03：ToolRegistry
├── agent.py            # 模块04：Agent 主循环
├── context.py          # 模块05：ContextManager
├── memory.py           # 模块05：Memory
├── coding_tools/       # 模块06：5 个工具实现
├── main.py             # 模块07：组装入口
└── tests/              # 各模块的自动化测试
```

搭建路线：

```
01: VibeCoding 入门（先玩起来，建立兴趣）
        ↓
02: LLMClient           ─┐
03: ToolRegistry         ─┤
04: Agent Loop           ─┤──→  07 拼装成完整 Agent  ──→  08 加 Skills + 挂 NPC + 大作业
05: Context + Memory     ─┤
06: Coding Tools × 5     ─┘
```

## 目录结构

```
.
├── 01-vibecoding-intro/          # 讲义 + Demo（先玩起来）
├── 02-meet-your-ai/              # 讲义 + Demo
├── 03-tools-and-agent-loop/      # 讲义 + Demo
├── 04-agent-patterns/            # 讲义 + Demo
├── 05-context-and-memory/        # 讲义 + Demo
├── 06-coding-agent-tools/        # 讲义 + Demo
├── 07-coding-agent-integration/  # 讲义 + Demo
├── 08-skills-and-npc/            # 讲义 + Demo + 大作业
├── my-agent/                       # ★ 你的核心产出（逐步填空各模块）
├── exercises/                      # 配套练习题（代码填空 + 自动验证）
├── examples/                       # 完整参考实现
└── assets/                         # 封面与全局资源
```

## 学习工作流

```bash
# 1. 看讲义（lecture/）
# 2. 跑 Demo（lab/）
# 3. 补全 my-agent/ 里对应的模块
# 4. 跑测试验证
cd my-agent && python tests/test_llm.py    # 模块02
cd my-agent && python tests/test_tools.py  # 模块03
# ...
```

## 环境准备

本项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖。

```bash
# 在仓库根目录执行一次，安装所有依赖
uv sync --all-packages
```

## 先修要求

- Python 基础（函数、类、字典、文件读写）
- 命令行基本使用（`cd` / `ls` / `cat` / 环境变量）
- 一台能联网的电脑

不需要提前会：Git、Docker、Agent、提示词工程——这些都会从零讲起。
