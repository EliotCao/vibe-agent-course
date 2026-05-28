# Day 3 · Agent 范式

> 本章目标：理解三种主流 Agent 思考模式，实现 Agent 主循环。
> 产出：`my-agent/agent.py` — 你的 Agent 类。

## 你将学到

- ReAct：边想边做（Thought → Action → Observation 循环）
- Plan-and-Solve：先规划再执行
- Reflection：起草 → 评审 → 修订循环
- 三种范式的适用场景对比

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 12 | ReAct 范式 | [12-react.md](./lecture/12-react.md) | `demo_12_react.py` |
| 13 | Plan-and-Solve | [13-plan-and-solve.md](./lecture/13-plan-and-solve.md) | `demo_13_plan_and_solve.py` |
| 14 | Reflection | [14-reflection.md](./lecture/14-reflection.md) | `demo_14_reflection.py` |

## 运行 Demo

```bash
cd 03-agent-patterns/lab
python demo_12_react.py
python demo_13_plan_and_solve.py
python demo_14_reflection.py
```

## 今日产出

补全 [`my-agent/agent.py`](../my-agent/agent.py) 中的 `Agent` 类，让测试通过：

```bash
cd my-agent
python tests/test_agent.py
```

## 配套练习

[`exercises/03-agent-patterns/`](../exercises/03-agent-patterns/) — 3 道代码填空题
