# Day 4 · 上下文与记忆

> 今天结束时，每个学生有一个 `ContextManager` 类和一个 `Memory` 类，能解决"上下文爆炸"和"跑完就忘"两个问题。

## 学习目标

- [ ] 能解释"上下文工程"是 Agent 工程的核心
- [ ] 区分 4 种上下文管理策略：截断 / 摘要 / 分层 / GSSC
- [ ] 区分短期记忆 / 长期记忆 / 工作记忆
- [ ] 能从零实现 `ContextManager`（含 token 预算 + 摘要压缩）
- [ ] 能从零实现 `Memory`（含简单向量检索）
- [ ] 能把它们接到 Day3 的 Agent 上

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 18 | 25min | 理论 | 上下文工程：为什么要管、什么时候爆 | [18-why-context-matters.md](./lecture/18-why-context-matters.md) |
| 19 | 30min | 理论 | 上下文管理策略：截断 / 摘要 / 分层 / GSSC | [19-context-strategies.md](./lecture/19-context-strategies.md) |
| 20 | 25min | 理论 | 记忆系统：短期 / 长期 / 工作记忆 | [20-memory-types.md](./lecture/20-memory-types.md) |
| 21 | 60min | 实操 | 实现 ContextManager 类 | [lab/part1](./lab/README.md#part1) |
| 22 | 50min | 实操 | 实现 Memory 类（含简单向量检索） | [lab/part2](./lab/README.md#part2) |
| 23 | 20min | 实操 | 把 Day3 的 Agent 接上 ContextManager + Memory | [lab/part3](./lab/README.md#part3) |

## 课前演示（开课前 5min 抛震撼）

把 Day3 的 Agent 跑一个 30 轮的复杂任务，让学生看着 token 消耗一路飙升，最后报错。

> "今天我们就是要解决这个问题。"

## 当日产物

```
day4/
├── context_manager.py     # 上下文管理类
├── memory.py              # 记忆类
└── agent_v2.py            # Day3 Agent 接上 Context + Memory
```

## Checkpoint

1. 三个产物文件
2. 一份对比报告：同样的 30 轮任务，Day3 版 vs Day4 版的 token 消耗曲线 + 最终输出质量
3. 100-200 字反思

## 教师演示备用

- `ch04-my-agent/context/context_builder.py` —— GSSC 流水线工程级实现
- `ch04-my-agent/memory/memory.py` —— Memory 实现
