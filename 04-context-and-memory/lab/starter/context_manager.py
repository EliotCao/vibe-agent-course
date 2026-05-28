"""
Day 4 Lab Part 1 · ContextManager 骨架 —— 填空

写一个 ContextManager 类，达到下面的能力：
  ① should_compress(messages): 判断是否需要压缩
  ② compress(messages): 用"分层策略"压缩

参考：第 19 节 + demos/demo_19_context_strategies.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from _env import get_model_id, make_client


# 用户硬约束的关键词（可以扩展）
KEY_FACT_KEYWORDS = ["过敏", "预算", "重要", "对了", "一定要", "不要"]


class ContextManager:
    def __init__(self, keep_last: int = 6, max_messages: int = 20) -> None:
        self.keep_last = keep_last
        self.max_messages = max_messages

    # ----------------------------------------------------------------
    # TODO ① 判断是否需要压缩
    # 简单做法：messages 条数超过 max_messages 就压缩
    # 进阶做法：估算 token 数（用 tiktoken 或 len(content) / 4 粗估）超过阈值就压缩
    # ----------------------------------------------------------------
    def should_compress(self, messages: list[dict]) -> bool:
        return False  # ← 你的代码

    # ----------------------------------------------------------------
    # TODO ② 关键事实抽取
    # 从 user 消息里捞出包含 KEY_FACT_KEYWORDS 的句子
    # ----------------------------------------------------------------
    def extract_key_facts(self, messages: list[dict]) -> list[str]:
        return []  # ← 你的代码

    # ----------------------------------------------------------------
    # TODO ③ 摘要生成（调一次 LLM）
    # 把"中间一段消息"压缩成一段中文摘要
    # ----------------------------------------------------------------
    def summarize(self, middle_messages: list[dict]) -> str:
        if not middle_messages:
            return ""
        client = make_client()
        # 拼一段 prompt 让 LLM 摘要，重点保留用户偏好/约束/关键事实
        return ""  # ← 你的代码

    # ----------------------------------------------------------------
    # TODO ④ 分层压缩
    # 输出顺序：[原始 system] + [关键事实] + [早期摘要] + [最近 N 轮]
    # ----------------------------------------------------------------
    def compress(self, messages: list[dict]) -> list[dict]:
        return messages  # ← 你的代码


# ============================================================
# 自测（跑通这段就过 Part 1）
# ============================================================
if __name__ == "__main__":
    # 构造一段假对话：第 3 条藏一个"过敏"硬约束
    messages = [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "我打算去北京"},
        {"role": "assistant", "content": "好的"},
        {"role": "user", "content": "重要：我对花粉过敏"},   # ⭐ 关键事实
        {"role": "assistant", "content": "明白"},
    ] + [
        m
        for i in range(20)
        for m in (
            {"role": "user", "content": f"问题 {i}"},
            {"role": "assistant", "content": f"回答 {i}"},
        )
    ] + [
        {"role": "user", "content": "总结一下我们说了什么"},
    ]

    ctx = ContextManager(keep_last=4, max_messages=15)
    print(f"原始: {len(messages)} 条")
    print(f"需要压缩? {ctx.should_compress(messages)}")
    print(f"关键事实: {ctx.extract_key_facts(messages)}")

    if ctx.should_compress(messages):
        compressed = ctx.compress(messages)
        print(f"\n压缩后: {len(compressed)} 条")
        for m in compressed:
            print(f"  [{m['role']}] {m['content'][:60]}")

        # 关键检查：'过敏' 还在不在
        text = " ".join(m["content"] for m in compressed)
        print(f"\n过敏事实保住了？ {'✅' if '过敏' in text else '❌'}")
