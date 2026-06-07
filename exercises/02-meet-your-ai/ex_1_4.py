"""
练习 1.4 · 流式输出收集器
==========================

知识点：第 1 节（LLM 逐 token 生成）+ 第 3 节（token 计费）

要求：补全 stream_collect 函数
  - 输入：user_message（str）
  - 输出：(full_text, token_count) — 完整回复文本 + 本次消耗的总 token 数

提示：
  - 使用 stream=True + stream_options={"include_usage": True}
  - 逐 chunk 收集 delta.content
  - 最后一个 chunk 的 chunk.usage 里有总 token 数
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../02-meet-your-ai/lab"))
from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def stream_collect(user_message: str) -> tuple[str, int]:
    """流式调用 LLM，返回 (完整回复文本, 总 token 数)。"""
    # TODO:
    #   1. 调用 client.chat.completions.create(
    #        model=MODEL,
    #        messages=[{"role": "user", "content": user_message}],
    #        stream=True,
    #        stream_options={"include_usage": True},
    #      )
    #   2. 遍历 response 的每个 chunk：
    #      - 如果 chunk.choices 且 delta.content 不为空 → 累加到 pieces 列表
    #      - 如果 chunk.usage 不为空 → 记录 usage.total_tokens
    #   3. 返回 ("".join(pieces), total_tokens)
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    text, tokens = stream_collect("用一句话介绍 Python 语言")

    # 基本类型检查
    assert isinstance(text, str), "第一个返回值应该是字符串"
    assert isinstance(tokens, int), "第二个返回值应该是整数"

    # 内容检查
    assert len(text) > 5, f"回复太短了: {text!r}"
    assert "python" in text.lower() or "Python" in text, "回复应该提到 Python"

    # token 检查
    assert tokens > 0, "token 数应该大于 0"
    assert tokens < 10000, "一句话回答不应该超过 10000 token"

    print(f"✅ PASSED: stream_collect 测试通过")
    print(f"   回复: {text[:50]}...")
    print(f"   总 token: {tokens}")
