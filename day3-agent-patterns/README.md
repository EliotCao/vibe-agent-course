# Day 3 · Agent 范式：ReAct / Plan-and-Solve / Reflection

> 今天结束时，每个学生有 3 个版本的 Agent，跑过同样 5 个任务，能讲出每种范式的优缺点。

## 学习目标

- [ ] 能画出 ReAct 的 Thought-Action-Observation 循环
- [ ] 能画出 Plan-and-Solve 的 Planner → Executor 流程
- [ ] 能解释 Reflection 是怎么"自我修正"的
- [ ] 能基于 Day2 的 Agent 实现这 3 种范式
- [ ] 能根据任务类型推荐合适的范式

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 12 | 30min | 理论 | ReAct：Thought-Action-Observation 循环 | [12-react.md](./lecture/12-react.md) |
| 13 | 25min | 理论 | Plan-and-Solve：先规划再执行 | [13-plan-and-solve.md](./lecture/13-plan-and-solve.md) |
| 14 | 25min | 理论 | Reflection：让 Agent 自我反思与修正 | [14-reflection.md](./lecture/14-reflection.md) |
| 15 | 50min | 实操 | 把 Day2 的 Agent 改成 ReAct 版 | [lab/part1](./lab/README.md#part1) |
| 16 | 50min | 实操 | 实现 Plan-and-Solve 版（Planner + Executor）| [lab/part2](./lab/README.md#part2) |
| 17 | 30min | 实操 | 给 Agent 加 Reflection 步骤 + 三种范式横向对比 | [lab/part3](./lab/README.md#part3) |

## 当日产物

```
day3/
├── agent_react.py         # ReAct 版（基于 prompt 解析）
├── agent_plan_solve.py    # 先 plan 再逐步 solve
├── agent_reflection.py    # Reflection 包装层
└── comparison.md          # 三种范式跑同 5 个任务的结果对比
```

## Checkpoint

1. 三个 Agent 文件
2. `comparison.md` 含至少 5 个任务的对比表（成功率 / 步数 / token 消耗 / 答案质量）
3. 一段你的"该选哪种"的判断指南
4. 100-200 字反思

## 教师演示备用

- `ch01-hello-react/agent.py` —— 标准 ReAct
- `ch03-hello-agents/main.py` —— 看 patch_react_agent_logging_and_parser，演示 ReAct 解析的脆弱性

## 教师准备

为了节省时间，老师**提前准备 3 份"半成品代码"**，学生在框架上填空：
- `agent_react_skeleton.py`：主循环写好，Thought/Action 解析留 TODO
- `agent_plan_solve_skeleton.py`：Planner / Executor 类骨架，prompt 留 TODO
- `agent_reflection_skeleton.py`：Reflection 包装层骨架
