"""极简工具系统 —— 工具注册、描述与执行。

核心设计：
- ToolRegistry 统一管理所有工具
- 支持两种注册方式：装饰器（简单函数）和 Tool 类（复杂工具）
- 自动生成 OpenAI function calling schema
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolParameter:
    """工具参数定义。"""

    name: str
    type: str  # string, number, integer, boolean, array
    description: str
    required: bool = True
    default: Any = None


class Tool(ABC):
    """工具基类：复杂工具继承此类实现。"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, **kwargs) -> str:
        """执行工具，返回字符串结果。"""
        pass

    def get_parameters(self) -> List[ToolParameter]:
        """返回参数定义列表，默认无参数。子类可覆写。"""
        return []

    def to_openai_schema(self) -> Dict[str, Any]:
        """转换为 OpenAI function calling schema。"""
        parameters = self.get_parameters()
        properties = {}
        required = []
        for param in parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }


class ToolRegistry:
    """工具注册表：管理所有可用工具。

    使用方式:
        registry = ToolRegistry()

        # 方式一：装饰器注册简单函数
        @registry.register("get_weather", "获取指定城市天气")
        def get_weather(city: str) -> str:
            return f"{city}的天气是晴天"

        # 方式二：注册 Tool 类实例
        registry.register_tool(MyComplexTool())

        # 执行工具
        result = registry.execute("get_weather", city="北京")

        # 获取 OpenAI schema（用于 function calling）
        tools_schema = registry.to_openai_schema()
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._functions: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        description: str,
        params: Optional[List[ToolParameter]] = None,
    ) -> Callable:
        """装饰器：注册一个普通函数为工具。"""

        def decorator(func: Callable) -> Callable:
            self._functions[name] = {
                "description": description,
                "func": func,
                "params": params or [],
            }
            return func

        return decorator

    def register_tool(self, tool: Tool) -> None:
        """注册一个 Tool 类实例。"""
        self._tools[tool.name] = tool

    def execute(self, name: str, **kwargs) -> str:
        """执行指定工具，返回结果字符串。"""
        # 优先查找 Tool 类
        if name in self._tools:
            try:
                return self._tools[name].run(**kwargs)
            except Exception as e:
                return f"❌ 工具 {name} 执行失败: {e}"

        # 再查找函数式工具
        if name in self._functions:
            try:
                return self._functions[name]["func"](**kwargs)
            except Exception as e:
                return f"❌ 工具 {name} 执行失败: {e}"

        return f"❌ 未找到工具: {name}"

    def get_tool_names(self) -> List[str]:
        """获取所有已注册工具的名称。"""
        return list(self._tools.keys()) + list(self._functions.keys())

    def get_tools_description(self) -> str:
        """获取所有工具的格式化描述（用于注入 system prompt）。"""
        lines = []
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
        for name, info in self._functions.items():
            lines.append(f"- {name}: {info['description']}")
        return "\n".join(lines) if lines else "暂无可用工具"

    def to_openai_schema(self) -> List[Dict[str, Any]]:
        """生成所有工具的 OpenAI function calling schema 列表。"""
        schemas = []

        # Tool 类实例
        for tool in self._tools.values():
            schemas.append(tool.to_openai_schema())

        # 函数式工具
        for name, info in self._functions.items():
            params = info.get("params", [])
            properties = {}
            required = []
            for p in params:
                properties[p.name] = {
                    "type": p.type,
                    "description": p.description,
                }
                if p.required:
                    required.append(p.name)

            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })

        return schemas
