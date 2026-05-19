"""todo 工具：维护任务列表。"""

import json
import os
from datetime import datetime
from tools import Tool, ToolParameter


class TodoTool(Tool):
    """维护 todo 任务列表，支持增删改查。"""

    def __init__(self, storage_path: str = ".todo.json"):
        super().__init__("todo", "维护任务 todo 列表（添加/完成/列出/删除）")
        self.storage_path = storage_path
        self._todos = self._load()

    def get_parameters(self):
        return [
            ToolParameter(name="action", type="string", description="操作: add/done/list/remove"),
            ToolParameter(name="text", type="string", description="任务内容（add 时必填）", required=False, default=""),
            ToolParameter(name="index", type="integer", description="任务序号（done/remove 时必填）", required=False, default=None),
        ]

    def run(self, action: str, text: str = "", index: int = None, **kwargs) -> str:
        action = action.lower().strip()

        if action == "add":
            return self._add(text)
        elif action == "done":
            return self._done(index)
        elif action == "remove":
            return self._remove(index)
        elif action == "list":
            return self._list()
        else:
            return f"❌ 未知操作: {action}（支持: add/done/list/remove）"

    def _add(self, text: str) -> str:
        if not text:
            return "❌ 请提供任务内容"
        self._todos.append({
            "text": text,
            "done": False,
            "created": datetime.now().isoformat(),
        })
        self._save()
        return f"✅ 已添加: {text}（共 {len(self._todos)} 条）"

    def _done(self, index: int) -> str:
        if index is None or index < 1 or index > len(self._todos):
            return f"❌ 无效序号（当前共 {len(self._todos)} 条）"
        self._todos[index - 1]["done"] = True
        self._save()
        return f"✅ 已完成: {self._todos[index - 1]['text']}"

    def _remove(self, index: int) -> str:
        if index is None or index < 1 or index > len(self._todos):
            return f"❌ 无效序号（当前共 {len(self._todos)} 条）"
        removed = self._todos.pop(index - 1)
        self._save()
        return f"✅ 已删除: {removed['text']}"

    def _list(self) -> str:
        if not self._todos:
            return "📋 任务列表为空"
        lines = []
        for i, t in enumerate(self._todos, 1):
            status = "✅" if t["done"] else "⬜"
            lines.append(f"  {i}. {status} {t['text']}")
        return "📋 任务列表:\n" + "\n".join(lines)

    def _load(self) -> list:
        if os.path.isfile(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self._todos, f, ensure_ascii=False, indent=2)
