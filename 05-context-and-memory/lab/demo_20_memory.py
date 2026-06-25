"""
Demo 20 · Memory：用 embedding API 做语义检索
============================================

配套：第 20 节《记忆系统：短期 / 长期 / 工作记忆》

Memory 与 ContextManager 的分工：
  - ContextManager：管理"本次对话的 messages 列表"（短期 + 工作记忆）
  - Memory：管理"跨会话持久化的事实库"（长期记忆）

本 demo 实现一个最小 Memory：
  ① add(text)         —— 调用 embedding API 编码文本，存入记忆库
  ② search(query, k)  —— 将查询也编码为向量，按余弦相似度返回 top-k

核心只用 numpy 计算余弦相似度，暂不引入向量数据库（先用最简方式把流程跑通，后续章节再换专业库）。

运行方式：
    source /workspace/.venv/bin/activate
    python demo_20_memory.py
"""

import json
from dataclasses import dataclass, field

import numpy as np

from _env import get_api_key, get_base_url, chat
from openai import OpenAI


# 单独建一个 client：embeddings 端点和 chat 端点共用同一组凭证
_emb_client = OpenAI(base_url=get_base_url(), api_key=get_api_key())

# 注意：模型名以你的 LLM gateway 实际暴露的为准
# CNB / 混元一般支持 hunyuan-embedding；OpenAI 兼容就用 text-embedding-3-small
EMBEDDING_MODEL = "hunyuan-embedding"


def embed(text: str) -> np.ndarray:
    """调用 embedding API 将文本转换为语义向量。

    通过 OpenAI 兼容的 embeddings 接口，将任意自然语言文本编码为
    一个固定维度的浮点向量。该向量捕捉了文本的语义信息，语义相近的
    文本在向量空间中距离更近（余弦相似度更高）。

    Args:
        text: 待编码的文本内容，长度不限（由 API 端点的上下文窗口决定）。

    Returns:
        np.ndarray: 形状为 `(d,)` 的 float32 向量，其中 `d` 是
        embedding 模型的输出维度（取决于具体模型，例如 768 或 1536）。

    Raises:
        openai.BadRequestError: 若文本过长或模型不支持。
        openai.APIError: 网络异常或服务端错误。

    Example:
        >>> v = embed("我喜欢喝拿铁。")
        >>> v.shape
        (768,)
        >>> v.dtype
        dtype('float32')
    """
    resp = _emb_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return np.array(resp.data[0].embedding, dtype=np.float32)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """计算两个向量之间的余弦相似度。

    余弦相似度衡量的是向量在方向上的接近程度，与向量的长度（模）无关。
    在 embedding 语义检索场景中，值越接近 1.0 表示两段文本语义越相似。

    计算公式：
        cos(a, b) = (a · b) / (|a| × |b|)

    其中 `a · b` 是向量点积，`|a|` 是 a 的模。

    分母加了 `1e-9` 防止零向量导致的除零错误。

    Args:
        a: 第一个向量，形状为 `(d,)` 的 float32 ndarray。
        b: 第二个向量，形状必须与 a 相同。

    Returns:
        float: 余弦相似度，范围 [-1.0, 1.0]。
        1.0 表示方向完全相同（语义完全一致），
        0 表示正交（无关），
        -1.0 表示方向完全相反（语义对立）。

    Example:
        >>> import numpy as np
        >>> a = np.array([1.0, 0.0], dtype=np.float32)
        >>> b = np.array([1.0, 0.0], dtype=np.float32)
        >>> cosine(a, b)
        1.0
        >>> c = np.array([0.0, 1.0], dtype=np.float32)
        >>> cosine(a, c)
        0.0
    """

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


# ============================================================
# 极简 Memory 实现
# ============================================================
@dataclass
class MemoryEntry:
    """一条长期记忆条目。

    用于 Memory 管理器的内部存储单元，包含原始文本、对应的向量编码
    以及可选的业务元数据。核心用途是为余弦相似度检索提供数据载体。

    Attributes:
        text: 记忆的原始文本内容。
        vec: 由 embedding API 生成的语义向量，类型为形状 (d,) 的 float32 数组，
            用于余弦相似度计算。
        meta: 附加元数据字典，由 add(..., **meta) 传入的任意键值对组成。
            可用于存储时间戳、来源、标签等辅助信息。

    Note:
        - vec 的类型是 `np.ndarray`（numpy 的多维数组），
          不是一个普通的 Python list 或 tuple，因此无法直接序列化到 JSON。
          持久化时通过 `.tolist()` 转为 Python 内置的 list 存入，
          还原时用 `np.array(list, dtype=np.float32)` 从 list 重建为 ndarray。
        - meta 默认空字典，避免多个实例共享同一个可变对象。
    """
    text: str
    vec: np.ndarray
    meta: dict = field(default_factory=dict)


