"""
练习 4.3 · 上下文管理决策器
============================

知识点：第 18-19 节《上下文管理》

要求：补全 should_compress 函数
  - 输入：messages 列表 + token 阈值
  - 输出：bool — 是否需要压缩

关键：用 tiktoken 统计 messages 的总 token 数，超过阈值就返回 True。
"""

import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")


def count_messages_tokens(messages: list[dict]) -> int:
    """统计 messages 列表的总 token 数。"""
    # TODO:
    #   1. 遍历每条消息
    #   2. 对每条消息的 content 调 ENC.encode() 统计 token 数
    #   3. 每条消息额外加 4 token（role、格式开销的近似值）
    #   4. 返回总数
    #
    # 注意：content 可能是 None（比如 assistant 的 tool_calls 消息），跳过即可
    raise NotImplementedError("请补全此函数")


def should_compress(messages: list[dict], threshold: int = 2000) -> bool:
    """判断 messages 是否需要压缩。

    当总 token 数 > threshold 时返回 True。
    """
    # TODO: 调用 count_messages_tokens，跟 threshold 比较
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 短对话 → 不需要压缩
    short_messages = [
        {"role": "system", "content": "你是助手"},
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
    ]
    assert should_compress(short_messages, threshold=2000) is False, "短对话不需要压缩"

    # 长对话 → 需要压缩
    long_messages = [{"role": "system", "content": "你是助手"}]
    for i in range(50):
        long_messages.append({"role": "user", "content": f"这是第 {i} 轮对话，我想聊聊关于人工智能的一些有趣话题，比如大模型的工作原理。"})
        long_messages.append({"role": "assistant", "content": f"好的，关于第 {i} 个话题，人工智能的大模型是通过海量数据训练出来的，核心是 Transformer 架构和注意力机制。"})
    assert should_compress(long_messages, threshold=2000) is True, "50 轮对话应该超过 2000 token"

    # count_messages_tokens 基本正确
    tokens = count_messages_tokens(short_messages)
    assert isinstance(tokens, int), "应该返回整数"
    assert 10 < tokens < 100, f"短对话 token 数应该在 10-100 之间，实际: {tokens}"

    # 阈值边界
    assert should_compress(short_messages, threshold=5) is True, "阈值极小时应该需要压缩"
    assert should_compress(short_messages, threshold=99999) is False, "阈值极大时不需要压缩"

    # None content 不崩
    messages_with_none = [
        {"role": "system", "content": "test"},
        {"role": "assistant", "content": None},
        {"role": "user", "content": "hello"},
    ]
    tokens2 = count_messages_tokens(messages_with_none)
    assert isinstance(tokens2, int), "content=None 时不应该崩"

    print("✅ PASSED: should_compress 全部测试通过")
    print(f"   短对话: {count_messages_tokens(short_messages)} tokens")
    print(f"   长对话: {count_messages_tokens(long_messages)} tokens")
