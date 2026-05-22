# VibeCoding 课程体系（8 天 · Agent 主线版）

面向**大二学生**的 VibeCoding 课程，主线是**从零理解并搭出一个完整的 Coding Agent**。

## 一、课程目标

学完之后，每个学生能做到：

1. **理解 AI**：说清 LLM 为什么具备"智能"、token 是什么、幻觉从哪来、外部工具如何弥补 LLM 短板
2. **会调 LLM**：能用 Python 流式对话、估 token、设计 prompt
3. **会做 Agent**：理解 Function Calling 协议，能从零实现一个工具注册系统 + Agent 主循环
4. **懂 Agent 范式**：能区分并实现 ReAct、Plan-and-Solve、Reflection 三种范式，知道各自适用场景
5. **会管上下文与记忆**：能从零实现上下文管理类与记忆管理类，理解 token 预算与压缩策略
6. **会做 Coding Agent**：知道一个 Coding Agent 需要哪些工具、为什么，能逐个实现
7. **能整合并部署**：把零件整合成完整 Agent，扩展 Skills 系统，挂到 CNB 仓库做成 NPC

## 二、课程主线一句话

> **从"跟 AI 聊天"到"AI 在你仓库里干活"，亲手搭完每一块零件。**

## 三、课程总览

| Day | 主题 | 核心产物 |
|-----|------|---------|
| Day1 | 认识你的 AI | LLM 流式对话脚本 + token 计算工具 |
| Day2 | Function Calling 与最小 Agent | `ToolRegistry` + 最小 Agent Loop |
| Day3 | Agent 范式 | ReAct / Plan-and-Solve / Reflection 对照实现 |
| Day4 | 上下文与记忆 | `ContextManager` + `Memory` 两个独立模块 |
| Day5 | Coding Agent 工具集 | 9 个工具的完整实现 |
| Day6 | 整合：完整 Coding Agent | 把 Day2-5 拼起来，能干真活 |
| Day7 | Skills 扩展 + NPC 上线 | 自定义 Skills + 仓库 NPC |
| Day8 | 总结 + 大作业 | 结课展示与作业布置 |

每天 3.5 小时（210min），按"理论 + 实操"分块，**实操占比 ≥ 50%**。

## 四、Agent 零件建造路径

每天的产物都是下一天的零件：

```
Day1: LLM 客户端           ─┐
Day2: ToolRegistry         ─┤
Day3: 三种范式（选一种）    ─┤──→  Day6 整合成完整 Agent  ──→  Day7 加 Skills + 挂 NPC
Day4: ContextManager + Mem ─┤
Day5: Coding 工具集 × 9    ─┘
```

## 五、工程化的处理（Git / Docker / CNB）

本课程**不专门安排"工程化日"**，相关知识在恰当节穿插：

| 工程化技能 | 在哪天讲 | 时长 |
|-----------|---------|------|
| Git 基础（push / branch / PR） | Day5 实操开始前 | 30min |
| Docker（运行容器 + 写 Dockerfile） | Day7 NPC 准备阶段 | 30min |
| CNB Pipeline + NPC 配置 | Day7 NPC 实操 | 60min |

**只讲够用的子集**，不讲 rebase / 多阶段构建优化 / 镜像瘦身这些进阶内容。

## 六、目录结构

```
course/
├── README.md                        # 本文件
├── syllabus.md                      # 完整教学大纲（按节细化到分钟）
├── teaching-notes.md                # 教师须知
│
├── day1-meet-your-ai/               # Day1：认识 AI
├── day2-tools-and-agent-loop/       # Day2：Function Calling + 最小 Agent
├── day3-agent-patterns/             # Day3：Agent 范式
├── day4-context-and-memory/         # Day4：上下文与记忆
├── day5-coding-agent-tools/         # Day5：Coding Agent 工具集
├── day6-coding-agent-integration/   # Day6：整合
├── day7-skills-and-npc/             # Day7：Skills 扩展 + NPC
└── day8-recap-and-final/            # Day8：总结 + 大作业
```

每天目录结构统一：

```
dayN-xxx/
├── README.md            # 当日总览（学习目标 + 时间表 + 产物 + 检查点）
├── lecture/             # 讲义（理论部分逐节 md）
├── lab/                 # 实操指导（学生跟做）
└── exercises/           # 练习题
```

## 七、与已有代码的对应关系

仓库根目录已有 `ch01-ch04` 四个章节，是本课程的"参考实现"：

| 已有章节 | 课程映射 |
|---------|---------|
| `ch02-hello-llm/` | Day1 实操底稿 |
| `ch01-hello-react/` | Day2 / Day3 ReAct 范式参考 |
| `ch03-hello-agents/` | Day3 框架对照（选讲） |
| `ch04-my-agent/llm/` | Day1-2 |
| `ch04-my-agent/tools/` | Day2 ToolRegistry / Day5 工具集 |
| `ch04-my-agent/context/` | Day4 上下文管理 |
| `ch04-my-agent/memory/` | Day4 记忆管理 |
| `ch04-my-agent/skills/` | Day7 Skills |
| `ch04-my-agent/Dockerfile` + `npc-entrypoint.sh` | Day7 NPC 上线 |
| `docs/cnb-npc-setup.md` | Day7 NPC 操作手册 |
| `docs/vibe-guide.md` | 全程引导阅读 |

> **教学策略**：学生不直接读这些代码。每天的实操是让学生**从零 vibe 出来**，遇阻时教师拿已有章节做对照演示。

## 八、先修要求

- Python 基础（函数、类、字典、文件读写）
- 命令行基本使用（`cd` / `ls` / `cat` / 环境变量）
- 一台能联网的电脑

**不需要先会的**：Git、Docker、Agent、提示词工程——这些都是课程内容。

## 九、评估方式

每天有一个 **Checkpoint**，提交：
- 当日实操产物
- 100-200 字的"我今天学到了什么 + 卡在哪里"

**结课大作业**（Day8 布置）：
- 在自己仓库挂一个 NPC，能在 Issue 评论里 @ 它，让它自动完成一类真实任务
- 课后 1 周提交，含录屏 demo + 总结文档

---

> 详细教学大纲见 [`syllabus.md`](./syllabus.md)。
