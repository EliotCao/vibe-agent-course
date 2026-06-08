# 第 20 节 · 记忆系统：短期 / 长期 / 工作记忆

## 一句话回答

> **ContextManager 是"本次对话怎么压缩"，Memory 是"跨会话怎么记住事实并按需召回"。** 二者协作让 Agent 像人一样"既不爆窗也不忘事"。

## 三种记忆，分别管什么

![三类记忆](./images/20-memory-types.png)

| 记忆类型 | 长什么样 | 存活时间 | 谁管 |
|---|---|---|---|
| **短期记忆** | 本次对话的 messages 列表 | 对话结束就丢 | 第2章的循环 |
| **长期记忆** | 持久化的事实库（用户偏好 / 历史决策 / 项目规范） | 跨会话存活 | **Memory（今天主角）** |
| **工作记忆** | 当下任务用到的精挑信息 | 当前任务用完即弃 | ContextManager |

工业 Coding Agent（Cursor / Claude Code）这三种全用：
- 短期：本次会话的 chat history
- 工作：当前任务相关的代码片段、上次工具结果
- 长期：用户的常用风格 / 项目的代码规范 / Skills

## 长期记忆要解决什么问题

```
第 1 次会话：用户说"我对花粉过敏"
↓
第 2 次会话：用户说"帮我安排周末户外"
↓
理想结果：Agent 自动记起"过敏"这个事实，避开花季景点
现实结果（没有 Memory）：Agent 一无所知，推荐花海公园
```

**没有长期记忆 = 每次会话用户都得重复说自己。**

## 怎么实现：向量检索

最流行的长期记忆实现 = **向量数据库 + 余弦相似度**。

### 先简单提一下：关键词检索 vs 向量检索

这两条路都能"按问题查事实"，差别在**怎么判断相关**：

| | 关键词检索（BM25 / TF-IDF） | 向量检索（embedding + 余弦） |
|---|---|---|
| 怎么判断相关 | 看问题和事实**有几个相同的词** | 看问题和事实**语义有多近** |
| 例子 | 查"我有什么过敏症状"找不到"我对花粉敏感"（一个词都不重合） | 这两句嵌入后向量很近，能召回 |
| 优点 | 无需嵌入模型 / 零外部依赖 / 极快 | 处理同义、改写、跨语言都不怕 |
| 缺点 | "字面对不上"就崩 | 要调 embedding 接口，每次要钱 |
| 适合 | 关键词稳定的领域（API 文档、代码命名） | 自然语言对话、用户偏好 |

**今天 Memory 我们走向量检索这条路**——我们的主线就是用户偏好/对话事实，向量更合适。关键词法当 baseline 在 exercises 里留了一道延伸题（你也可以两条线混合，叫 hybrid retrieval，工业 RAG 的常见做法）。

---

![向量检索：把句子变成空间里的点](./images/20-vector-search.png)

### 三步走

#### 第 1 步：把每条事实"编码"成一个向量

```python
text = "用户对花粉过敏"
vector = embedding_model.embed(text)   # 一个 1536 维的向量
# [0.012, -0.034, 0.567, ..., 0.089]
```

这个向量是一个空间里的点。**语义相近的句子在空间里就近**。

> [!NOTE]
>
> **关于注释里的「1536 维向量」**
>
> "1536 维"不是抽象概念——`vector` 就是一个**长度为 1536 的 `list[float]`**，`len(vector) == 1536`。叫"维"是因为数学上每个数对应一根独立坐标轴：3 个数 → 三维空间里的一个点 (x, y, z)；1536 个数 → 1536 维空间里的一个点。
>
> 这个数字**不是随便选的，由 embedding 模型写死**：OpenAI `text-embedding-ada-002` / `text-embedding-3-small` 是 1536，`text-embedding-3-large` 是 3072，BGE-base / M3E-base 是 768，腾讯混元 `hunyuan-embedding` 是 1024 或 1536（看版本）。所以注释里的 1536 是举例，**实际跑起来 `len(vec)` 是多少，看你用哪个模型**。
>
> 几何含义就是后面整套向量检索的基石：embedding 模型的训练目标是**把语义相近的句子，编码到这个高维空间里靠近的位置**——人脑想象不了 1536 维，但"距离/夹角"的数学运算照样能做，这就是第 3 步用 `cosine` 算相似度的依据。
>
> 维度并非越高越好：维度高表达力强、召回质量好，但每条向量占 `4 × 1536 = 6KB`（float32），10 万条事实就是 600MB，余弦遍历也变慢——这是后面要引入向量数据库（FAISS / Milvus / Qdrant）的根本原因。



