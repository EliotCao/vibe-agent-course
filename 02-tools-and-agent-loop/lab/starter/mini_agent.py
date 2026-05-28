"""
Day 2 Lab · 最小 Agent Loop —— 填空骨架
==========================================

这个文件是"半成品"，关键 5 个核心点都标了 TODO。
你需要把每个 TODO 填上，让脚本跑通。

参考资料：
  - 第 9 节《最小 Agent Loop 的 5 个核心点》
  - demo_07_function_calling_protocol.py（消息流细节）
  - demo_08_tool_registry.py（ToolRegistry 用法）

跑法：
    python mini_agent.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 让脚本能直接 import 同仓库 demos 里的 _env.py（如果你拷贝到了别处，删掉这两行）
sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from _env import get_model_id, make_client

# 你可以从 demo_08 把 ToolRegistry 类直接拷过来，或者自己重写一遍
from typing import Any, Callable
import inspect


_TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean"}


class ToolRegistry:
    """极简 ToolRegistry。已经写好了，你直接用即可。"""

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
# 注册 3 个工具（你也可以自己再加）
# ============================================================
registry = ToolRegistry()


@registry.tool("计算一个数学表达式，例如 '1+2*3'")
def calculator(expr: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        return f"非法表达式: {expr}"
    return str(eval(expr))


@registry.tool("获取当前北京时间，格式 YYYY-MM-DD HH:MM:SS")
def current_time() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@registry.tool("抓取一个 URL，返回前 500 字内容")
def fetch_url(url: str) -> str:
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="replace")[:500]
    except Exception as e:
        return f"抓取失败: {e}"


# ============================================================
# 这里就是你今天要填的部分：最小 Agent Loop
# ============================================================
def run_agent(question: str, max_iters: int = 6) -> str:
    """跑一个最小 Agent Loop。

    填空提示：第 9 节讲了 5 个核心点，每个 TODO 对应一个核心点。
    """
    client = make_client()
    MODEL = get_model_id()

    messages = [
        {
            "role": "system",
            "content": "你是一个会用工具的助手。需要时调用工具，最终给出简洁的中文回答。",
        },
        {"role": "user", "content": question},
    ]

    for turn in range(1, max_iters + 1):
        print(f"\n--- 第 {turn} 轮 ---")

        # ----------------------------------------------------------------
        # TODO ① 调 LLM
        #   - 把 messages 全量传过去
        #   - 把 registry.to_schemas() 作为 tools 参数
        #   - tool_choice="auto"
        # 提示：返回的 msg = resp.choices[0].message
        # ----------------------------------------------------------------
        msg = ...   # ← 你的代码

        # ----------------------------------------------------------------
        # TODO ② 检查 tool_calls：没有就直接返回（这是循环唯一退出条件）
        # ----------------------------------------------------------------
        if ...:     # ← 你的代码
            print(f"✅ 模型给出最终回答")
            return msg.content or ""

        print(f"模型要求调用 {len(msg.tool_calls)} 个工具")

        # ----------------------------------------------------------------
        # TODO ③ 把 assistant 消息（含 tool_calls）追加回 messages
        # 提示：role="assistant"，content=msg.content（可能是 None），
        #      tool_calls 字段需要把每个 tc 序列化成 dict
        # ----------------------------------------------------------------
        messages.append(...)   # ← 你的代码

        # ----------------------------------------------------------------
        # TODO ④ 逐个执行工具，结果以 role=tool 追加
        #   - 用 json.loads(tc.function.arguments) 解析参数
        #   - 用 registry.invoke(tc.function.name, args) 执行
        #   - 追加 {"role": "tool", "tool_call_id": tc.id, "content": result}
        # ----------------------------------------------------------------
        for tc in msg.tool_calls:
            args = ...          # ← 你的代码
            result = ...        # ← 你的代码
            print(f"  → {tc.function.name}({args}) = {result[:80]}...")
            messages.append(...)  # ← 你的代码

        # ⑤ 进入下一轮（for 循环自然处理）

    return "⚠️ 达到最大轮次仍未给出最终答案"


# ============================================================
# 自测任务
# ============================================================
TASKS = [
    "现在几点？",
    "17 * 23 等于多少？",
    "请抓取 https://example.com 的内容，告诉我它的字符长度除以 7 是多少。",
    "你训练数据里没有的 '2099 年世界杯冠军' 是谁？",   # 故意刁难
]


if __name__ == "__main__":
    for i, q in enumerate(TASKS, 1):
        print("\n" + "=" * 60)
        print(f"任务 {i}: {q}")
        print("=" * 60)
        answer = run_agent(q)
        print(f"\n🎯 最终答案：{answer}")
