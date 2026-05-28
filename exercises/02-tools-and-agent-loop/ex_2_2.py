"""
练习 2.2 · ToolRegistry 注册与调用
====================================

知识点：第 8 节《ToolRegistry》

要求：补全 MiniToolRegistry 类的三个方法
  - register(func): 装饰器，把函数注册进来
  - to_schemas(): 返回 OpenAI tools 格式的 schema 列表
  - invoke(name, args_dict): 按名字找到函数并执行

提示：
  - 用 func.__name__ 做键
  - 用 func.__doc__ 做 description
  - 用 func.__annotations__ 推断参数类型
  - inspect.signature(func) 可以拿到参数默认值（判断 required）
"""

import inspect
from typing import Any, Callable


class MiniToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, func: Callable) -> Callable:
        """装饰器：把 func 注册到 self._tools 里，键是函数名。"""
        # TODO: 把 func 存进 self._tools，然后原样返回 func
        raise NotImplementedError("请补全 register")

    def to_schemas(self) -> list[dict]:
        """生成 OpenAI tools 格式的 schema 列表。"""
        schemas = []
        for name, func in self._tools.items():
            # TODO: 对每个注册的函数，生成一个 schema dict：
            # {
            #   "type": "function",
            #   "function": {
            #       "name": name,
            #       "description": func.__doc__ or "",
            #       "parameters": {
            #           "type": "object",
            #           "properties": { ... },   # 从 __annotations__ 推断
            #           "required": [ ... ],      # 没有默认值的参数
            #       }
            #   }
            # }
            #
            # 类型映射：str→"string", int→"integer", float→"number", bool→"boolean"
            raise NotImplementedError("请补全 to_schemas")
        return schemas

    def invoke(self, name: str, args: dict) -> Any:
        """按名字找到函数并执行，返回结果。"""
        # TODO: 从 self._tools 里找到 name 对应的函数，传入 args 执行
        raise NotImplementedError("请补全 invoke")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    registry = MiniToolRegistry()

    @registry.register
    def get_weather(city: str, unit: str = "celsius") -> str:
        """查询指定城市的天气"""
        return f"{city}: 晴，25°{unit[0].upper()}"

    @registry.register
    def add(a: int, b: int) -> int:
        """计算两个整数的和"""
        return a + b

    # 测试 register
    assert "get_weather" in registry._tools, "get_weather 应该被注册"
    assert "add" in registry._tools, "add 应该被注册"

    # 测试 to_schemas
    schemas = registry.to_schemas()
    assert len(schemas) == 2, f"应该有 2 个 schema，实际 {len(schemas)}"

    weather_schema = next(s for s in schemas if s["function"]["name"] == "get_weather")
    assert weather_schema["type"] == "function"
    assert "city" in weather_schema["function"]["parameters"]["properties"]
    assert "city" in weather_schema["function"]["parameters"]["required"]
    # unit 有默认值，不应该在 required 里
    assert "unit" not in weather_schema["function"]["parameters"]["required"]

    add_schema = next(s for s in schemas if s["function"]["name"] == "add")
    assert add_schema["function"]["description"] == "计算两个整数的和"
    props = add_schema["function"]["parameters"]["properties"]
    assert props["a"]["type"] == "integer"
    assert props["b"]["type"] == "integer"

    # 测试 invoke
    result = registry.invoke("get_weather", {"city": "北京"})
    assert "北京" in result, f"get_weather 返回应该包含'北京'，实际: {result}"

    result = registry.invoke("add", {"a": 3, "b": 5})
    assert result == 8, f"add(3,5) 应该等于 8，实际: {result}"

    print("✅ PASSED: MiniToolRegistry 全部测试通过")
