"""
Day 4 Lab Part 2 · Memory 骨架 —— 学生填空

实现一个最小 Memory：
  - add(text)：调 embedding API 把文本变成向量存起来
  - search(query, k)：把 query 也 embed，按余弦相似度返回 top-k

参考：第 20 节 + demos/demo_20_memory.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from _env import get_api_key, get_base_url


# embedding 模型名 —— CNB 上是 hunyuan-embedding，OpenAI 兼容是 text-embedding-3-small
EMBEDDING_MODEL = "hunyuan-embedding"

_emb_client = OpenAI(base_url=get_base_url(), api_key=get_api_key())


# ----------------------------------------------------------------
# TODO ① 写 embed() 函数：调 embeddings 接口拿一条向量
# 返回 np.ndarray，dtype=float32
# ----------------------------------------------------------------
def embed(text: str) -> np.ndarray:
    return np.zeros(1536, dtype=np.float32)  # ← 你的代码


# ----------------------------------------------------------------
# TODO ② 写余弦相似度
# cosine(a, b) = a·b / (|a| |b|)
# ----------------------------------------------------------------
def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return 0.0  # ← 你的代码


@dataclass
class MemoryEntry:
    text: str
    vec: np.ndarray
    meta: dict = field(default_factory=dict)


class Memory:
    def __init__(self) -> None:
        self.entries: list[MemoryEntry] = []

    # ----------------------------------------------------------------
    # TODO ③ add：embed text 然后 append 一条 entry
    # ----------------------------------------------------------------
    def add(self, text: str, **meta) -> None:
        pass  # ← 你的代码

    # ----------------------------------------------------------------
    # TODO ④ search：embed query → 跟所有 entries 做余弦相似度 → 取 top-k
    # 返回 [(score, entry), ...]，从高到低排序
    # ----------------------------------------------------------------
    def search(self, query: str, k: int = 3) -> list[tuple[float, MemoryEntry]]:
        return []  # ← 你的代码


# ============================================================
# 自测：5 条记忆 + 4 个查询，看相似度对不对
# ============================================================
if __name__ == "__main__":
    mem = Memory()
    facts = [
        "我对花粉过敏，户外活动需要避开花期。",
        "我每天预算 500 元。",
        "我喜欢喝拿铁，不喜欢美式。",
        "我下个月要去北京出差。",
        "我家里有一只 3 岁的橘猫，叫胖虎。",
    ]
    for f in facts:
        mem.add(f)

    queries = [
        "用户的饮食喜好是什么",        # 应该召回 "拿铁"
        "出行有没有什么健康限制",      # 应该召回 "过敏"
        "用户最近会去哪里",            # 应该召回 "北京"
        "金钱方面有没有约束",          # 应该召回 "预算"
    ]

    print(f"\n{'='*60}\n基础召回测试\n{'='*60}")
    for q in queries:
        print(f"\n查询: {q}")
        for score, e in mem.search(q, k=2):
            print(f"  [{score:.3f}] {e.text}")

    print(f"\n💡 自检：4 个查询都召回了对应事实吗？相似度都 > 0.5 吗？")