class Memory:
    """基于向量的长期记忆管理器。

    在内存中维护一个记忆条目列表，通过 embedding API 将文本编码为向量，
    检索时用余弦相似度计算查询与每条记忆的匹配度，返回 top-k 最相关结果。

    设计原则：
        - 接口简洁：add / search / save / load 四个方法覆盖完整生命周期
        - 存储无关：当前使用内存 list + numpy，可无缝替换为 pgvector / qdrant / milvus
        - 读写分离：_entries 为私有属性，外部通过 entries 属性仅可读取不可变副本

    Examples:
        >>> mem = Memory()
        >>> mem.add("我喜欢喝拿铁。")
        >>> results = mem.search("用户的饮品偏好", k=2)
        >>> for score, entry in results:
        ...     print(f"[{score:.3f}] {entry.text}")
    """

    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    @property
    def entries(self) -> tuple[MemoryEntry, ...]:
        """只读属性：返回当前所有记忆条目的不可变拷贝。

        Returns:
            tuple[MemoryEntry, ...]: 所有记忆条目的元组，外部无法修改内部列表。

        Note:
            返回的是 tuple 而非 list，防止调用方直接 append / remove。
        """
        return tuple(self._entries)

    def add(self, text: str, **meta) -> None:
        """添加一条新记忆到记忆库中。

        自动调用 embedding API 将文本编码为向量，与原文及元数据一起存储。

        Args:
            text: 要存储的记忆文本内容。
            **meta: 可选的附加元数据，会存入 MemoryEntry.meta 字典中。

        Example:
            >>> mem.add("我每天预算 500 元。", category="budget", priority=1)
        """
        v = embed(text)
        self._entries.append(MemoryEntry(text=text, vec=v, meta=meta))

    def search(self, query: str, k: int = 3) -> list[tuple[float, MemoryEntry]]:
        """按语义相似度检索最相关的 top-k 条记忆。

        将查询文本编码为向量，与所有记忆的向量逐一计算余弦相似度，
        按相似度降序返回前 k 条。

        Args:
            query: 查询文本，任意自然语言描述。
            k: 返回的最大条目数量，默认为 3。

        Returns:
            list[tuple[float, MemoryEntry]]:
                按相似度从高到低排序的 (相似度分数, 记忆条目) 列表。
                相似度范围 [-1.0, 1.0]，越接近 1.0 表示语义越相关。
                若记忆库为空则返回空列表。

        Example:
            >>> results = mem.search("用户喜欢什么饮品", k=2)
            >>> for score, entry in results:
            ...     print(f"{score:.2f} | {entry.text}")
        """
        if not self._entries:
            return []
        q = embed(query)
        scored = [(cosine(q, e.vec), e) for e in self._entries]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]

    def save(self, path: str) -> None:
        """将当前所有记忆持久化到 JSON 文件。

        向量数据从 numpy array 转为 Python list 后存入 JSON，
        可通过 load() 完整还原。

        Args:
            path: JSON 文件的保存路径（含文件名）。

        Raises:
            IOError: 若文件写入失败（如路径不存在或权限不足）。

        Example:
            >>> mem.save("data/memory_backup.json")
        """
        data = [
            {"text": e.text, "vec": e.vec.tolist(), "meta": e.meta}
            for e in self._entries
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        """从 JSON 文件加载记忆，替换当前内存中的所有条目。

        将 JSON 中存储的 list 还原为 numpy array，恢复完整的 MemoryEntry 列表。

        Args:
            path: 由 save() 生成的 JSON 文件路径。

        Raises:
            FileNotFoundError: 若指定路径的文件不存在。
            json.JSONDecodeError: 若文件内容不是合法 JSON。

        Example:
            >>> mem.load("data/memory_backup.json")
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._entries = [
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
    """演示语义记忆的基本召回能力。

    本函数模拟一个典型的使用场景：用户提供了多条关于自身的个人事实（偏好、限制、
    计划等），系统将其逐条存入 Memory；随后用多个不同语义方向的查询进行检索，
    验证 embedding + 余弦相似度方案是否能将"语义上相关但措辞不同"的事实正确召回。

    工作流程：
        1. 创建一个空的 Memory 实例。
        2. 将 5 条中文用户事实调用 memory.add() 逐一存入，每条事实自动经
           embedding API 编码为语义向量。
        3. 用 4 个语义方向各异的查询（饮食偏好、健康限制、出行计划、金钱约束）
           分别调用 memory.search(query, k=2)，输出每条 top-2 匹配结果的
           相似度分数和原文。

    输出解读：
        - 每个查询打印一个 `[分数] 原文` 列表，分数为余弦相似度，范围 [-1.0, 1.0]，
          越接近 1.0 表示语义越匹配。
        - 观察分数可以帮助判断：哪些查询得到了高置信度匹配（分数 > 0.8），
          哪些查询因缺少相关记忆导致所有候选得分都偏低。
        - 例如，"用户的饮食喜好"应高分命中"我喜欢喝拿铁"；
          "金钱有没有约束"应高分命中"我每天预算 500 元"。

    Note:
        - 本函数仅打印结果，无返回值，也不做断言；用于教学演示而非自动化测试。
        - 实际 embedding 结果受模型版本影响，分数可能略有波动，但相对排序应保持稳定。
        - Memory.search() 的参数 k=2 表示只取相似度最高的前 2 条结果。

    Examples:
        >>> demo_basic_search()
    """
    print("=" * 60)
    print("【演示一：基本语义召回】")
    print("=" * 60)

    memory = Memory()
    facts = [
        "我对花粉过敏，户外活动需要避开花期。",
        "我每天预算 500 元。",
        "我喜欢喝拿铁，不喜欢美式。",
        "我下个月要去北京出差。",
        "我家里有一只 3 岁的橘猫，叫胖虎。",
    ]
    for f in facts:
        print(f"  + 添加: {f}")
        memory.add(f)

    queries = [
        "用户的饮食喜好是什么",
        "出行有没有什么健康限制",
        "用户最近会去哪里",
        "金钱方面有没有约束",
    ]

    for query in queries:
        print(f"\n查询: {query}")
        for score, e in memory.search(query, k=2):
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

    # 真去调一次 LLM（使用 stream 模式的 chat 封装，API 端点只支持流式）
    resp = chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    print("=== Agent 回答 ===")
    print(resp.content)
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
