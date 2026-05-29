"""
Demo 05 · LLM + 外部支持：从"不知道"到"知道"
=============================================

配套：第 5 节《LLM 智能 + 外部支持：为什么需要工具与上下文》

效果：同一个问题，分两种方式：
  ① 手动把外部知识塞进 prompt（最朴素的 RAG）
  ② 真正的 Function Calling：让模型自己决定调工具

直观感受"为什么需要 第2章 的工具系统"。

跑法：
    python demo_05_with_tool.py
"""

from __future__ import annotations

import datetime
import json

from _env import get_model_id, make_client, chat as llm_chat

client = make_client()
MODEL = get_model_id()


# ---------- 一个"工具"：返回当前时间 ----------
def get_current_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------- 一个"工具"：查文件内容（mock 一个 LLM 不知道的事实） ----------
SECRET_FILE = """\
[内部公告]
项目交付截止时间：2026-06-30 23:59:59
联系人：王经理
紧急联系电话：13800138000
"""

def read_internal_doc() -> str:
    return SECRET_FILE


# ---------- 实验 1：手动注入外部知识 ----------
def exp_internal_knowledge() -> None:
    print("=" * 60)
    print("【实验 1：把外部知识塞进 prompt】")
    print("=" * 60)

    question = "Hello-Agents 项目的交付截止时间是什么时候？联系人电话多少？"

    print("\n--- ① 纯 LLM 回答 ---")
    msg = llm_chat(
        [{"role": "user", "content": question}],
        temperature=0,
    )
    print(msg.content)
    print("👆 模型不可能知道，要么承认不知道，要么编一个。")

    print("\n--- ② 把'内部文档'塞进 prompt ---")
    enriched = f"""\
请基于下面提供的内部文档回答用户问题。

【内部文档】
{read_internal_doc()}

【用户问题】
{question}
"""
    msg = llm_chat(
        [{"role": "user", "content": enriched}],
        temperature=0,
    )
    print(msg.content)

    print("\n💡 看：把'外部知识'喂进去，模型立刻能精准回答。")
    print("   这就是 RAG（Retrieval-Augmented Generation）的最朴素版本。")


# ---------- 实验 2：真正的 Function Calling（预告） ----------
def exp_real_tool_call() -> None:
    """最简 Function Calling：让模型自己决定调工具。第2章 会展开讲。"""
    print("\n\n" + "=" * 60)
    print("【实验 2：真正的 Function Calling（第2章 预告）】")
    print("=" * 60)
    print("上面是'人工拼 prompt'。下面让模型**自己决定**要不要调工具：\n")

    # 声明一个工具 schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "获取当前北京时间",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]

    question = "现在北京时间几点？"
    messages = [{"role": "user", "content": question}]

    # 第一轮：模型看到工具列表，自己决定是否调用
    msg = llm_chat(
        messages,
        tools=tools,
    )

    if msg.tool_calls:
        print("msg.tool_calls:", msg.tool_calls)
        tool_call = msg.tool_calls[0]
        print(f"✅ 模型决定调用工具: {tool_call.function.name}()")
        print(f"   tool_call_id: {tool_call.id}")

        # 执行工具
        result = get_current_time()
        print(f"   工具返回: {result}")

        # 第二轮：把工具结果回传，模型生成最终回答
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            ],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })
        final_msg = llm_chat(
            messages,
            tools=tools,
        )
        print(f"\n🤖 最终回答: {final_msg.content}")
    else:
        print(f"模型直接回答（没调工具）: {msg.content}")

    print("\n💡 区别：这次不是我们手动塞结果，而是模型自主决定'我需要调工具'。")
    print("   第2章 会完整讲解这个协议的每一条消息。")


if __name__ == "__main__":
    exp_internal_knowledge()
    exp_real_tool_call()
