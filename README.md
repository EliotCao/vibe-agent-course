# VibeCoding 课程（8 天 · Agent 主线）

> 从"跟 AI 聊天"到"AI 在你仓库里干活"，亲手搭完每一块零件。

## 课程目标

学完之后你能做到：

1. 理解 LLM 的工作原理（next-token prediction、token、幻觉、工具补强）
2. 用 Python 流式调用 LLM、设计 prompt、估算 token
3. 实现工具注册系统 + Agent 主循环（Function Calling）
4. 区分并实现 ReAct、Plan-and-Solve、Reflection 三种 Agent 范式
5. 从零实现上下文管理与记忆系统
6. 搭建完整的 Coding Agent（9 个工具）
7. 整合所有模块，部署为 CNB 仓库 NPC

## 课程总览

| Day | 主题 | 核心产物 |
|-----|------|---------|
| 1 | [认识你的 AI](./day1-meet-your-ai/) | LLM 流式对话 + token 计算 |
| 2 | [Function Calling 与最小 Agent](./day2-tools-and-agent-loop/) | `ToolRegistry` + Agent Loop |
| 3 | [Agent 范式](./day3-agent-patterns/) | ReAct / Plan-and-Solve / Reflection |
| 4 | [上下文与记忆](./day4-context-and-memory/) | `ContextManager` + `Memory` |
| 5 | [Coding Agent 工具集](./day5-coding-agent-tools/) | 9 个工具实现 |
| 6 | [整合：完整 Coding Agent](./day6-coding-agent-integration/) | Day2-5 零件拼装 |
| 7 | [Skills 扩展 + NPC 上线](./day7-skills-and-npc/) | 自定义 Skills + 仓库 NPC |
| 8 | [总结 + 大作业](./day8-recap-and-final/) | 复盘与结课 |

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
├── day1-meet-your-ai/              # Day1：认识 AI
├── day2-tools-and-agent-loop/      # Day2：Function Calling + 最小 Agent
├── day3-agent-patterns/            # Day3：Agent 范式
├── day4-context-and-memory/        # Day4：上下文与记忆
├── day5-coding-agent-tools/        # Day5：Coding Agent 工具集
├── day6-coding-agent-integration/  # Day6：整合
├── day7-skills-and-npc/            # Day7：Skills + NPC
├── day8-recap-and-final/           # Day8：总结
├── examples/                       # 实践代码示例
│   ├── ch01-hello-react/           # ReAct 模式旅行助手
│   ├── ch02-hello-llm/            # 最小流式 LLM 客户端
│   ├── ch03-hello-agents/         # hello-agents 框架上手
│   └── ch04-my-agent/            # 从零搭建完整 Agent
└── docs/                          # 全局教学文档
```

## 与实践代码的对应关系

| 实践项目 | 课程映射 |
|---------|---------|
| `examples/ch02-hello-llm/` | Day1 |
| `examples/ch01-hello-react/` | Day3 ReAct 范式 |
| `examples/ch03-hello-agents/` | Day3 框架对照 |
| `examples/ch04-my-agent/tools/` | Day2 + Day5 |
| `examples/ch04-my-agent/context/` | Day4 |
| `examples/ch04-my-agent/memory/` | Day4 |
| `examples/ch04-my-agent/skills/` | Day7 |

## 环境准备

本课程使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境与依赖。

```bash
# 在仓库根目录执行一次，安装所有依赖
uv sync --all-packages
```

## 先修要求

- Python 基础（函数、类、字典、文件读写）
- 命令行基本使用（`cd` / `ls` / `cat` / 环境变量）
- 一台能联网的电脑

不需要提前会：Git、Docker、Agent、提示词工程——这些都是课程内容。
