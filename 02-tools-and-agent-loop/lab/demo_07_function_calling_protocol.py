"""
Demo 07 · Function Calling 协议：手工拼出完整消息流
==================================================

配套：第 7 节《Function Calling 协议：Tool Schema 与消息流》

效果：直观展示——
  - 一个完整的 function calling 调用，到底有几条消息
  - 每条消息长什么样、role 字段为什么有 4 种
  - assistant 消息里的 tool_calls 是什么结构
  - tool 消息凭什么对应到上一条 tool_call（靠 tool_call_id）

我们故意**不调用任何封装**，全部手写 messages 列表，展示协议本身。

跑法：
    python demo_07_function_calling_protocol.py
"""

from __future__ import annotations

import json

from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


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
# ============================================================
def main() -> None:
    print("=" * 60)
    print("Function Calling 完整消息流演示")
    print("=" * 60)

    # ---- 初始消息：system + user ----
    messages = [
        {
            "role": "system",
            "content": "你是一个天气助手。可以使用 get_weather 工具查询天气。",
        },
        {"role": "user", "content": "北京今天天气怎么样？穿什么衣服合适？"},
    ]

    print("\n--- 初始 messages ---")
    print(json.dumps(messages, ensure_ascii=False, indent=2))

    # ---- 第一次调用：把 tools schema 一并传过去 ----
    print("\n>>> 第一次调用 LLM（带 tools 参数）...")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS_SCHEMA,
        tool_choice="auto",  # 让模型自己决定要不要调
        temperature=0,
    )

    msg = resp.choices[0].message
    print("\n--- 第一次响应：assistant 消息 ---")
    print(f"role:       {msg.role}")
    print(f"content:    {msg.content!r}   ← 注意可能是 None")
    print(f"tool_calls: {msg.tool_calls}")
    print()
    if not msg.tool_calls:
        print("（模型没有要求调工具，结束）")
        return

    # ---- 把 assistant 的 tool_calls 消息加回 messages（必须！）----
    messages.append(
        {
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
        }
    )

    # ---- 执行每个 tool_call，结果以 role=tool 追加 ----
    for tc in msg.tool_calls:
        name = tc.function.name
        args = json.loads(tc.function.arguments)
        print(f">>> 执行工具: {name}({args})")
        if name == "get_weather":
            result = get_weather(**args)
        else:
            result = f"未知工具: {name}"
        print(f"   工具返回: {result}")

        # 关键：tool_call_id 必须和上一条 assistant.tool_calls[*].id 对得上
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            }
        )

    # ---- 第二次调用：让模型基于工具结果生成最终回答 ----
    print("\n>>> 第二次调用 LLM（带工具结果）...")
    resp2 = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS_SCHEMA,
        temperature=0,
    )
    final_msg = resp2.choices[0].message
    print("\n--- 第二次响应：assistant 最终回答 ---")
    print(final_msg.content)

    # ---- 把最终消息也加回去，打印整段对话历史 ----
    messages.append({"role": "assistant", "content": final_msg.content})

    print("\n\n" + "=" * 60)
    print("📜 完整 messages 历史（4 种角色都出现了）：")
    print("=" * 60)
    for i, m in enumerate(messages, 1):
        role = m["role"]
        if role == "tool":
            print(f"[{i}] 🛠 tool      content={m['content']!r}")
            print(f"      tool_call_id={m['tool_call_id']}")
        elif role == "assistant" and m.get("tool_calls"):
            print(f"[{i}] 🤖 assistant content={m['content']!r}")
            for tc in m["tool_calls"]:
                print(f"      tool_calls -> id={tc['id']}")
                print(f"                    name={tc['function']['name']}")
                print(f"                    args={tc['function']['arguments']}")
        else:
            content = m.get("content", "")
            if content and len(content) > 80:
                content = content[:80] + "..."
            print(f"[{i}] {role:9s} content={content!r}")

    print("\n💡 关键观察:")
    print("  - 完整一次工具调用 = 4 条消息：system + user + assistant(tool_calls) + tool")
    print("  - assistant.content 在调工具时通常是 None，真正的'指令'藏在 tool_calls 里")
    print("  - tool 消息靠 tool_call_id 精准对应到上一条 assistant 的某个 tool_call")
    print("  - 第二次调用时必须把上面 4 条都传回去，模型才能看见'刚才的工具结果'")


if __name__ == "__main__":
    main()
