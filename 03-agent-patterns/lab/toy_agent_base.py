"""
第3章 公共基础：极简 ToolRegistry + 5 个测试任务

3 种范式（ReAct / Plan-and-Solve / Reflection）的 demo 都从这里 import。
保证三个 demo 用的是**同一套工具**，让"横向对比"是 apple-to-apple。
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Callable

from _env import get_model_id, make_client


# ============================================================
# 极简 ToolRegistry（来自 第2章 demo_07）
# ============================================================
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

    def get_tools_description(self) -> str:
        """以人类可读形式列出工具，用于注入 ReAct 风格 prompt。"""
        return "\n".join(
            f"- {name}({', '.join(inspect.signature(self._funcs[name]).parameters)}): {desc}"
            for name, desc in self._descs.items()
        )

    def invoke(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._funcs:
            return f"未知工具: {name}"
        try:
            return str(self._funcs[name](**args))
        except Exception as e:  # noqa: BLE001
            return f"工具 {name} 执行出错: {e}"


# ============================================================
# 共享工具集（mock，方便本地跑）
# ============================================================
registry = ToolRegistry()


@registry.tool("查询指定城市的当前天气，参数 city 为城市名")
def get_weather(city: str) -> str:
    fake = {"北京": "晴 25°C", "上海": "多云 27°C", "深圳": "雷阵雨 30°C"}
    return fake.get(city, f"暂无 {city} 数据")


@registry.tool("根据城市和天气推荐旅游景点，参数 city 为城市，weather 为天气描述")
def get_attraction(city: str, weather: str) -> str:
    fake = {
        "北京": "故宫、颐和园、长城（雨天可改去国家博物馆）",
        "上海": "外滩、东方明珠、迪士尼（雨天可去 K11、新天地）",
        "深圳": "世界之窗、东部华侨城（雷雨可去万象城）",
    }
    return fake.get(city, f"暂无 {city} 景点数据")


@registry.tool("计算一个数学表达式，例如 '1+2*3'")
def calculator(expr: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        return f"非法表达式: {expr}"
    return str(eval(expr))  # noqa: S307 demo 简化


@registry.tool("查询某商品的价格，参数 sku 为商品编号")
def get_price(sku: str) -> str:
    fake = {"A001": "100", "A002": "250", "A003": "80"}
    return fake.get(sku, f"未找到 {sku}")


# ============================================================
# 5 个统一测试任务
# 不同范式跑同样这 5 个，便于横向对比
# ============================================================
TASKS = [
    "北京今天天气怎么样？基于天气推荐 2 个景点。",
    "A001、A002、A003 三个商品总价是多少？再算一下平均价。",
    "深圳今天适合户外活动吗？如果不适合，请推荐室内景点。",
    "帮我查上海天气，再推荐景点，最后告诉我景点名字一共有几个汉字。",
    "我训练数据里没有的 '2099 年世界杯冠军' 是谁？",  # 故意刁难
]


# ============================================================
# 调度封装
# ============================================================
def make_llm():
    return make_client(), get_model_id()