#### 第 2 步：所有事实都存成 (text, vector) 对

```python
memory = [
    ("用户对花粉过敏", vec_1),
    ("用户每天预算 500 元", vec_2),
    ("用户喜欢博物馆", vec_3),
    ...
]
```



#### 第 3 步：查询时

```python
query = "周末有没有什么健康限制"
q_vec = embedding_model.embed(query)

# 跟所有事实算余弦相似度
scores = [cosine(q_vec, v) for _, v in memory]

# 取分数最高的 top-k
top_k = sorted(zip(scores, memory), reverse=True)[:3]
# → [(0.78, "用户对花粉过敏"), (0.31, "用户喜欢博物馆"), ...]
```

最相关的事实分数最高，**就召回它**。



## Embedding 是什么 / 怎么调

Embedding 模型是一个**专门把文本变向量的小模型**，跟 chat 模型不是一回事。

```python
from openai import OpenAI

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

resp = client.embeddings.create(
    model="hunyuan-embedding",   # CNB 上是这个名字
    input="用户对花粉过敏",
)
vec = resp.data[0].embedding     # → [float] 长度 1024 或 1536
```

接口跟 chat completion 同一个 base_url + 同一个 API key，**只是端点是 `/embeddings`**。



### 余弦相似度怎么算

```python
import numpy as np

def cosine(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

返回值 [-1, 1]，**越接近 1 越相似**。一般 > 0.5 算"挺相关"，> 0.7 算"很相关"。

> [!NOTE]
>
> **为什么"越接近 1 越相似"**
>
> `cosine(a, b)` 算出来的就是两向量夹角 θ 的 `cos(θ)`：
>
> - 点积的几何定义 `a · b = |a| · |b| · cos(θ)`，分母 `|a| · |b|` 把长度约掉，**只剩方向**。（即 
> - 三角函数性质：θ ∈ [0°, 180°] 上 `cos(θ)` 单调递减——0° → 1（同向，最相似），90° → 0（垂直，无关），180° → -1（反向，最不相似）。
> - embedding 模型的训练目标就是把**语义相近的句子映射到方向相近的向量**。所以"夹角小 ↔ cos 大 ↔ 语义近"。
>
> 用一张二维示意图直观感受一下（箭头从原点出发）：
>
> ```text
>                  "用户对花粉过敏"
>                          ↗  ← 夹角很小，cos ≈ 0.95（语义近）
>                       ↗
>     query: "周末有  ↗
>     健康限制吗"   ●─────────────→  "用户喜欢逛博物馆"
>                    \              ↑ 夹角约 90°，cos ≈ 0.05（无关）
>                     \
>                      ↘
>                       ↘  ← 夹角接近 180°，cos ≈ -0.9（相反）
>                "用户讨厌一切户外活动"
> ```
>
> 同一个 query，跟三段记忆分别算余弦：方向越贴近，分数越高 → 召回时排第一。
>
> 阈值 0.5 / 0.7 是经验值：高维空间里完全无关的文本余弦也很少为 0（通常 0.0~0.3），同主题约 0.5~0.75，近义改写 0.85+。**换 embedding 模型阈值会平移**，工程上要抽样校准。
>



## 一个最小 Memory 类

```python
class Memory:
    def __init__(self):
        self.entries = []   # [(text, vector)]

    def add(self, text):
        self.entries.append((text, embed(text)))

    def search(self, query, k=3):
        q = embed(query)
        scored = [(cosine(q, v), t) for t, v in self.entries]
        scored.sort(reverse=True)
        return scored[:k]
