"""
练习 4.1 · 上下文压缩器
========================

知识点：第 19 节《上下文管理策略》

要求：补全 compress_messages 函数
  - 输入：messages 列表（保留 system + 最近 keep_last 条）+ 要压缩的中间部分
  - 输出：压缩后的新 messages 列表（system + 摘要消息 + 最近 keep_last 条）

压缩思路：把中间部分让 LLM 生成一段摘要，替换原来的多条消息。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../02-meet-your-ai/lab"))
from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def compress_messages(messages: list[dict], keep_last: int = 4) -> list[dict]:
    """压缩 messages 列表：保留 system + 最近 keep_last 条，中间部分用摘要替换。

    返回压缩后的新 messages 列表。
    """
    # 如果消息不够多，不需要压缩
    if len(messages) <= keep_last + 2:
        return messages[:]

    system = messages[0]  # system 消息永远保留
    recent = messages[-keep_last:]  # 最近 keep_last 条保留
    middle = messages[1:-keep_last]  # 中间部分需要压缩

    # TODO:
    #   1. 把 middle 里的消息拼成一段文本（格式如 "user: ...\nassistant: ...\n"）
    #   2. 让 LLM 生成摘要：
    #      system prompt: "请把下面的对话摘要成 2-3 句话，保留关键事实和用户偏好。"
    #      user message: 拼好的对话文本
    #   3. 构造新的 messages 列表：
    #      [system, {"role": "assistant", "content": f"[对话摘要] {summary}"}, *recent]
    #   4. 返回新列表
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 构造一段长对话
    messages = [
        {"role": "system", "content": "你是一个旅行助手。"},
        {"role": "user", "content": "我想去杭州玩"},
        {"role": "assistant", "content": "杭州很不错！你喜欢什么类型的景点？"},
        {"role": "user", "content": "我喜欢自然风景，不喜欢人太多的地方"},
        {"role": "assistant", "content": "推荐九溪烟树和龙井茶园，人少风景好。"},
        {"role": "user", "content": "我对茶过敏，换一个"},
        {"role": "assistant", "content": "那推荐西溪湿地，自然风光很棒。"},
        {"role": "user", "content": "好的，帮我查一下明天天气"},
        {"role": "assistant", "content": "杭州明天多云，25度，适合出行。"},
    ]

    # 压缩（保留最近 4 条）
    compressed = compress_messages(messages, keep_last=4)

    # 测试 1：长度减少
    assert len(compressed) < len(messages), (
        f"压缩后应该更短: 原 {len(messages)} 条 → 现 {len(compressed)} 条"
    )

    # 测试 2：system 消息保留
    assert compressed[0]["role"] == "system", "第一条应该还是 system"
    assert "旅行" in compressed[0]["content"], "system 内容不应该变"

    # 测试 3：最近的消息保留
    assert compressed[-1]["content"] == messages[-1]["content"], "最后一条消息应该保留原样"
    assert compressed[-2]["content"] == messages[-2]["content"], "倒数第二条也应该保留"

    # 测试 4：中间有摘要
    summary_msg = compressed[1]
    assert "摘要" in summary_msg["content"] or len(summary_msg["content"]) > 5, (
        f"应该有摘要内容，实际: {summary_msg['content']!r}"
    )

    print(f"✅ PASSED: compress_messages 测试通过")
    print(f"   原始: {len(messages)} 条 → 压缩后: {len(compressed)} 条")
    print(f"   摘要: {compressed[1]['content'][:80]}...")
