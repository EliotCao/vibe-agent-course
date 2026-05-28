# Day 4 · 实操：ContextManager + Memory + Agent v2

> 130 分钟 · 实操（第 21-23 节）

## 前提

已经看过 4 个 demo：
- `demo_18_context_explosion.py` —— 30 轮对话 token 怎么膨胀
- `demo_19_context_strategies.py` —— 4 种策略对比（截断 / 摘要 / 分层 / GSSC）
- `demo_20_memory.py` —— Memory 实现 + 向量检索
- `demo_21_agent_v2.py` —— 三件事拼起来

并且复用 Day2 / Day3 的 ToolRegistry + Agent Loop（不用重写）。

## 时间分配

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 5min | 看 starter 骨架，确认环境（embedding 端点能跑） |
| B | 50min | Part 1：填空 `context_manager.py`（分层策略） |
| C | 50min | Part 2：填空 `memory.py`（embedding + 余弦） |
| D | 25min | Part 3：填空 `agent_v2.py`，跑对比报告 |

## 当日产物

```
04-checkpoint/
├── context_manager.py     # 你填空补完的 ContextManager
├── memory.py              # 你填空补完的 Memory
├── agent_v2.py            # 把上面两个接到 Agent v2
├── comparison.md          # Day3 vs Day4 同任务的 token 消耗对比
└── reflection.md          # 100-200 字反思
```

---

## 阶段 A · 环境检查（5min）

### A.1 验证 embedding API 能跑

```bash
cd 04-context-and-memory/lab/demos
python -c "from _env import make_client, get_base_url, get_api_key
from openai import OpenAI
c = OpenAI(base_url=get_base_url(), api_key=get_api_key())
r = c.embeddings.create(model='hunyuan-embedding', input='测试')
print(f'OK，向量维度={len(r.data[0].embedding)}')
"
```

如果跑通看到向量维度（一般 1024 / 1536），说明环境对了。

### A.2 跑通 demo_18

```bash
python demo_18_context_explosion.py
```

让你切身感受**不做上下文管理时 token 飙升的速度**——后面要把这条曲线压回去。

---

## 阶段 B · Part 1：ContextManager（50min）<a id="part1"></a>

打开 [`starter/context_manager.py`](./starter/context_manager.py)，4 个 TODO：

| TODO | 难度 | 提示 |
|---|---|---|
| ① `should_compress` | 低 | 简单做法：消息条数超阈值就压；进阶：用 `len(content) // 4` 粗估 token |
| ② `extract_key_facts` | 中 | 关键词命中即提取，注意只查 user 消息 |
| ③ `summarize` | 中 | 调一次 LLM，prompt 里写"特别保留偏好/约束/事实" |
| ④ `compress` | 中 | 拼接顺序：[原 system] + [关键事实] + [早期摘要] + [最近 N 轮] |

### 动手 vibe（25min）

让你不要看 demo_19，自己用 AI 写：

```
帮我实现一个 ContextManager 类：
- should_compress(messages): 当 messages 条数 > 20 时返回 True
- extract_key_facts(messages): 从 user 消息里捞包含 "过敏 / 预算 / 重要" 关键词的句子
- summarize(messages): 调 LLM 把消息列表压缩成 100 字摘要，prompt 里特别强调"保留用户偏好和硬约束"
- compress(messages): 输出 [system + 关键事实 + 摘要 + 最近 6 轮]
```

跑自测脚本（starter 文件末尾就有），检查 **'过敏'** 这个早期事实在压缩后还在不在。

### 参考演示（15min）

参考实现 [`demos/demo_19_context_strategies.py`](./demos/demo_19_context_strategies.py)，重点对比：
- 你的 summarize prompt 有没有强调"保留偏好/约束"
- 你的 compress 顺序对不对（system 必须在最前）
- 关键事实抽取漏了没（关键词没覆盖的情况）

### 当堂练习（10min）

让你**故意把"过敏"换成"花生过敏"**测试一遍——能不能跨越压缩保住？

---

## 阶段 C · Part 2：Memory（50min）<a id="part2"></a>

打开 [`starter/memory.py`](./starter/memory.py)，4 个 TODO：

| TODO | 难度 | 提示 |
|---|---|---|
| ① `embed(text)` | 低 | 调 `_emb_client.embeddings.create(model=EMBEDDING_MODEL, input=text)`，取 `data[0].embedding` |
| ② `cosine(a, b)` | 低 | 一行：`np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))` |
| ③ `Memory.add` | 低 | 调 embed，append `MemoryEntry` |
| ④ `Memory.search` | 中 | 列表推导算余弦，sort 取 top-k |

### 动手 vibe（20min）

