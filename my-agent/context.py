"""
Day4 产出：ContextManager
==========================

补全这个类，让 tests/test_context.py 全部通过。
"""

from __future__ import annotations

from llm import LLMClient


class ContextManager:
    def __init__(self, llm: LLMClient, max_tokens: int = 4000, keep_last: int = 4):
        # TODO: 保存 llm, max_tokens, keep_last
        raise NotImplementedError("请补全 __init__")

    def should_compress(self, messages: list[dict]) -> bool:
        """判断 messages 总 token 是否超过 max_tokens。"""
        # TODO: 统计所有 message.content 的 token 总和，与 max_tokens 比较
        raise NotImplementedError("请补全 should_compress")

    def compress(self, messages: list[dict]) -> list[dict]:
        """压缩 messages：保留 system + 最近 keep_last 条，中间部分摘要。"""
        # TODO:
        #   1. 如果不需要压缩，原样返回
        #   2. system = messages[0], recent = messages[-keep_last:]
        #   3. middle 部分让 LLM 生成摘要
        #   4. 返回 [system, summary_msg, *recent]
        raise NotImplementedError("请补全 compress")
