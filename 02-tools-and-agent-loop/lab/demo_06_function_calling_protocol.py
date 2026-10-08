"""
Demo 07 · Function Calling 协议：手工拼出完整消息流
==================================================

配套：第 6 节《Function Calling 协议：Tool Schema 与消息流》

效果：直观展示——
  - 一个完整的 function calling 调用，到底有几条消息
  - 每条消息长什么样、role 字段为什么有 4 种
  - assistant 消息里的 tool_calls 是什么结构
  - tool 消息凭什么对应到上一条 tool_call（靠 tool_call_id）

我们故意**不调用任何 Agent 封装**，全部手写 messages 列表，
但循环骨架已经按 demo_08《最小 Agent Loop》的标准模板来写
（`for turn in range(max_iters)`、消息回填字段顺序完全一致），
方便你之后切到第 8 节时一眼就能看出"啊，那个 loop 我已经见过了"。

跑法：
    python demo_06_function_calling_protocol.py
"""

from __future__ import annotations

import json

from _env import chat


# ============================================================
# Step 1：手写一份 Tool Schema（OpenAI 标准格式）
# ============================================================
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，例如 '北京'、'上海'",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


# ============================================================
# Step 2：工具的"真实实现"（Mock，不依赖外部 API，方便本地跑）
# ============================================================
def get_weather(city: str) -> str:
    fake_db = {
        "北京": "晴，25°C，微风",
        "上海": "多云，27°C，东南风",
        "深圳": "雷阵雨，30°C，闷热",
    }
    return fake_db.get(city, f"暂无 {city} 的天气数据")


# ============================================================
# Step 3：一次完整调用，把每条消息打印出来看全貌
#
# 循环结构与 demo_08 的 run_agent 严格对齐：
#   ① 调 LLM（带 tools 参数）
#   ② 看返回里有没有 tool_calls
#   ③ 没有 → 把最终 assistant 消息回填后 break（结束）
#   ④ 有   → 把 assistant 消息（含 tool_calls）和 tool 结果都回填到 messages
#   ⑤ 回到 ①，直到不再要工具 / 达到 max_iters
#
# 与 demo_08 唯一的差异：本 demo 在每一步都把 messages 详细打印出来，
# 让你看到协议本身长什么样；demo_08 只打印必要进度。
# ============================================================
def main(
    question: str = "北京今天天气怎么样？穿什么衣服合适？",
    max_iters: int = 4,
) -> None:
    print("=" * 60)
    print("Function Calling 完整消息流演示")
    print("=" * 60)

    # ---- 初始消息：system + user ----
    messages = [
        {
            "role": "system",
            "content": "你是一个天气助手。可以使用 get_weather 工具查询天气。",
        },
        {"role": "user", "content": question},
    ]

    print("\n--- 初始 messages ---")
    print(json.dumps(messages, ensure_ascii=False, indent=2))

    for turn in range(1, max_iters + 1):
        # ① 调 LLM
        print(f"\n>>> 第 {turn} 轮：调用 LLM（带 tools 参数）...")
        msg = chat(
            messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0,
        )

        print(f"\n--- 第 {turn} 轮 · assistant 响应 ---")
        print(f"role:       assistant")
        print(f"content:    {msg.content!r}   ← 注意可能是 None")
        print(f"tool_calls: {msg.tool_calls}")

        # ② / ③ 没有 tool_calls：返回最终回答
        if not msg.tool_calls:
            print(f"\n[第 {turn} 轮] ✅ 模型给出最终回答（不再要求调工具）")
            # 把最终 assistant 消息也回填进 messages，方便最后打印完整历史
            messages.append({"role": "assistant", "content": msg.content})
            break

        print(f"\n[第 {turn} 轮] 模型要求调用 {len(msg.tool_calls)} 个工具：")

        # ④ 把 assistant 消息追加（必须含 tool_calls 字段）
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ],
        })

        # 逐个执行工具，结果以 role=tool 追加
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"  → 执行工具: {name}({args})")
            if name == "get_weather":
                result = get_weather(**args)
            else:
                result = f"未知工具: {name}"
            print(f"    = {result}")
            # 关键：tool_call_id 必须和上一条 assistant.tool_calls[*].id 对得上
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
        # ⑤ 进入下一轮
    else:
        print(f"\n⚠️ 达到最大轮次 {max_iters}，仍未给出最终回答")

    # ---- 打印整段对话历史 ----
    print("\n\n" + "=" * 60)
    print("📜 完整 messages 历史（4 种角色都出现了）：")
    print("=" * 60)
    print(json.dumps(messages, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
