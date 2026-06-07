"""
练习 3.2 · Plan-and-Solve 的 Planner
======================================

知识点：第 13 节《Plan-and-Solve 范式》

要求：补全 make_plan 函数
  - 输入：用户问题（str）
  - 输出：步骤列表（list[str]），每个元素是一个具体步骤描述

实现思路：让 LLM 把问题拆成步骤，要求输出 JSON 数组。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../02-meet-your-ai/lab"))
from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def make_plan(question: str) -> list[str]:
    """让 LLM 把 question 拆解成有序步骤列表。

    返回一个字符串列表，如 ["第一步：...", "第二步：...", ...]
    """
    # TODO:
    #   1. 构造 system prompt，要求模型：
    #      - 把用户问题拆解成 3-6 个具体执行步骤
    #      - 只输出 JSON 数组格式，如 ["步骤1", "步骤2", ...]
    #      - 不要输出其他内容
    #   2. 调用 API
    #   3. 解析返回的 JSON（注意容错：模型可能输出 ```json...``` 包裹）
    #   4. 返回步骤列表
    #
    # 容错提示：可以用 content.strip().strip("```json").strip("```").strip()
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：简单任务
    plan = make_plan("帮我写一个 Python 的冒泡排序并测试它")
    assert isinstance(plan, list), f"应该返回列表，实际: {type(plan)}"
    assert len(plan) >= 2, f"至少应该有 2 步，实际: {len(plan)} 步"
    assert all(isinstance(s, str) for s in plan), "每个步骤应该是字符串"
    print(f"[测试1] 计划有 {len(plan)} 步:")
    for i, step in enumerate(plan, 1):
        print(f"  {i}. {step}")

    # 测试 2：复杂任务
    plan2 = make_plan("查北京和上海的天气，对比哪个更适合周末出游，给出推荐理由")
    assert len(plan2) >= 3, f"复杂任务至少 3 步，实际: {len(plan2)} 步"
    print(f"\n[测试2] 计划有 {len(plan2)} 步:")
    for i, step in enumerate(plan2, 1):
        print(f"  {i}. {step}")

    # 测试 3：步骤内容不为空
    for step in plan + plan2:
        assert len(step.strip()) > 0, "步骤内容不应该为空"

    print("\n✅ PASSED: make_plan 全部测试通过")
