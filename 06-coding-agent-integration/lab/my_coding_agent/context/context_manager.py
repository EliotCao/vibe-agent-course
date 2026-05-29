"""ContextManager：分层策略 + 关键事实抽取（来自 第4章）。

把 第4章 demo_19 的 strategy_hierarchical 包成一个类。
跟 Memory 的区别再强调一遍：
- ContextManager：管"本次对话的 messages"（短期工作记忆）
- Memory：管"跨会话持久化事实"（长期记忆）
"""

from __future__ import annotations

from typing import Callable

KEY_FACT_KEYWORDS = ["过敏", "预算", "重要", "对了", "一定要", "不要", "记住", "禁止"]


def extract_key_facts(messages: list[dict]) -> list[str]:
    """从 user 消息里捞包含关键词的句子。"""
    facts: list[str] = []
    seen: set[str] = set()
    for m in messages:
        if m.get("role") != "user":
            continue
        text = m.get("content") or ""
        for kw in KEY_FACT_KEYWORDS:
            if kw in text and text not in seen:
                facts.append(text.strip())
                seen.add(text)
                break
    return facts


class ContextManager:
    """分层策略：[system] + [关键事实] + [早期摘要] + [最近 N 轮]。

    `summarize_fn` 接收一段 messages，返回一段中文摘要文本。
    传入的实现一般是"调一次 LLM 摘要"。
    """

    def __init__(
        self,
        keep_last: int = 10,
        max_messages: int = 30,
        summarize_fn: Callable[[list[dict]], str] | None = None,
    ):
        self.keep_last = keep_last
        self.max_messages = max_messages
        self.summarize_fn = summarize_fn

    def should_compress(self, messages: list[dict]) -> bool:
        return len(messages) > self.max_messages

    def compress(self, messages: list[dict]) -> list[dict]:
        sys_msgs = [m for m in messages if m.get("role") == "system"]
        non_sys = [m for m in messages if m.get("role") != "system"]
        if len(non_sys) <= self.keep_last:
            return messages

        middle = non_sys[: -self.keep_last]
        recent = non_sys[-self.keep_last :]

        # 1) 关键事实（独立提取，永远不丢）
        facts = extract_key_facts(messages)

        # 2) 早期摘要（可选）
        summary_msg = None
        if self.summarize_fn and middle:
            try:
                summary = self.summarize_fn(middle)
                if summary:
                    summary_msg = {
                        "role": "system",
                        "content": f"[早期对话摘要]\n{summary}",
                    }
            except Exception:
                summary_msg = None

        out: list[dict] = list(sys_msgs)
        if facts:
            fact_block = "\n".join(f"- {f}" for f in facts)
            out.append({"role": "system", "content": f"[关键事实，永远记住]\n{fact_block}"})
        if summary_msg:
            out.append(summary_msg)
        out.extend(recent)
        return out
