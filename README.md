<p align="center">
  <img src="./assets/banner.png" alt="从零亲手搭一个 Coding Agent —— 不调用任何框架，每一块零件你都看得见" width="100%">
</p>

# Vibe Agent Course（8 天 · 从零搭建 Coding Agent）

> 从"跟 AI 聊天"到"AI 在你仓库里干活"，亲手搭完每一块零件。

## 项目目标

学完之后你能做到：

1. 理解 LLM 的工作原理（next-token prediction、token、幻觉、工具补强）
2. 用 Python 流式调用 LLM、设计 prompt、估算 token
3. 实现工具注册系统 + Agent 主循环（Function Calling）
4. 区分并实现 ReAct、Plan-and-Solve、Reflection 三种 Agent 范式
5. 从零实现上下文管理与记忆系统
6. 搭建完整的 Coding Agent（9 个工具）
7. 整合所有模块，部署为 CNB 仓库 NPC

## 内容总览

| Day | 主题 | 核心产物 |
|-----|------|---------|
| 1 | [认识你的 AI](./01-meet-your-ai/) | LLM 流式对话 + token 计算 |
| 2 | [Function Calling 与最小 Agent](./02-tools-and-agent-loop/) | `ToolRegistry` + Agent Loop |
| 3 | [Agent 范式](./03-agent-patterns/) | ReAct / Plan-and-Solve / Reflection |
| 4 | [上下文与记忆](./04-context-and-memory/) | `ContextManager` + `Memory` |
| 5 | [Coding Agent 工具集](./05-coding-agent-tools/) | 9 个工具实现 |
| 6 | [整合：完整 Coding Agent](./06-coding-agent-integration/) | Day2-5 零件拼装 |
| 7 | [Skills 扩展 + NPC 上线](./07-skills-and-npc/) | 自定义 Skills + 仓库 NPC |
| 8 | [总结 + 大作业](./08-recap-and-final/) | 复盘与结课 |

## 零件建造路径

每天的产物都是下一天的零件：

```
Day1: LLM 客户端           ─┐
Day2: ToolRegistry         ─┤
Day3: 三种范式（选一种）    ─┤──→  Day6 整合成完整 Agent  ──→  Day7 加 Skills + 挂 NPC
Day4: ContextManager + Mem ─┤
Day5: Coding 工具集 × 9    ─┘
```

## 目录结构

```
.
├── 01-meet-your-ai/              # Day1：认识 AI
├── 02-tools-and-agent-loop/      # Day2：Function Calling + 最小 Agent
├── 03-agent-patterns/            # Day3：Agent 范式
├── 04-context-and-memory/        # Day4：上下文与记忆
├── 05-coding-agent-tools/        # Day5：Coding Agent 工具集
├── 06-coding-agent-integration/  # Day6：整合
├── 07-skills-and-npc/            # Day7：Skills + NPC
├── 08-recap-and-final/           # Day8：总结
├── exercises/                      # 所有练习题（按天分目录）
├── examples/                       # 实践代码示例
│   ├── 01-hello-react/           # ReAct 模式旅行助手
│   ├── 02-hello-llm/            # 最小流式 LLM 客户端
│   ├── 03-hello-agents/         # hello-agents 框架上手
│   └── 04-my-agent/            # 从零搭建完整 Agent
└── assets/                         # 封面与全局资源
```

## 与实践代码的对应关系

| 实践项目 | 章节映射 |
|---------|---------|
| `examples/02-hello-llm/` | Day1 |
| `examples/01-hello-react/` | Day3 ReAct 范式 |
| `examples/03-hello-agents/` | Day3 框架对照 |
| `examples/04-my-agent/tools/` | Day2 + Day5 |
| `examples/04-my-agent/context/` | Day4 |
| `examples/04-my-agent/memory/` | Day4 |
| `examples/04-my-agent/skills/` | Day7 |

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
