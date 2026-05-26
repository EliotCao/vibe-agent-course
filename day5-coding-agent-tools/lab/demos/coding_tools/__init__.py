"""
Day 5 工具集集合：把 5 个必做 + 1 个选做工具注册到 ToolRegistry

用法：
    from coding_tools import build_registry
    registry = build_registry(workdir="/path/to/workspace")
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from .read import read
from .write import write
from .edit import edit
from .list_dir import list_dir
from .bash import bash
from .grep import grep


# ============================================================
# 极简 ToolRegistry（来自 Day2，方便 Day5 demo 自洽运行）
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

    def register(self, func: Callable, description: str) -> None:
        self._funcs[func.__name__] = func
        self._descs[func.__name__] = description

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
        return "\n".join(f"- {n}: {d}" for n, d in self._descs.items())

    def invoke(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._funcs:
            return f"未知工具: {name}"
        try:
            return str(self._funcs[name](**args))
        except Exception as e:
            return f"工具 {name} 执行出错: {e}"


# ============================================================
# 默认注册：5 个必做 + 1 个选做（grep）
# ============================================================
def build_registry() -> ToolRegistry:
    """构造一个包含 Day5 所有工具的 ToolRegistry。"""
    reg = ToolRegistry()
    reg.register(read, "读取文件内容，返回带行号的文本")
    reg.register(write, "新建文件或覆盖已有文件（已存在文件需 overwrite=True）")
    reg.register(edit, "精确替换文件中的一段已有内容（old_content 必须唯一）")
    reg.register(list_dir, "列出目录的文件和子目录")
    reg.register(bash, "在工作区内执行 shell 命令，返回 stdout / stderr / exit code")
    reg.register(grep, "递归在目录里搜索包含正则 pattern 的行（选做）")
    return reg


__all__ = ["ToolRegistry", "build_registry", "read", "write", "edit", "list_dir", "bash", "grep"]
