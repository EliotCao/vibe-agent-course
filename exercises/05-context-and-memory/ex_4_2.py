"""
练习 4.2 · 向量记忆存取
========================

知识点：第 20 节《Memory 系统》

要求：补全 VectorMemory 类
  - add(text): 把文本转成向量存起来
  - search(query, k): 找出与 query 最相似的 k 条记忆

提示：
  - 用 OpenAI 兼容的 embedding API 生成向量
  - 余弦相似度 = dot(a, b) / (norm(a) * norm(b))
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../02-meet-your-ai/lab"))
from _env import make_client

client = make_client()


def get_embedding(text: str) -> list[float]:
    """调用 embedding API 获取向量（已实现，不用改）。"""
    resp = client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        input=text,
    )
    return resp.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算两个向量的余弦相似度。"""
    # TODO:
    #   1. 计算点积 dot = sum(x*y for x,y in zip(a,b))
    #   2. 计算 norm_a = sqrt(sum(x*x for x in a))
    #   3. 计算 norm_b = sqrt(sum(x*x for x in b))
    #   4. 返回 dot / (norm_a * norm_b)
    #   5. 注意边界：如果 norm 为 0，返回 0.0
    raise NotImplementedError("请补全此函数")


class VectorMemory:
    def __init__(self):
        self._entries: list[tuple[str, list[float]]] = []  # (text, embedding)

    def add(self, text: str) -> None:
        """存入一条记忆：文本 + 对应的向量。"""
        # TODO:
        #   1. 调用 get_embedding(text) 获取向量
        #   2. 把 (text, embedding) 追加到 self._entries
        raise NotImplementedError("请补全 add")

    def search(self, query: str, k: int = 3) -> list[tuple[float, str]]:
        """检索与 query 最相似的 k 条记忆。

        返回 [(similarity, text), ...] 按相似度降序排列。
        """
        # TODO:
        #   1. 调用 get_embedding(query) 获取查询向量
        #   2. 对 self._entries 中每条计算 cosine_similarity
        #   3. 按相似度降序排序
        #   4. 返回前 k 条 [(similarity, text), ...]
        raise NotImplementedError("请补全 search")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    mem = VectorMemory()

    # 存入几条记忆
    mem.add("用户喜欢吃辣，不吃鱼")
    mem.add("用户下周要去杭州出差")
    mem.add("用户的名字叫小李")
    mem.add("今天讨论了 Python 的列表推导式")
    mem.add("用户对花粉过敏")

    # 测试 1：相关查询
    results = mem.search("用户有什么饮食偏好？", k=2)
    assert len(results) == 2, f"应该返回 2 条，实际: {len(results)}"
    assert results[0][0] > results[1][0], "第一条相似度应该最高"
    # 最相关的应该包含"辣"或"鱼"
    assert "辣" in results[0][1] or "鱼" in results[0][1], (
        f"饮食偏好查询应该匹配到吃辣/不吃鱼，实际: {results[0][1]!r}"
    )

    # 测试 2：cosine_similarity 基本正确
    sim = cosine_similarity([1, 0, 0], [1, 0, 0])
    assert abs(sim - 1.0) < 0.001, f"相同向量相似度应该是 1，实际: {sim}"

    sim2 = cosine_similarity([1, 0], [0, 1])
    assert abs(sim2 - 0.0) < 0.001, f"正交向量相似度应该是 0，实际: {sim2}"

    # 测试 3：返回格式
    results2 = mem.search("过敏", k=1)
    assert isinstance(results2[0], tuple), "每条结果应该是 tuple"
    assert isinstance(results2[0][0], float), "第一个元素应该是 float (相似度)"
    assert isinstance(results2[0][1], str), "第二个元素应该是 str (文本)"

    print("✅ PASSED: VectorMemory 全部测试通过")
    print(f"   查询 '饮食偏好' top-2: {results}")