```

**就这么简单**。`demo_20_memory.py` 完整版加了几个工程细节（持久化 / 元数据），核心还是这十行。

## 把 Memory 接到 Agent：两步

### 步骤 1：每轮对话开始前，召回相关事实

```python
def chat(user_input):
    relevant = memory.search(user_input, k=3)
    facts = [t for score, t in relevant if score > 0.5]
    
    system = f"{base_system_prompt}\n\n[相关长期事实]\n" + "\n".join(facts)
    return llm.chat([{"role": "system", "content": system}, ...])
```

**召回的事实塞进 system prompt** —— 模型自动"记得"这些事。

### 步骤 2：对话结束时，提炼新事实写回 Memory

```python
DISTILL_PROMPT = """从下面对话提炼**值得长期记的事实**，每行一条：
- 用户偏好
- 硬约束
- 重要事实
不要把一次性问答存进去。

对话：{transcript}
"""

new_facts = llm.chat(...)
for fact in new_facts.splitlines():
    memory.add(fact)
```

下次会话时，这些事实会自动被召回。

## 一个常见困惑：Memory 和 ContextManager 怎么协作？

```mermaid
flowchart TD
    Q[/"用户当前问题 query"/]

    MEM["<b>Memory：长期事实库（跨会话持久化）</b><br/>━━━━━━━━━━━━━━━<br/>· 用户过敏<br/>· 预算 500<br/>· 偏好博物馆<br/>· ……"]

    Q -->|"按 query 算余弦，召回 top-k"| MEM

    S["system ＋ 召回的长期事实"]
    H["近 N 轮对话原文"]
    U2["user 当前问题"]

    MEM -->|"relevant facts 拼进 system"| S
    S --> H --> U2

    U2 --> CM{"ContextManager<br/>本轮 messages<br/>长度超阈值？"}
    CM -->|"否：原样发出"| LLM
    CM -->|"是：压缩中间一段"| LLM[["调 LLM"]]

    classDef mem fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,color:#92400e
    classDef msg fill:#dbeafe,stroke:#3b82f6,stroke-width:1px,color:#1e40af
    classDef ctrl fill:#fce7f3,stroke:#ec4899,stroke-width:2px,color:#9d174d
    classDef llm fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    class MEM mem
    class S,H,U2 msg
    class CM ctrl
    class LLM llm
```

> [!NOTE]
>
> 色块说明：
>
> 1. 黄色：长期记忆 Memory
> 2. 蓝色三段：本轮 messages（短期/工作记忆）
> 3. 粉色：控制节点 ContextManager
> 4. 绿色：最终发给 LLM



**两件事的分工：**

- **Memory** 决定"哪些长期事实塞进来"
- **ContextManager** 决定"塞进来的本次 messages 怎么压"

## 工业版的进阶（今天不做）

| 进阶项 | 做什么 |
|---|---|
| 向量库 | 换成 pgvector / qdrant / milvus，量大时 numpy 算余弦慢 |
| Embedding 缓存 | 同一段文本不要 embed 两次（按 hash 缓存） |
| 阈值过滤 | 相似度 < 0.5 不召回，避免污染 prompt |
| 时间衰减 | 老记忆权重降低 |
| 混合检索 | 关键词 + 向量混合，关键词命中加权 |
| 用户分区 | 每个用户单独的命名空间，避免串号 |

第7章 / 第8章介绍工业级 Agent 时会再讨论这些。

## 动手试试

```bash
python demo_20_memory.py
```

会跑两个演示：
1. 基本召回：5 条事实，4 个查询，看相似度对不对
2. 注入对话：把 Memory 召回结果塞进 system 跑一次完整对话

## 小结

| 概念 | 一句话理解 |
|------|-----------|
| 短期 / 长期 / 工作记忆 | 三种存活时间不同的"记忆" |
| Memory | 长期记忆的实现，本质是向量数据库 |
| Embedding | 把文本变成向量的小模型 |
| 余弦相似度 | 衡量两个向量"语义有多近" |
| 用法 | 每轮按 query 召回 top-k 事实，塞 system；对话结束提炼新事实写回 |

---

理论部分到此结束。下面 lab：
- Part 1：写 ContextManager（分层策略）
- Part 2：写 Memory（向量检索）
- Part 3：拼成 Agent v2，对比第3章朴素版的 token 消耗
