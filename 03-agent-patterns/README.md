# 第 3 章 · Agent 范式

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
| 10 | ReAct 范式 | [10-react.md](./lecture/10-react.md) | `demo_10_react.py` |
| 11 | Plan-and-Solve | [11-plan-and-solve.md](./lecture/11-plan-and-solve.md) | `demo_11_plan_and_solve.py` |
| 12 | Reflection | [12-reflection.md](./lecture/12-reflection.md) | `demo_12_reflection.py` |

## 运行 Demo

```bash
cd 03-agent-patterns/lab
python demo_10_react.py
python demo_11_plan_and_solve.py
python demo_12_reflection.py
```

## 作业指引

本章作业在配套作业仓库中完成：

> 📦 **作业仓库**：<https://cnb.cool/opencamp/learning-agent/vibe-agent-exercise>

**流程**：Fork 作业仓库 → 在 `my-agent/`（核心产出）与 `exercises/`（配套填空）中完成本章任务 → 提交 PR，CI 流水线（`.cnb.yml`）自动测评，全绿即通过。

## 本章产出

在作业仓库中补全 `my-agent/agent.py` 的 `Agent` 类，让测试通过：

```bash
cd my-agent
python tests/test_agent.py
```

## 配套练习

作业仓库的 `exercises/03-agent-patterns/` — 3 道代码填空题（运行 `python exercises/03-agent-patterns/ex_*.py` 看到 ✅ PASSED 即通过）。
