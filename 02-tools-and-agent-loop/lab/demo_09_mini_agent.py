"""
Demo 09 · 最小 Agent Loop：50 行核心代码搞定
=============================================

配套：第 9 节《最小 Agent Loop 的 5 个核心点》

效果：把 demo_06 / demo_07 / demo_08 的零件拼成一个真正的 Agent：
  - 复用 demo_08 里写的 ToolRegistry
  - 用 OpenAI 官方 tool_calls 协议（demo_07 学过）
  - 主循环就 5 个核心点：调 LLM → 看 tool_calls → 跑工具 → 拼回 messages → 再来

核心代码不到 50 行，对比 demo_06 那个 hand-rolled 版本，你会发现：
  - 不再手写 prompt 让模型"输出 JSON"
  - 不再担心模型把 JSON 写歪了
  - 不再手工 parse 每一行模型输出

这是因为 OpenAI tool_calls 协议把"调用"这件事从 prompt 移到了结构化字段。

跑法：
    python demo_09_mini_agent.py
"""

from __future__ import annotations

import json
import urllib.request

from _env import get_model_id, make_client


# ============================================================
# Step 1：复用 ToolRegistry（demo_08 的写法，这里直接精简内联）
# ============================================================
import inspect
from typing import Any, Callable

_TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean"}


class ToolRegistry:
    def __init__(self) -> None:
        self._funcs: dict[str, Callable] = {}
        self._descs: dict[str, str] = {}

    def tool(self, description: str):
        def deco(func):
            self._funcs[func.__name__] = func
            self._descs[func.__name__] = description
            return func
        return deco

    def to_schemas(self) -> list[dict]:
        out = []
        for name, func in self._funcs.items():
            sig = inspect.signature(func)
            properties, required = {}, []
            for pname, p in sig.parameters.items():
                properties[pname] = {
                    "type": _TYPE_MAP.get(p.annotation, "string"),
                    "description": f"参数 {pname}",
                }
                if p.default is inspect.Parameter.empty:
                    required.append(pname)
            out.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": self._descs[name],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })
        return out

    def invoke(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._funcs:
            return f"未知工具: {name}"
        try:
            return str(self._funcs[name](**args))
        except Exception as e:
            return f"工具 {name} 执行出错: {e}"


# ============================================================
# Step 2：注册 3 个工具
# ============================================================
registry = ToolRegistry()


@registry.tool("计算一个数学表达式，例如 '1+2*3'")
def calculator(expr: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        return f"非法表达式: {expr}"
    return str(eval(expr))  # noqa: S307 demo 简化


@registry.tool("抓取一个 URL，返回前 500 字内容")
def fetch_url(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return body[:500]
    except Exception as e:
        return f"抓取失败: {e}"


@registry.tool("获取当前北京时间，格式 YYYY-MM-DD HH:MM:SS")
def current_time() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# Step 3：最小 Agent Loop —— 这才是今天的主菜
# ============================================================
def run_agent(question: str, max_iters: int = 6, verbose: bool = True) -> str:
    """最小可工作的 Agent Loop。

    5 个核心点：
      ① 调 LLM（带 tools 参数）
      ② 看返回里有没有 tool_calls
      ③ 没有 → 直接 return content（结束）
      ④ 有   → 逐个执行工具，把结果以 role=tool 追加到 messages
      ⑤ 回到 ①，直到不再要工具 / 达到 max_iters
    """
    client = make_client()
    MODEL = get_model_id()

    messages = [
        {"role": "system", "content": "你是一个会用工具的助手。需要时调用工具，最终给出简洁的中文回答。"},
        {"role": "user", "content": question},
    ]

    for turn in range(1, max_iters + 1):
        # ① 调 LLM
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=registry.to_schemas(),
            tool_choice="auto",
            temperature=0,
        )
        msg = resp.choices[0].message

        # ② / ③ 没有 tool_calls：返回最终回答
        if not msg.tool_calls:
            if verbose:
                print(f"\n[第 {turn} 轮] ✅ 模型给出最终回答")
            return msg.content or ""

        if verbose:
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
            args = json.loads(tc.function.arguments)
            result = registry.invoke(tc.function.name, args)
            if verbose:
                print(f"  → {tc.function.name}({args})")
                print(f"    = {result[:120]}{'...' if len(result) > 120 else ''}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
        # ⑤ 进入下一轮

    return "⚠️ 达到最大轮次仍未能给出最终答案"


# ============================================================
# 4 个测试任务，覆盖：单工具 / 多工具 / 串联 / 不存在工具
# ============================================================
TASKS = [
    "现在几点？",
    "17 * 23 等于多少？",
    "请抓取 https://example.com 的内容并告诉我它的字符长度除以 7 是多少。",
    "帮我查一下你训练数据里没有的'2099 年世界杯冠军是谁'。",
]


if __name__ == "__main__":
    for i, q in enumerate(TASKS, 1):
        print("\n" + "=" * 60)
        print(f"任务 {i}: {q}")
        print("=" * 60)
        answer = run_agent(q, max_iters=6)
        print(f"\n🎯 最终答案：{answer}")

    print("\n\n" + "=" * 60)
    print("🎯 看看你刚才看到了什么")
    print("=" * 60)
    print("  ① 任务 1/2 —— 单工具，一轮就结束")
    print("  ② 任务 3   —— 串联：先 fetch_url，再 calculator，两轮才完")
    print("  ③ 任务 4   —— 没有合适工具，模型应该承认不知道，而不是硬调")
    print()
    print("  注意：整个 Loop 主体不到 50 行，但这就是 Cursor / Claude Code")
    print("        每次帮你写代码时跑的同一个循环。复杂的不是循环本身，")
    print("        而是工具集（第5章）、上下文管理（第4章）、UI（第6章）。")
    print("=" * 60)
