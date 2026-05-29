"""
第2章产出：ToolRegistry
========================

补全这个类，让 tests/test_tools.py 全部通过。
"""

from __future__ import annotations

import inspect
import json
from typing import Any, Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, func: Callable) -> Callable:
        """装饰器：注册工具函数。"""
        # TODO: 存储 func，键为 func.__name__，返回 func
        raise NotImplementedError("请补全 register")

    def to_schemas(self) -> list[dict]:
        """生成 OpenAI tools 格式的 schema 列表。"""
        # TODO: 遍历 self._tools，为每个函数生成 schema
        #   - name: func.__name__
        #   - description: func.__doc__
        #   - parameters: 从 __annotations__ + inspect.signature 推断
        #   - required: 没有默认值的参数
        #   类型映射: str→"string", int→"integer", float→"number", bool→"boolean"
        raise NotImplementedError("请补全 to_schemas")

    def invoke(self, name: str, args: dict) -> str:
        """按名字执行工具，返回字符串结果。"""
        # TODO:
        #   func = self._tools[name]
        #   result = func(**args)
        #   return str(result)
        # 注意：用 try/except 包住，出错返回错误信息而不是抛异常
        raise NotImplementedError("请补全 invoke")

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
