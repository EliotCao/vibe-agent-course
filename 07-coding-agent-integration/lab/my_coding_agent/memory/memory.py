"""Memory：embedding + 余弦相似度的最小向量记忆（来自 第4章）。

整合时新增两件小事：
- 持久化：save() / load() 到 JSON
- 阈值过滤：search 默认相似度 > 0.5 才返回

跟 第4章 的 demo_20_memory.py 接口完全兼容。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import numpy as np

from _env import get_api_key, get_base_url


# 单独的 OpenAI 客户端（embedding 端点跟 chat 共用同一组凭证）
def _make_emb_client():
    from openai import OpenAI
    return OpenAI(base_url=get_base_url(), api_key=get_api_key())


EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "hunyuan-embedding")


def embed(text: str) -> np.ndarray:
    client = _make_emb_client()
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype=np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    return float(np.dot(a, b) / denom)


@dataclass
class MemoryEntry:
    text: str
    vec: np.ndarray
    meta: dict = field(default_factory=dict)


class Memory:
    """最小可用 Memory：内存里 list + 余弦相似度 + JSON 持久化。

    `min_score` 用来在 search 阶段剪掉不相关的结果。
    """

    def __init__(self, min_score: float = 0.5):
        self.entries: list[MemoryEntry] = []
        self.min_score = min_score
        # 简单 dedup：相同 text 不重复存
        self._seen: set[str] = set()

    def __len__(self) -> int:
        return len(self.entries)

    def add(self, text: str, **meta) -> None:
        if not text or text in self._seen:
            return
        v = embed(text)
        self.entries.append(MemoryEntry(text=text, vec=v, meta=meta))
        self._seen.add(text)

    def search(self, query: str, k: int = 3) -> list[tuple[float, MemoryEntry]]:
        if not self.entries:
            return []
        q = embed(query)
        scored = [(cosine(q, e.vec), e) for e in self.entries]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(s, e) for s, e in scored[:k] if s >= self.min_score]

    # ---------- 持久化 ----------
    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data = [
            {"text": e.text, "vec": e.vec.tolist(), "meta": e.meta}
            for e in self.entries
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        if not os.path.isfile(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.entries = []
        self._seen = set()
        for d in data:
            self.entries.append(
                MemoryEntry(
                    text=d["text"],
                    vec=np.array(d["vec"], dtype=np.float32),
                    meta=d.get("meta", {}),
                )
            )
            self._seen.add(d["text"])
