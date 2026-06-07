# 第 4 章 · 上下文与记忆

> 本章目标：解决"聊久了爆炸"和"下次忘了"两个问题。
> 产出：`my-agent/context.py` + `my-agent/memory.py`。

## 你将学到

- 为什么上下文会爆炸（token 线性增长）
- 上下文管理策略：keep_last + 摘要压缩
- 向量记忆：embedding + 余弦相似度检索
- Agent v2：接入 Context + Memory

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 18 | 为什么要管上下文 | [18-why-context-matters.md](./lecture/18-why-context-matters.md) | `demo_18_context_explosion.py` |
| 19 | 上下文管理策略 | [19-context-strategies.md](./lecture/19-context-strategies.md) | `demo_19_context_strategies.py` |
| 20 | Memory 系统 | [20-memory-types.md](./lecture/20-memory-types.md) | `demo_20_memory.py` |
| 21 | Agent v2（整合） | — | `demo_21_agent_v2.py` |

## 运行 Demo

```bash
cd 05-context-and-memory/lab
python demo_18_context_explosion.py
python demo_19_context_strategies.py
python demo_20_memory.py
python demo_21_agent_v2.py
```

## 本章产出

补全 [`my-agent/context.py`](../my-agent/context.py) 和 [`my-agent/memory.py`](../my-agent/memory.py)，让测试通过：

```bash
cd my-agent
python tests/test_context.py
python tests/test_memory.py
```

## 配套练习

[`exercises/05-context-and-memory/`](../exercises/05-context-and-memory/) — 3 道代码填空题
