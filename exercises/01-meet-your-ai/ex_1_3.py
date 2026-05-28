"""
练习 1.3 · 幻觉检测器
======================

知识点：第 4 节《大模型幻觉》

要求：补全 detect_hallucination 函数
  - 输入：question（str）、answer（str）
  - 输出：bool — True 表示回答中可能有幻觉，False 表示没有

实现思路：让 LLM 来判断！
  构造一个 prompt，把 question 和 answer 喂给模型，让它判断回答中有没有编造。
  模型回复 "是" 或 "否"，你解析成 bool 返回。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../01-meet-your-ai/lab"))
from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def detect_hallucination(question: str, answer: str) -> bool:
    """让 LLM 判断 answer 中是否存在针对 question 的幻觉/编造内容。

    返回 True = 有幻觉，False = 没有。
    """
    # TODO:
    #   1. 构造一个 system prompt，告诉模型它是"事实核查员"
    #   2. 把 question 和 answer 喂进去，让模型判断有没有编造
    #   3. 要求模型只回复 "是" 或 "否"
    #   4. 解析回复：包含 "是" → return True，否则 return False
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：明显的幻觉（虚构的事实）
    result = detect_hallucination(
        question="Python 是谁发明的？",
        answer="Python 是由 Steve Jobs 在 1985 年发明的，最初用于苹果电脑。",
    )
    assert result is True, "Steve Jobs 发明 Python 是明显的幻觉"

    # 测试 2：正确的事实
    result = detect_hallucination(
        question="Python 是谁发明的？",
        answer="Python 是由 Guido van Rossum 在 1991 年左右发布的。",
    )
    assert result is False, "Guido van Rossum 发明 Python 是正确事实"

    # 测试 3：返回值类型
    result = detect_hallucination("1+1=?", "1+1=2")
    assert isinstance(result, bool), "返回值应该是 bool"

    print("✅ PASSED: detect_hallucination 全部测试通过")
