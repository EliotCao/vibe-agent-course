"""
Demo 08 · ToolRegistry：从函数到 Schema 的自动化
================================================

配套：第 8 节《ToolRegistry：让加工具像加函数一样简单》

效果：直观展示——
  - 一个 80 行以内的 ToolRegistry，能做到：
    ① 装饰器注册：@registry.tool("xx") 一行搞定
    ② 自动从函数签名 + docstring 生成 OpenAI tool schema
    ③ 按工具名分发执行
  - 与 demo_07 对比：手写 schema 那 30 行配置全部消失了

跑法：
    python demo_08_tool_registry.py
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Callable

from _env import get_model_id, make_client


# ============================================================
# 一份 80 行以内、简洁可读的 ToolRegistry
# ============================================================
class ToolRegistry:
    """极简工具注册表。

    用法：
        registry = ToolRegistry()

        @registry.tool("查询城市天气")
        def get_weather(city: str) -> str:
            ...

        # 把 schema 喂给 LLM
        schemas = registry.to_schemas()
        # 接到 tool_calls 后调度执行
        result = registry.invoke("get_weather", {"city": "北京"})
    """

    # Python 类型 -> OpenAI schema 类型
    _TYPE_MAP = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    def __init__(self) -> None:
        self._funcs: dict[str, Callable] = {}
        self._descs: dict[str, str] = {}

    # ---------- 注册 ----------
    def tool(self, description: str) -> Callable:
        """装饰器：注册一个函数为工具。description 给 LLM 看。"""

        def decorator(func: Callable) -> Callable:
            self._funcs[func.__name__] = func
            self._descs[func.__name__] = description
            return func

        return decorator

    # ---------- 生成 OpenAI tool schema ----------
    def _func_to_schema(self, name: str) -> dict:
        func = self._funcs[name]
        sig = inspect.signature(func)

        properties: dict[str, dict] = {}
        required: list[str] = []
        for pname, param in sig.parameters.items():
            ptype = self._TYPE_MAP.get(param.annotation, "string")
            properties[pname] = {
                "type": ptype,
                "description": f"参数 {pname}",
            }
            if param.default is inspect.Parameter.empty:
                required.append(pname)

        return {
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
        }

    def to_schemas(self) -> list[dict]:
        return [self._func_to_schema(n) for n in self._funcs]

    # ---------- 调度执行 ----------
    def invoke(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._funcs:
            return f"未知工具: {name}"
        try:
            return str(self._funcs[name](**args))
        except Exception as e:  # noqa: BLE001 demo 简化
            return f"工具 {name} 执行出错: {e}"


# ============================================================
# 用 ToolRegistry 注册三个工具
# ============================================================
registry = ToolRegistry()


@registry.tool("计算一个数学表达式，例如 '1+2*3'，只允许数字和 + - * / ( ) .")
def calculator(expr: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        return f"非法表达式: {expr}"
    return str(eval(expr))  # noqa: S307 demo 简化


@registry.tool("获取当前北京时间，格式为 YYYY-MM-DD HH:MM:SS")
def current_time() -> str:
    import datetime

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@registry.tool("查询指定城市的当前天气，参数 city 为城市名")
def get_weather(city: str) -> str:
    fake_db = {"北京": "晴 25°C", "上海": "多云 27°C"}
    return fake_db.get(city, f"暂无 {city} 数据")


# ============================================================
# 看看 ToolRegistry 自动生成的 schema 长什么样
# ============================================================
def show_schemas() -> None:
    print("=" * 60)
    print("【ToolRegistry 自动生成的 schemas】")
    print("=" * 60)
    schemas = registry.to_schemas()
    print(f"共注册了 {len(schemas)} 个工具，下面是它们的 schema：\n")
    print(json.dumps(schemas, ensure_ascii=False, indent=2))


# ============================================================
# 跟 LLM 跑一次完整调用，看 ToolRegistry 怎么调度
# ============================================================
def run_with_llm() -> None:
    from _env import chat as llm_chat

    print("\n\n" + "=" * 60)
    print("【用 ToolRegistry 完整跑一次 function calling】")
    print("=" * 60)

    messages = [
        {"role": "system", "content": "你是助手。需要时使用工具。"},
        {"role": "user", "content": "现在几点？北京天气怎么样？另外 17 * 23 等于多少？"},
    ]

    # 多轮循环：模型可能会连续调多个工具
    for turn in range(1, 6):
        print(f"\n--- 第 {turn} 轮 ---")
        msg = llm_chat(
            messages,
            tools=registry.to_schemas(),
            tool_choice="auto",
            temperature=0,
        )

        if not msg.tool_calls:
            print(f"🎯 最终回答：{msg.content}")
            return

        # 把 assistant 的 tool_calls 消息原样追加
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

        # 用 ToolRegistry 调度，结果以 role=tool 追加
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = registry.invoke(tc.function.name, args)
            print(f"  → {tc.function.name}({args}) = {result}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    print("⚠️ 达到最大轮次")


if __name__ == "__main__":
    show_schemas()
    run_with_llm()

    print("\n\n" + "=" * 60)
    print("🎯 跟 demo_07 对比一下")
    print("=" * 60)
    print("  demo_07：每加一个工具都要手写 30 行 schema JSON")
    print("  demo_08：写个普通函数 + 装饰器一行，schema 自己长出来")
    print()
    print("  这就是为什么需要 ToolRegistry —— 让加工具像加函数一样简单。")
    print("=" * 60)
