"""ToolRegistry：装饰器注册 + 自动 schema + 按名分发。

跟 Day2 demo_08 的 ToolRegistry 几乎一致，多了一个 `bind_workdir`：
让 bash 工具的 cwd 能被 Agent 锁定到工作区。
"""

from __future__ import annotations

import inspect
from functools import partial
from typing import Any, Callable

_TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolRegistry:
    def __init__(self) -> None:
        self._funcs: dict[str, Callable] = {}
        self._descs: dict[str, str] = {}

    # ---------- 注册 ----------
    def tool(self, description: str):
        def deco(func):
            self._funcs[func.__name__] = func
            self._descs[func.__name__] = description
            return func
        return deco

    def register(self, func: Callable, description: str, *, name: str | None = None) -> None:
        n = name or func.__name__
        self._funcs[n] = func
        self._descs[n] = description

    # ---------- 把某个工具的某个参数永久绑定（比如 bash 的 workdir） ----------
    def bind_default(self, name: str, **defaults) -> None:
        """给已注册的工具固定一些默认参数。常用于 bash(workdir=...)。"""
        if name not in self._funcs:
            raise KeyError(f"未注册的工具: {name}")
        original = self._funcs[name]
        bound = partial(original, **defaults)
        # functools.partial 对象拿不到 __name__，手动给个属性
        bound.__name__ = name  # type: ignore[attr-defined]
        self._funcs[name] = bound
        # 复用 inspect 时基于 original，绑定参数从 schema 中剔除
        self._defaults_bound = getattr(self, "_defaults_bound", {})
        self._defaults_bound[name] = (original, set(defaults.keys()))

    # ---------- 生成 OpenAI schema ----------
    def to_schemas(self) -> list[dict]:
        out = []
        for name in self._funcs:
            original, hidden = (
                getattr(self, "_defaults_bound", {}).get(name, (self._funcs[name], set()))
            )
            sig = inspect.signature(original)
            properties, required = {}, []
            for pname, p in sig.parameters.items():
                if pname in hidden:
                    continue  # 已被 bind_default 锁定的参数不暴露给 LLM
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

    # ---------- 调度 ----------
    def invoke(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._funcs:
            return f"❌ 未知工具: {name}"
        try:
            return str(self._funcs[name](**args))
        except Exception as e:  # noqa: BLE001
            return f"❌ 工具 {name} 执行出错: {e}"


# ============================================================
# 默认装配：注册 5 个必做 + 1 个选做
# ============================================================
def build_registry(workdir: str | None = None) -> ToolRegistry:
    """构造一个完整 ToolRegistry。

    workdir：传入后会绑到 bash 工具，让 LLM 不需要每次都传 workdir。
    """
    from .coding_tools import read, write, edit, list_dir, bash, grep

    reg = ToolRegistry()
    reg.register(read, "读取文件内容，返回带行号的文本（支持 offset/limit/max_bytes）")
    reg.register(write, "新建文件或覆盖已有文件（已存在文件需 overwrite=True）")
    reg.register(edit, "精确替换文件中的一段已有内容（old_content 必须唯一出现）")
    reg.register(list_dir, "列出目录的文件和子目录")
    reg.register(bash, "在工作区内执行 shell 命令，返回 stdout / stderr / exit code")
    reg.register(grep, "递归在目录里搜索包含正则 pattern 的行")

    if workdir:
        reg.bind_default("bash", workdir=workdir)
    return reg
