"""
练习 1.1 · Token 计数器
========================

知识点：第 3 节《Token、上下文窗口与成本》

要求：补全 count_tokens 函数
  - 输入：任意字符串
  - 输出：该字符串的 token 数（使用 cl100k_base 编码器）

提示：用 tiktoken 库
"""

import tiktoken


def count_tokens(text: str) -> int:
    """返回 text 的 token 数量（使用 cl100k_base 编码器）。"""
    # TODO: 用 tiktoken 获取编码器，encode 文本，返回长度
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 基本测试
    assert count_tokens("Hello") > 0, "token 数应该大于 0"
    assert count_tokens("Hello, world!") < 10, "英文短句不应该超过 10 token"

    # 中文比英文"贵"
    en_tokens = count_tokens("Today is a good day.")
    zh_tokens = count_tokens("今天是个好日子。")
    assert zh_tokens >= en_tokens, "同义中文通常 token 数 ≥ 英文"

    # 空字符串
    assert count_tokens("") == 0, "空字符串应该是 0 token"

    # emoji
    emoji_tokens = count_tokens("🤖")
    assert emoji_tokens >= 1, "emoji 至少 1 token"

    print("✅ PASSED: count_tokens 全部测试通过")
