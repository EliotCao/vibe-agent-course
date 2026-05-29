"""
第4章产出：Memory
==================

补全这个类，让 tests/test_memory.py 全部通过。
"""

from __future__ import annotations

import json
import math
import os

from llm import LLMClient


class Memory:
    def __init__(self, llm: LLMClient):
        self._entries: list[tuple[str, list[float]]] = []
        self._llm = llm

    def _get_embedding(self, text: str) -> list[float]:
        """获取文本的向量表示。"""
        # TODO: 调用 embedding API
        #   from openai import OpenAI  (或复用 llm.client)
        #   resp = client.embeddings.create(model=..., input=text)
        #   return resp.data[0].embedding
        raise NotImplementedError("请补全 _get_embedding")

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """余弦相似度。"""
        # TODO: dot / (norm_a * norm_b)
        raise NotImplementedError("请补全 _cosine_similarity")

    def add(self, text: str) -> None:
        """存入一条记忆。"""
        # TODO: embedding = self._get_embedding(text), 追加到 self._entries
        raise NotImplementedError("请补全 add")

    def search(self, query: str, k: int = 3) -> list[tuple[float, str]]:
        """检索最相关的 k 条，返回 [(similarity, text), ...]。"""
        # TODO: 对 query 做 embedding，遍历 _entries 算相似度，排序取 top-k
        raise NotImplementedError("请补全 search")

    def save(self, path: str) -> None:
        """持久化到 JSON 文件。"""
        # TODO: json.dump self._entries 到 path
        raise NotImplementedError("请补全 save")

    def load(self, path: str) -> None:
        """从 JSON 文件加载。"""
        # TODO: json.load 并赋值给 self._entries
        raise NotImplementedError("请补全 load")
