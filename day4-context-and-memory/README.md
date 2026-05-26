# Day 4 · 上下文与记忆

> 今天结束时，你有一个 `ContextManager` 类（管本次对话怎么压缩）和一个 `Memory` 类（管跨会话事实库），并把它们接到 Day3 的 Agent 上变成 v2。

## 你将学到

- 上下文工程为什么是 Agent 工程的核心（30 轮对话 token 怎么膨胀）
- 4 种上下文管理策略：截断 / 摘要 / 分层 / GSSC，各自的优缺点
- 三种记忆：短期（messages）/ 长期（Memory）/ 工作记忆（ContextManager）
- 用 OpenAI 兼容的 `embeddings` 接口 + 余弦相似度实现最小向量检索
- 把 ContextManager + Memory 接到 Agent 上，跨会话"记得"用户

## 内容结构

| 节 | 类型 | 内容 | 讲义 | Demo |
|----|------|------|------|------|
| 18 | 理论 · 25min | 上下文工程：为什么要管、什么时候爆 | [18-why-context-matters.md](./lecture/18-why-context-matters.md) | `demo_18_context_explosion.py` |
| 19 | 理论 · 30min | 4 种上下文管理策略：截断 / 摘要 / 分层 / GSSC | [19-context-strategies.md](./lecture/19-context-strategies.md) | `demo_19_context_strategies.py` |
| 20 | 理论 · 25min | 记忆系统：短期 / 长期 / 工作记忆 + 向量检索 | [20-memory-types.md](./lecture/20-memory-types.md) | `demo_20_memory.py` |
| 21-23 | 实操 · 130min | 三件零件 + 拼成 v2 + 跑对比 | [lab/README.md](./lab/README.md) | `lab/starter/*.py` |

## 配套 Demo

```bash
cd lab/demos
python demo_18_context_explosion.py        # 跑 20 轮看 token 飙升
python demo_19_context_strategies.py       # 4 种策略横向对比
python demo_20_memory.py                   # Memory 实现 + 注入对话演示
python demo_21_agent_v2.py                 # 三件事拼成 v2 跑 12 轮
```

## 当日产物

```
day4-checkpoint/
├── context_manager.py      # 你写的 ContextManager（分层策略）
├── memory.py               # 你写的 Memory（embedding + 余弦）
├── agent_v2.py             # Day3 Agent 接上 ContextManager + Memory
├── comparison.md           # Day3 vs Day4 同任务的 token 消耗对比
└── reflection.md           # 100-200 字反思
```

## Checkpoint

1. **三个产物文件**，跑通各自的自测脚本
2. **`comparison.md`**：同 12 轮对话 Day3 vs Day4 v2 的 prompt_tokens 对比表 + 关键事实保住情况
3. **跨越 30 轮的"过敏"事实保住了** —— 这是分层策略的最小成功标准
4. **100-200 字反思**：详见 [lab/README.md → 反思要求](./lab/README.md#反思要求reflectionmd)

## 跟 Day1-3 / Day5-6 的衔接

| 来自前几天 | 今天怎么用 |
|---|---|
| Day1 第 3 节 token 概念 | 今天直接用 `usage.prompt_tokens` 量化压缩效果 |
| Day1 第 3 节 Lost in the Middle | 解释为什么"窗口大也要管" |
| Day2 ToolRegistry | 不变，v2 仍然带工具调用 |
| Day3 Agent Loop（任一范式）| v2 在 Loop 外面套 ContextManager + Memory，循环本身不动 |

| 今天产出 | Day5 / Day6 / Day7 怎么用 |
|---|---|
| `ContextManager` | Day5 `read_file` 会返回大文件，必须靠 ContextManager 压；Day6 整合时是 Agent 类的核心字段 |
| `Memory` | Day7 Skills 系统底层就是同一套向量检索机制 |
| `agent_v2` 结构 | Day6 整合后的 `my_coding_agent/` 直接对应到这个结构 |

## 一个重要的实现选择

**Memory 用 embedding API + cosine 实现**（不是 BM25 / TF-IDF）：
- 优点：语义相近的句子自动召回，不依赖关键词
- 代价：每次 `add` 和 `search` 都要调一次 embedding 端点
- 工业版：Day7/8 介绍 pgvector / qdrant / milvus 时再换

CNB 平台的 embedding 模型名是 `hunyuan-embedding`，跟 chat 端点共用同一个 base_url + API key。

## 参考实现

| 资产 | 用途 |
|---|---|
| [`examples/ch04-my-agent/context/context_builder.py`](../examples/ch04-my-agent/context/context_builder.py) | 工程级 GSSC 流水线 ContextBuilder |
| [`examples/ch04-my-agent/memory/memory.py`](../examples/ch04-my-agent/memory/memory.py) | 工程级 Memory 实现 |

> 这两份比今天教的复杂得多（多源 / 缓存 / 去重 / 元数据 / 持久化）。**今天先掌握极简版，Day7/8 再迭代。**

## 课后练习题

详见 [exercises/README.md](./exercises/README.md)：
- 必做 3 题：关键事实漏抓的代价 / Memory 阈值调优 / 跨会话记忆验证
- 选做 2 题：摘要质量评估 / SQLite + sqlite-vec 持久化升级
