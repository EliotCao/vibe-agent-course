"""极简上下文构建器 —— 实现 GSSC 流水线。

GSSC = Gather → Select → Structure → Compress

核心思想：在每次调用 LLM 前，以可控的方式拼装最优上下文。
支持普通对话和 Function Calling 两种消息格式。
"""

from dataclasses import dataclass, field
from datetime import datetime
from math import exp
from typing import Any, Dict, List, Optional


@dataclass
class ContextPacket:
    """候选信息包：上下文构建的最小单元。"""

    content: str
    source: str = "user"  # user / system / memory / tool / assistant
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
    keep_recent: int = 10  # 压缩时保留最近消息数


class ContextBuilder:
    """上下文构建器，实现 GSSC 四阶段流水线。

    支持两种使用模式：

    模式 A（普通对话）：
        builder = ContextBuilder(system_prompt="你是一个助手")
        builder.add("历史对话", source="memory", relevance=0.6)
        messages = builder.build(user_input="当前问题")

    模式 B（Function Calling）：
        builder = ContextBuilder(system_prompt="你是编程助手")
        builder.append({"role": "user", "content": "..."})
        builder.append({"role": "assistant", "tool_calls": [...]})
        builder.append({"role": "tool", "tool_call_id": "...", "content": "..."})
        messages = builder.get_messages()
    """

    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant.",
        config: Optional[ContextConfig] = None,
    ):
        self.system_prompt = system_prompt
        self.config = config or ContextConfig()
        self._packets: List[ContextPacket] = []
        # Function Calling 模式的完整消息列表
        self._messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    # ========== 模式 A：基于 ContextPacket 的 GSSC 流水线 ==========

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
        """执行 GSSC 流水线，输出最终 messages 列表（普通对话模式）。"""
        packets = self._packets.copy()
        selected = self._select(packets, user_input)
        messages = self._structure(selected, user_input)
        messages = self._compress_simple(messages)
        return messages

    # ========== 模式 B：Function Calling 消息管理 ==========

    def append(self, message: Dict[str, Any]) -> "ContextBuilder":
        """追加一条完整消息（支持 tool_calls、tool 等特殊格式）。"""
        self._messages.append(message)
        return self

    def get_messages(self) -> List[Dict[str, Any]]:
        """获取完整的 messages 列表（自动压缩如果超预算）。"""
        self._compress_messages()
        return self._messages.copy()

    def _compress_messages(self):
        """压缩 Function Calling 格式的对话历史。

        策略：保留 system（首条）+ 最近 N 条消息，中间部分生成摘要。
        注意保持 tool_calls 和 tool 的配对完整性。
        """
        total_tokens = self._estimate_messages_tokens(self._messages)
        budget = self.config.max_tokens

        if total_tokens < budget * 0.8:
            return  # 还没超预算

        keep_recent = self.config.keep_recent
        if len(self._messages) <= keep_recent + 1:
            return  # 消息太少，不压缩

        # 找到安全的分割点：不能切断 tool_calls 和 tool 的配对
        cut_end = len(self._messages) - keep_recent
        # 向后调整，确保不切断 tool/tool_calls 配对
        while cut_end < len(self._messages) and self._messages[cut_end].get("role") == "tool":
            cut_end += 1

        if cut_end >= len(self._messages) - 2:
            return  # 没有可压缩的空间

        # 提取被压缩部分的摘要
        middle = self._messages[1:cut_end]
        summary = self._summarize_messages(middle)

        # 重建：system + 摘要伪对话 + 最近消息
        self._messages = (
            [self._messages[0]]  # system
            + [
                {"role": "user", "content": f"[对话历史摘要]\n{summary}"},
                {"role": "assistant", "content": "好的，我已了解之前的对话内容，请继续。"},
            ]
            + self._messages[cut_end:]
        )

    @staticmethod
    def _summarize_messages(messages: List[Dict[str, Any]]) -> str:
        """将一组消息压缩为文本摘要。"""
        parts = []
        for m in messages:
            role = m.get("role", "")
            content = m.get("content", "") or ""
            if role == "user" and content:
                parts.append(f"- 用户: {content[:80]}")
            elif role == "assistant" and content:
                parts.append(f"- 助手: {content[:80]}")
            elif role == "tool" and content:
                parts.append(f"- 工具结果: {content[:60]}")
        # 只保留最近几条摘要
        return "\n".join(parts[-8:]) if parts else "（无历史）"

    def _estimate_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """估算一组 messages 的总 token 数。"""
        total = 0
        for m in messages:
            content = m.get("content", "") or ""
            total += self._estimate_tokens(content)
            # tool_calls 的 arguments 也占 token
            for tc in m.get("tool_calls", []):
                args = tc.get("function", {}).get("arguments", "")
                total += self._estimate_tokens(args)
        return total

    # ========== 通用方法 ==========

    def clear(self) -> None:
        """清空所有状态。"""
        self._packets.clear()
        self._messages = [{"role": "system", "content": self.system_prompt}]

    # ========== 内部方法（GSSC） ==========

    def _score(self, packet: ContextPacket, query: str) -> float:
        """计算综合分数 = 相关性权重×相关性 + 新近性权重×新近性。"""
        cfg = self.config
        relevance = packet.relevance
        age_hours = (datetime.now() - packet.timestamp).total_seconds() / 3600
        recency = exp(-age_hours / 24)
        return cfg.relevance_weight * relevance + cfg.recency_weight * recency

    def _select(
        self, packets: List[ContextPacket], query: str
    ) -> List[ContextPacket]:
        """贪心选择：在 token 预算内挑选价值最高的信息包。"""
        cfg = self.config
        budget = int(cfg.max_tokens * (1 - cfg.reserve_ratio))

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
        """将选中的信息包组装成 OpenAI messages 格式。"""
        messages: List[Dict[str, str]] = []

        # System prompt + 参考信息
        system_parts = [self.system_prompt]
        context_pieces = [p.content for p in selected if p.source in ("tool", "memory")]
        if context_pieces:
            system_parts.append("\n[参考信息]\n" + "\n---\n".join(context_pieces))
        messages.append({"role": "system", "content": "\n\n".join(system_parts)})

        # 历史对话：按时间排序
        history = [p for p in selected if p.source in ("user", "assistant")]
        history.sort(key=lambda p: p.timestamp)
        for p in history:
            role = "user" if p.source == "user" else "assistant"
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n" + p.content
            else:
                messages.append({"role": role, "content": p.content})

        # 当前用户输入
        if messages[-1]["role"] == "user":
            messages[-1]["content"] += "\n" + user_input
        else:
            messages.append({"role": "user", "content": user_input})

        return messages

    def _compress_simple(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """简单压缩（普通对话模式）：超预算时从中间截断。"""
        total = sum(self._estimate_tokens(m["content"]) for m in messages)
        if total <= self.config.max_tokens:
            return messages

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
