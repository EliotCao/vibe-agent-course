"""极简上下文构建器 —— 实现 GSSC 流水线。

GSSC = Gather → Select → Structure → Compress

核心思想：在每次调用 LLM 前，以可控的方式拼装最优上下文。
"""

from dataclasses import dataclass, field
from datetime import datetime
from math import exp
from typing import Dict, List, Optional


@dataclass
class ContextPacket:
    """候选信息包：上下文构建的最小单元。"""

    content: str
    source: str = "user"  # user / system / memory / tool
    relevance: float = 0.5  # 相关性 0.0~1.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def token_count(self) -> int:
        """粗略估算 token 数：中文1字≈1token，英文1词≈1.3token。"""
        cn_chars = sum(1 for c in self.content if "\u4e00" <= c <= "\u9fff")
        en_words = len(self.content.split()) - cn_chars  # 近似
        return cn_chars + max(0, int(en_words * 1.3))


@dataclass
class ContextConfig:
    """上下文构建配置。"""

    max_tokens: int = 3000  # 总 token 预算
    reserve_ratio: float = 0.2  # 系统指令预留比例
    recency_weight: float = 0.3  # 新近性权重
    relevance_weight: float = 0.7  # 相关性权重
    min_relevance: float = 0.1  # 最低相关性阈值


class ContextBuilder:
    """极简上下文构建器，实现 GSSC 四阶段流水线。

    使用方式:
        builder = ContextBuilder(system_prompt="你是一个助手")
        builder.add("用户的历史对话", source="memory", relevance=0.6)
        builder.add("检索到的文档片段", source="tool", relevance=0.9)
        messages = builder.build(user_input="用户当前问题")
    """

    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant.",
        config: Optional[ContextConfig] = None,
    ):
        self.system_prompt = system_prompt
        self.config = config or ContextConfig()
        self._packets: List[ContextPacket] = []

    def add(
        self,
        content: str,
        source: str = "user",
        relevance: float = 0.5,
        timestamp: Optional[datetime] = None,
    ) -> "ContextBuilder":
        """添加一条候选信息包（支持链式调用）。"""
        packet = ContextPacket(
            content=content,
            source=source,
            relevance=relevance,
            timestamp=timestamp or datetime.now(),
        )
        self._packets.append(packet)
        return self

    def build(self, user_input: str) -> List[Dict[str, str]]:
        """执行 GSSC 流水线，输出最终 messages 列表。"""
        # 1. Gather —— 已通过 add() 汇集
        packets = self._packets.copy()

        # 2. Select —— 按综合分数排序，贪心填充
        selected = self._select(packets, user_input)

        # 3. Structure —— 组装为 messages 格式
        messages = self._structure(selected, user_input)

        # 4. Compress —— 确保不超预算（截断）
        messages = self._compress(messages)

        return messages

    def clear(self) -> None:
        """清空所有候选信息包。"""
        self._packets.clear()

    # ---- 内部方法 ----

    def _score(self, packet: ContextPacket, query: str) -> float:
        """计算综合分数 = 相关性权重×相关性 + 新近性权重×新近性。"""
        cfg = self.config

        # 相关性：使用简单的关键词重叠（Jaccard）
        relevance = self._keyword_relevance(packet.content, query)
        # 与预设的 relevance 取较高值
        relevance = max(relevance, packet.relevance)

        # 新近性：指数衰减，24h 内保持高分
        age_hours = (datetime.now() - packet.timestamp).total_seconds() / 3600
        recency = exp(-age_hours / 24)

        return cfg.relevance_weight * relevance + cfg.recency_weight * recency

    @staticmethod
    def _keyword_relevance(text: str, query: str) -> float:
        """基于关键词重叠的简易相关性（Jaccard 相似度）。"""
        text_tokens = set(text.lower().split())
        query_tokens = set(query.lower().split())
        if not query_tokens:
            return 0.0
        intersection = text_tokens & query_tokens
        union = text_tokens | query_tokens
        return len(intersection) / len(union) if union else 0.0

    def _select(
        self, packets: List[ContextPacket], query: str
    ) -> List[ContextPacket]:
        """贪心选择：按分数降序，直到填满 token 预算。"""
        cfg = self.config
        budget = int(cfg.max_tokens * (1 - cfg.reserve_ratio))

        # 计算分数并排序
        scored = [(p, self._score(p, query)) for p in packets]
        scored.sort(key=lambda x: x[1], reverse=True)

        selected: List[ContextPacket] = []
        used_tokens = 0
        for packet, score in scored:
            if score < cfg.min_relevance:
                continue
            if used_tokens + packet.token_count > budget:
                continue
            selected.append(packet)
            used_tokens += packet.token_count

        return selected

    def _structure(
        self, selected: List[ContextPacket], user_input: str
    ) -> List[Dict[str, str]]:
        """将选中的信息包组装成 OpenAI messages 格式。

        结构：
          [system]     系统提示 + 参考信息（tool/memory）
          [user]       历史用户消息
          [assistant]  历史助手回复
          ...          （user/assistant 交替）
          [user]       当前用户输入
        """
        messages: List[Dict[str, str]] = []

        # System prompt + 参考信息
        system_parts = [self.system_prompt]
        context_pieces = [p.content for p in selected if p.source in ("tool", "memory")]
        if context_pieces:
            system_parts.append("\n[参考信息]\n" + "\n---\n".join(context_pieces))

        messages.append({"role": "system", "content": "\n\n".join(system_parts)})

        # 历史对话：按时间排序，保持 user/assistant 交替
        history = [p for p in selected if p.source in ("user", "assistant")]
        history.sort(key=lambda p: p.timestamp)
        for p in history:
            role = "user" if p.source == "user" else "assistant"
            # 避免连续相同角色
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n" + p.content
            else:
                messages.append({"role": role, "content": p.content})

        # 当前用户输入（如果上一条也是 user，合并进去）
        if messages[-1]["role"] == "user":
            messages[-1]["content"] += "\n" + user_input
        else:
            messages.append({"role": "user", "content": user_input})

        return messages

    def _compress(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """简单压缩：如果总 token 超预算，从中间截断历史消息。"""
        total = sum(self._estimate_tokens(m["content"]) for m in messages)
        if total <= self.config.max_tokens:
            return messages

        # 保留首条 system 和末条 user，从中间删除
        while total > self.config.max_tokens and len(messages) > 2:
            removed = messages.pop(1)
            total -= self._estimate_tokens(removed["content"])

        return messages

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """粗略估算 token 数。"""
        cn_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        en_words = len(text.split()) - cn_chars
        return cn_chars + max(0, int(en_words * 1.3))