```
帮我实现一个最小 Memory 类：
- 用 OpenAI 兼容的 embeddings 接口（client.embeddings.create）
- 内存里 list 存所有 (text, vector)
- search(query, k) 用余弦相似度返回 top-k
```

跑自测，4 个查询都要召回对应事实，相似度 > 0.5。

### 参考演示（15min）

参考实现 [`demos/demo_20_memory.py`](./demos/demo_20_memory.py)，重点：
- embed() 的返回值类型（必须是 `np.ndarray` float32，否则后面计算慢）
- cosine() 的边界情况（向量全零时分母会爆）

### 当堂改造（15min）

加两个工程优化（任选一个）：
- **embedding 缓存**：相同 text 不要 embed 两次（用 dict 按 hash 缓存）
- **阈值过滤**：search 返回时只保留相似度 > 0.5 的

跑自测看效果。

---

## 阶段 D · Part 3：Agent v2 + 对比报告（25min）<a id="part3"></a>

### 25min 安排

| 时间 | 干什么 |
|---|---|
| 0-10min | 填空 `agent_v2.py`（2 个 TODO） |
| 10-20min | 跑对比测试：Day3 朴素 Agent vs Day4 v2 跑同 12 轮 |
| 20-25min | 写 `comparison.md` |

### Agent v2 填空（10min）

[`starter/agent_v2.py`](./starter/agent_v2.py)，2 个 TODO：

| TODO | 提示 |
|---|---|
| ① `chat(user_input)` | 召回 → 注入 system → 加 user → 检查压缩 → 调 LLM → 写回 messages |
| ② `distill_to_memory()` | 用 LLM 提炼"值得长期记的事实"，循环调 self.memory.add |

### 跑对比（10min）

跑你的 `agent_v2.py`，记录每一轮的 prompt_tokens；同时跑 Day3 朴素 Agent 跑同样 12 轮。

> **没有 Day3 朴素 Agent 怎么办？** 简单做法：把你的 v2 的 `chat()` 里"召回 / 压缩 / 提炼"全注释掉，就是 Day3 版。

### comparison.md 模板

```markdown
# Day3 vs Day4 同任务 token 对比

## 任务

12 轮旅行规划对话（详见 agent_v2.py 里的 questions）

## 数据

| 轮次 | Day3 prompt_tokens | Day4 v2 prompt_tokens | 节省 |
|---|---|---|---|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| ... | | | |
| 12 | ... | ... | ... |

## 关键观察

1. v2 在第 ___ 轮触发了第一次压缩
2. 召回事实在第 ___ 轮起作用（注入了"过敏"或"预算"事实）
3. Day3 在第 ___ 轮起 prompt 长度超过了 v2

## 一个意外发现

___（你跑出来的，最让你意外的一件事）___
```

---

## 阶段 E · 提交清单

```
04-checkpoint/
├── context_manager.py
├── memory.py
├── agent_v2.py
├── comparison.md
└── reflection.md
```

### 反思要求（reflection.md）

必须包含：
- ContextManager 的"分层策略"实现里，**最难写的是哪一段**？
- 你的 Memory 在 5 个测试事实 + 4 个查询里，有哪一对没有正确召回？为什么？
- 跑 v2 的 12 轮任务时，Memory 召回最让你意外的一次是哪个？
- 一个明天 Day5 你想看到的东西

---

## 助教检查重点

- [ ] `context_manager.py` 的 `compress` 输出顺序正确（system 在最前 / 关键事实在 system 之后 / 最近 N 轮在最末）
- [ ] `extract_key_facts` 真的从 user 消息里抽出来了（不是把 assistant 也算上）
- [ ] `memory.py` 的 embed 返回类型是 `np.ndarray`，不是 `list`
- [ ] `cosine` 处理了零向量边界（除 0 不会崩）
- [ ] `agent_v2.py` 的 `chat()` 真的同时做了"召回 + 压缩"两件事
- [ ] `comparison.md` 含 Day3 vs Day4 的真实数据，不是凭空编

---

## 参考资产（仅卡住时参考）

| 情况 | 投屏什么 |
|---|---|
| ContextManager 摘要 prompt 写得不好 | `demos/demo_19_context_strategies.py` 的 `strategy_summary` |
| Memory 召回不准 | `demos/demo_20_memory.py` + 检查 EMBEDDING_MODEL 名字对不对 |
| v2 没触发压缩 | `demos/demo_21_agent_v2.py` 的 `should_compress` |
| 想看工程级 GSSC | [`examples/04-my-agent/context/context_builder.py`](../../examples/04-my-agent/context/context_builder.py) |
| 想看工程级 Memory | [`examples/04-my-agent/memory/memory.py`](../../examples/04-my-agent/memory/memory.py) |
