"""
Demo 20 · Memory：用 embedding API 做语义检索
============================================

配套：第 20 节《记忆系统：短期 / 长期 / 工作记忆》

Memory 跟 ContextManager 的区别：
  - ContextManager：管"本次对话的 messages 列表"（短期工作记忆）
  - Memory：管"跨会话持久化的事实库"（长期记忆）

本 demo 实现一个最小 Memory：
  ① add(text)         —— 把一条记忆调 embedding API 存进去
  ② search(query, k)  —— 把 query 也 embed，按余弦相似度返回 top-k

用纯 numpy 算余弦相似度，不引入向量数据库（learn first，库以后再换）。

跑法：
    python demo_20_memory.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import numpy as np

from _env import get_api_key, get_base_url
from openai import OpenAI


# 单独建一个 client：embeddings 端点和 chat 端点共用同一组凭证
_emb_client = OpenAI(base_url=get_base_url(), api_key=get_api_key())

# 注意：模型名以你的 LLM gateway 实际暴露的为准
# CNB / 混元一般支持 hunyuan-embedding；OpenAI 兼容就用 text-embedding-3-small
EMBEDDING_MODEL = "hunyuan-embedding"


def embed(text: str) -> np.ndarray:
    """把一段文本调 embedding 接口，返回单条向量。"""
    resp = _emb_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype=np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """余弦相似度，范围 [-1, 1]，越接近 1 越相似。"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


# ============================================================
# 极简 Memory 实现
# ============================================================
@dataclass
class MemoryEntry:
    text: str
    vec: np.ndarray
    meta: dict = field(default_factory=dict)


class Memory:
    """最小可用 Memory：内存里 list + 余弦相似度。

    生产环境换成 pgvector / qdrant / milvus，接口保持不变。
    """

    def __init__(self) -> None:
        self.entries: list[MemoryEntry] = []

    def add(self, text: str, **meta) -> None:
        v = embed(text)
        self.entries.append(MemoryEntry(text=text, vec=v, meta=meta))

    def search(self, query: str, k: int = 3) -> list[tuple[float, MemoryEntry]]:
        """返回 (相似度, entry) 列表，从高到低排序。"""
        if not self.entries:
            return []
        q = embed(query)
        scored = [(cosine(q, e.vec), e) for e in self.entries]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]

    def save(self, path: str) -> None:
        """把记忆持久化到 JSON（vec 转成 list 存）。"""
        data = [
            {"text": e.text, "vec": e.vec.tolist(), "meta": e.meta}
            for e in self.entries
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.entries = [
            MemoryEntry(
                text=d["text"],
                vec=np.array(d["vec"], dtype=np.float32),
                meta=d.get("meta", {}),
            )
            for d in data
        ]


# ============================================================
# 演示一：基本召回
# ============================================================
def demo_basic_search() -> None:
    print("=" * 60)
    print("【演示一：基本语义召回】")
    print("=" * 60)

    mem = Memory()
    facts = [
        "我对花粉过敏，户外活动需要避开花期。",
        "我每天预算 500 元。",
        "我喜欢喝拿铁，不喜欢美式。",
        "我下个月要去北京出差。",
        "我家里有一只 3 岁的橘猫，叫胖虎。",
    ]
    for f in facts:
        print(f"  + 添加: {f}")
        mem.add(f)

    queries = [
        "用户的饮食喜好是什么",
        "出行有没有什么健康限制",
        "用户最近会去哪里",
        "金钱方面有没有约束",
    ]

    for q in queries:
        print(f"\n查询: {q}")
        for score, e in mem.search(q, k=2):
            print(f"  [{score:.3f}] {e.text}")


# ============================================================
# 演示二：跟 ContextManager 集成（用 Memory 拿"长期事实"塞进 system）
# ============================================================
def demo_with_context_injection() -> None:
    print("\n\n" + "=" * 60)
    print("【演示二：Memory 召回结果注入到当前对话的 system】")
    print("=" * 60)

    # 先存几条"用户的长期偏好"
    mem = Memory()
    user_facts = [
        "用户每天预算 500 元。",
        "用户对花粉过敏，户外活动需要避开花期。",
        "用户喜欢咖啡，不喜欢甜食。",
        "用户在北京工作，家在朝阳区。",
        "用户上次反馈：博物馆类景点很喜欢。",
    ]
    for f in user_facts:
        mem.add(f)

    # 这次用户问的问题
    question = "帮我安排周末两天的活动。"
    print(f"\n用户问: {question}")

    # 用问题去 Memory 检索 top-3 相关事实
    relevant = mem.search(question, k=3)
    print(f"\n召回的相关长期事实：")
    for score, e in relevant:
        print(f"  [{score:.3f}] {e.text}")

    # 把这些事实注入到 system prompt
    facts_block = "\n".join(f"- {e.text}" for _, e in relevant)
    system_prompt = (
        "你是用户的助手。下面是用户的长期偏好和约束，请在回答中遵守：\n"
        + facts_block
    )

    print(f"\n=== 注入后的 system prompt ===")
    print(system_prompt)
    print()

    # 真去调一次 LLM
    from _env import get_model_id, make_client

    client = make_client()
    resp = client.chat.completions.create(
        model=get_model_id(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
        max_tokens=400,
    )
    print("=== Agent 回答 ===")
    print(resp.choices[0].message.content)
    print()
    print("👀 观察回答里有没有体现：预算 500、避花粉、博物馆偏好。")


if __name__ == "__main__":
    demo_basic_search()
    demo_with_context_injection()

    print("\n\n" + "=" * 60)
    print("🎯 关键认识")
    print("=" * 60)
    print("  1. Memory 不是 messages 列表，是一个'按语义可搜索'的事实库")
    print("  2. 检索 = 把 query embed → 跟所有记忆做余弦相似度 → top-k")
    print("  3. 用法：每轮对话开始前用当前 question 去 Memory 召回相关事实")
    print("           塞到 system prompt 里 → 模型自动'有了记忆'")
    print()
    print("  生产环境优化：")
    print("    - 向量库：换成 pgvector / qdrant，量大时 numpy 算余弦会慢")
    print("    - 缓存 embedding：相同文本不要 embed 两次")
    print("    - 阈值过滤：相似度低于 0.6 的不召回，避免污染 prompt")
