# Day 3 · Agent 范式：ReAct / Plan-and-Solve / Reflection

> 今天结束时，你有 3 个版本的 Agent，跑过同样 5 个任务，能讲清每种范式的适用场景与代价。

## 你将学到

- ReAct 的 Thought-Action-Observation 循环（含 prompt 解析的脆弱性）
- Plan-and-Solve 的 Planner / Executor / Aggregator 三段架构
- Reflection 包装层：起草 → 自评 → 修订
- 三种范式的横向对比 + 选型指南
- 如何在 Day2 的最小 Agent Loop 之上**装上不同的"驾驶模式"**

## 内容结构

| 节 | 类型 | 内容 | 讲义 | Demo |
|----|------|------|------|------|
| 12 | 理论 · 30min | ReAct：Thought-Action-Observation | [12-react.md](./lecture/12-react.md) | `demo_12_react.py` |
| 13 | 理论 · 25min | Plan-and-Solve：先规划再执行 | [13-plan-and-solve.md](./lecture/13-plan-and-solve.md) | `demo_13_plan_and_solve.py` |
| 14 | 理论 · 25min | Reflection：自我反思与修正 | [14-reflection.md](./lecture/14-reflection.md) | `demo_14_reflection.py` |
| 15-17 | 实操 · 130min | 填空补完三个范式 + 横向对比 | [lab/README.md](./lab/README.md) | 参考 `lab/demo_12/13/14` |

## 配套 Demo

所有 demo 在 `lab/` 目录下：

```bash
cd lab/demos
python demo_12_react.py            # ReAct（prompt + 正则）跑 5 个任务
python demo_13_plan_and_solve.py   # Plan-and-Solve 跑 5 个任务
python demo_14_reflection.py       # Reflection（套在 Plan-and-Solve 外）跑 3 个任务
```

> `toy_agent_base.py` 是公共底座：内置 ToolRegistry（来自 Day2）+ 4 个 mock 工具 + 5 个统一测试任务。三个 demo 全部 import 同一份，保证横向对比 apple-to-apple。

## 当日产物

lab 提交的目录：

```
03-checkpoint/
├── agent_react.py           # 你填空补完的 ReAct（基于 prompt + 正则）
├── agent_plan_solve.py      # 你填空补完的 Plan-and-Solve（含 Executor 复用 Day2）
├── agent_reflection.py      # 你填空补完的 Reflection 包装层
├── comparison.md            # 5 个任务三种范式对比表 + 选型指南
└── reflection.md            # 100-200 字反思
```

## Checkpoint

1. **三个 Agent 文件**：每个都能跑通 5 个任务（任务 5"故意刁难"不要求答对，但要看 Agent 怎么反应）
2. **`comparison.md`**：5 个任务 × 3 种范式的对比表，含每个任务的步数 / token 消耗 / 是否答对 / 答案质量
3. **选型指南**：根据对比结果，写一段你的"什么任务该选哪种范式"
4. **100-200 字反思**：详见 [lab/README.md → 反思要求](./lab/README.md#反思要求reflectionmd)

## 跟 Day1 / Day2 / Day4 的衔接

| 来自 Day2 | 今天怎么用 |
|---|---|
| ToolRegistry + 4 工具 | 今天**所有**范式共用同一套（`toy_agent_base.py`）|
| 最小 Agent Loop（tool_calls 协议） | Plan-and-Solve 的 Executor 直接复用 |
| messages 协议 / 4 角色 | 三种范式都基于 messages 拼接，差别只在 prompt 怎么写、循环怎么组织 |

| 今天产出 | Day4 / Day5 / Day6 怎么用 |
|---|---|
| 三种范式 | Day6 整合时**选一种**作为你 Coding Agent 的主驾驶模式 |
| Reflection 包装层 | Day5 给 Coding Agent 的写代码任务套上 Reflection 显著提质 |
| `comparison.md` 的选型指南 | Day8 大作业里你要在自己的 Agent 里**自圆其说**为什么选某种范式 |

## 参考实现（参考资产）

| 资产 | 用途 |
|---|---|
| [`examples/01-hello-react/agent.py`](../examples/01-hello-react/agent.py) | 标准 ReAct 100 行参考实现，含截断兜底 |
| [`examples/03-hello-agents/main.py`](../examples/03-hello-agents/main.py) | hello-agents 框架 ReAct 用法 + 一段 `patch_react_agent_logging_and_parser` 演示工业版的 fallback 之多 |
| [`examples/04-my-agent/agent/agent.py`](../examples/04-my-agent/agent/agent.py) | 工程级 `SimpleAgent` + `ReActAgent` 双范式实现 |

## 准备清单

| 项 | 说明 |
|---|---|
| 课前 | 跑通三个 demo（demo_12 / 13 / 14），确认你的环境能跑 5 个任务全过 |
| 阶段 B（ReAct 填空） | 准备一份"模型不规矩输出"的截图看一下，引导他们感受脆弱性 |
| 阶段 C（PS 填空） | 提醒**复用 Day2 的最小 Agent Loop**，不要重写 |
| 阶段 D（Reflection + 对比） | 准备好 token 计数小工具（在 demo 里就能加 `usage.total_tokens` 累加），减少踩坑 |

## 课后练习题

详见 [exercises/README.md](../exercises/03-agent-patterns/README.md)：

- 必做 3 题：ReAct 健壮性压测 / Plan-and-Solve 加 Replan / 范式自动选择器
- 选做 2 题：ReAct + Function Calling 混合（工业最常用） / 双模型 Reflection
