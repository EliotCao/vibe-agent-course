"""
练习 3.3 · Reflection 评审循环
================================

知识点：第 14 节《Reflection 范式》

要求：补全 reflect_and_revise 函数
  - 输入：task（任务描述）
  - 输出：最终修订后的文本

流程：
  1. 起草：让 LLM 写一个初稿
  2. 评审：让 LLM 扮演评审员，找出问题并判断是否通过
  3. 如果没通过 → 让 LLM 修订 → 再评审 → 循环
  4. 通过或达到 max_rounds → 返回最终版本
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../01-meet-your-ai/lab"))
from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def draft(task: str) -> str:
    """让 LLM 生成初稿（已实现，不用改）。"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个写作助手，根据任务要求写一段内容。"},
            {"role": "user", "content": task},
        ],
        max_tokens=500,
    )
    return resp.choices[0].message.content


def review(task: str, content: str) -> tuple[bool, str]:
    """让 LLM 评审内容，返回 (是否通过, 评审意见)。

    要求模型第一行回复 PASS 或 FAIL，后面是具体意见。
    """
    # TODO:
    #   1. 构造 system prompt：你是严格的评审员
    #   2. user message 包含原始任务 + 待评审内容
    #   3. 要求模型第一行只写 PASS 或 FAIL，第二行开始写具体意见
    #   4. 解析返回：第一行是否包含 "PASS" → passed = True/False
    #   5. 返回 (passed, feedback_text)
    raise NotImplementedError("请补全此函数")


def revise(task: str, content: str, feedback: str) -> str:
    """根据评审意见修订内容。"""
    # TODO:
    #   1. 构造 prompt：把任务、当前内容、评审意见都给模型
    #   2. 要求模型输出修订后的完整版本
    #   3. 返回修订后的文本
    raise NotImplementedError("请补全此函数")


def reflect_and_revise(task: str, max_rounds: int = 3) -> str:
    """Reflection 主循环：起草 → 评审 → 修订 → ... → 返回最终版本。"""
    # TODO:
    #   1. content = draft(task) — 生成初稿
    #   2. for i in range(max_rounds):
    #        passed, feedback = review(task, content)
    #        if passed: break
    #        content = revise(task, content, feedback)
    #   3. return content
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：基本功能
    result = reflect_and_revise("写一个 Python 函数，计算斐波那契数列第 n 项，要求有 docstring 和类型注解")
    assert isinstance(result, str), "应该返回字符串"
    assert len(result) > 20, f"结果太短了: {result!r}"
    assert "def" in result or "fib" in result.lower(), "结果应该包含函数定义"
    print(f"[测试1] 最终结果 ({len(result)} 字符):")
    print(result[:200] + "..." if len(result) > 200 else result)

    # 测试 2：review 函数基本工作
    passed, feedback = review("写一首五言绝句", "床前明月光，疑是地上霜。举头望明月，低头思故乡。")
    assert isinstance(passed, bool), "passed 应该是 bool"
    assert isinstance(feedback, str), "feedback 应该是字符串"
    print(f"\n[测试2] review 结果: passed={passed}, feedback={feedback[:50]}...")

    # 测试 3：max_rounds 参数生效
    result2 = reflect_and_revise("用一句话解释什么是 AI", max_rounds=1)
    assert isinstance(result2, str) and len(result2) > 0, "max_rounds=1 也应该返回结果"

    print("\n✅ PASSED: reflect_and_revise 全部测试通过")
