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
| 2 | Function Calling 与最小 Agent | `ToolRegistry` + Agent Loop |
| 3 | Agent 范式 | ReAct / Plan-and-Solve / Reflection |
| 4 | 上下文与记忆 | `ContextManager` + `Memory` |
| 5 | Coding Agent 工具集 | 9 个工具实现 |
| 6 | 整合：完整 Coding Agent | Day2-5 零件拼装 |
| 7 | Skills 扩展 + NPC 上线 | 自定义 Skills + 仓库 NPC |
| 8 | 总结 + 大作业 | 复盘与结课 |

## 零件建造路径

每天的产物都是下一天的零件：

```
Day1: LLM 客户端           ─┐
Day2: ToolRegistry         ─┤
Day3: 三种范式（选一种）    ─┤──→  Day6 整合成完整 Agent  ──→  Day7 加 Skills + 挂 NPC
Day4: ContextManager + Mem ─┤
Day5: Coding 工具集 × 9    ─┘
```

## 各天详细内容

### Day 1 · 认识你的 AI

| 节 | 主题 | 类型 |
|----|------|------|
| 1 | LLM 为什么具备智能：从概率预测到涌现 | 理论 |
| 2 | 提示词与角色：System / User / Assistant | 理论 |
| 3 | Token、上下文窗口、token 怎么算 | 理论 |
| 4 | 大模型幻觉：从哪来、怎么识别、怎么缓解 | 理论 |
| 5 | LLM 智能 + 外部支持：为什么需要工具与上下文 | 理论 |
| 6 | 实操：调用 LLM API + 流式输出 + token 计数 | 实操 |

### Day 2 · Function Calling 与最小 Agent

| 节 | 主题 | 类型 |
|----|------|------|
| 7 | Agent vs Chatbot：为什么需要循环 | 理论 |
| 8 | Function Calling 协议：Tool Schema 与消息流 | 理论 |
| 9 | 最小 Agent Loop 的 5 个核心点 | 理论 |
| 10 | 实操：实现 ToolRegistry | 实操 |
| 11 | 实操：搭最小 Agent Loop + 接 3 个工具 | 实操 |

### Day 3 · Agent 范式

| 节 | 主题 | 类型 |
|----|------|------|
| 12 | ReAct：Thought-Action-Observation 循环 | 理论 |
| 13 | Plan-and-Solve：先规划再执行 | 理论 |
| 14 | Reflection：自我反思与修正 | 理论 |
| 15-17 | 实操：三种范式实现 + 横向对比 | 实操 |

### Day 4 · 上下文与记忆

| 节 | 主题 | 类型 |
|----|------|------|
| 18 | 上下文工程：为什么要管、什么时候爆 | 理论 |
| 19 | 上下文管理策略：截断 / 摘要 / 分层 | 理论 |
| 20 | 记忆系统：短期 / 长期 / 工作记忆 | 理论 |
| 21-23 | 实操：ContextManager + Memory 实现与集成 | 实操 |

### Day 5 · Coding Agent 工具集

| 节 | 主题 | 类型 |
|----|------|------|
| 24 | Coding Agent 工作模式：浏览-定位-理解-修改-验证 | 理论 |
| 25 | 9 个工具的设计哲学 | 理论 |
| 26-27 | 实操：实现读类工具 + 写类工具 | 实操 |

工具清单：`read` / `write` / `edit` / `list` / `glob` / `grep` / `bash` / `todo` / `webfetch`

### Day 6 · 整合：完整 Coding Agent

把 Day2-5 的零件拼成一个能干真活的完整 Agent，在真实任务上验证。

### Day 7 · Skills 扩展 + NPC 上线

- Skills 系统：让 Agent 学会团队规范
- Docker 打包 + CNB Pipeline 配置
- 把 Agent 挂到仓库做成 NPC

### Day 8 · 总结 + 大作业

复盘全链路 + 行业图景（Cursor / Claude Code / Devin 对比）+ 布置结课大作业。

## 目录结构

```
course/
├── README.md                        # 本文件
├── pyproject.toml                   # 依赖管理
├── day1-meet-your-ai/              # Day1：认识 AI
├── day2-tools-and-agent-loop/      # Day2：Function Calling + 最小 Agent
├── day3-agent-patterns/            # Day3：Agent 范式
├── day4-context-and-memory/        # Day4：上下文与记忆
├── day5-coding-agent-tools/        # Day5：Coding Agent 工具集
├── day6-coding-agent-integration/  # Day6：整合
├── day7-skills-and-npc/            # Day7：Skills + NPC
└── day8-recap-and-final/           # Day8：总结
```

## 与已有代码的对应关系

| 已有章节 | 课程映射 |
|---------|---------|
| `ch02-hello-llm/` | Day1 |
| `ch01-hello-react/` | Day3 ReAct 范式 |
| `ch03-hello-agents/` | Day3 框架对照 |
| `ch04-my-agent/tools/` | Day2 + Day5 |
| `ch04-my-agent/context/` | Day4 |
| `ch04-my-agent/memory/` | Day4 |
| `ch04-my-agent/skills/` | Day7 |

## 先修要求

- Python 基础（函数、类、字典、文件读写）
- 命令行基本使用（`cd` / `ls` / `cat` / 环境变量）
- 一台能联网的电脑

不需要提前会：Git、Docker、Agent、提示词工程——这些都是课程内容。
