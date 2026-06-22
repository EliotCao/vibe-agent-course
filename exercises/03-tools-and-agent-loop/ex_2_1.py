"""
练习 2.1 · 手搓 Function Calling 消息流
=========================================

知识点：第 7 节《Function Calling 协议》

要求：补全 run_tool_call 函数
  - 给模型一个 calculator 工具
  - 让模型决定是否调用
  - 手动执行工具
  - 把结果回传，拿到最终回答

你需要理解 4 条消息的完整流转。
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../03-tools-and-agent-loop/lab"))
from _env import chat, get_model_id, make_client

client = make_client()
MODEL = get_model_id()

# 工具的 schema
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算一个数学表达式，返回结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '2 + 3 * 4'",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]


def execute_calculator(expression: str) -> str:
    """执行计算（已实现，不用改）"""
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def run_tool_call(question: str) -> str:
    """完整的 Function Calling 流程，返回模型最终回答。"""

    messages = [{"role": "user", "content": question}]

    # TODO Step 1: 第一次调 API（带 tools 参数），让模型决定是否调用工具
    #   msg = chat(messages, tools=TOOLS, client=client, model=MODEL)

    # TODO Step 2: 检查 msg.tool_calls 是否存在
    #   如果没有 tool_calls，说明模型直接回答了，返回 msg.content

    # TODO Step 3: 有 tool_calls → 执行工具
    #   - 取出 tool_call = msg.tool_calls[0]
    #   - 解析参数: args = json.loads(tool_call.function.arguments)
    #   - 执行: result = execute_calculator(args["expression"])

    # TODO Step 4: 把 assistant 消息和 tool 结果追加到 messages
    #   messages.append(msg)  # assistant 消息（含 tool_calls）
    #   messages.append({
    #       "role": "tool",
    #       "tool_call_id": tool_call.id,
    #       "content": result,
    #   })

    # TODO Step 5: 第二次调 API，拿到最终回答
    # msg2 = chat(messages, tools=TOOLS, client=client, model=MODEL)
     # return msg2.content


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 测试 1：简单计算
    answer = run_tool_call("请帮我算一下 123 乘以 456 等于多少")
    assert "56088" in re.sub(r"\D", "", answer), f"123×456=56088，但模型回答: {answer}"

    # 测试 2：返回类型
    answer2 = run_tool_call("7 + 8 等于多少？")
    assert isinstance(answer2, str), "返回值应该是字符串"
    assert "15" in re.sub(r"\D", "", answer2), f"7+8=15，但模型回答: {answer2}"

    print("✅ PASSED: run_tool_call 全部测试通过")
