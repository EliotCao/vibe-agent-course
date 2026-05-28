"""
练习 1.2 · System Prompt 切换器
================================

知识点：第 2 节《提示词与角色：System / User / Assistant》

要求：补全 chat_with_system 函数
  - 输入：system_prompt（str）、user_message（str）
  - 输出：模型的回复文本（str）

提示：构造 messages 列表，包含 system 和 user 两条消息，调用 API
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../01-meet-your-ai/lab"))
from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def chat_with_system(system_prompt: str, user_message: str) -> str:
    """用指定的 system prompt 和 user 消息调用 LLM，返回回复文本。"""
    # TODO:
    #   1. 构造 messages 列表（两条：system + user）
    #   2. 调用 client.chat.completions.create(...)
    #   3. 返回 resp.choices[0].message.content
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：简洁模式 → 回复应该很短
    short_reply = chat_with_system(
        system_prompt="你只能用一个字回答任何问题。",
        user_message="今天天气好吗？",
    )
    assert len(short_reply) <= 10, f"期望极短回复，实际收到: {short_reply!r}"

    # 测试 2：翻译模式 → 回复应该包含英文
    translate_reply = chat_with_system(
        system_prompt="你是一个翻译机器，把用户说的中文翻译成英文，只输出英文。",
        user_message="你好",
    )
    # 翻译结果应该包含英文字母
    assert any(c.isascii() and c.isalpha() for c in translate_reply), (
        f"期望英文翻译，实际收到: {translate_reply!r}"
    )

    # 测试 3：函数应该返回字符串
    result = chat_with_system("你是助手。", "说一个字")
    assert isinstance(result, str), "返回值应该是字符串"
    assert len(result) > 0, "返回值不应该是空字符串"

    print("✅ PASSED: chat_with_system 全部测试通过")
