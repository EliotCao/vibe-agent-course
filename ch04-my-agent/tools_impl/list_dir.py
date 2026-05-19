"""list 工具：列出目录内容。"""

import os
from tools import Tool, ToolParameter


class ListTool(Tool):
    """列出目录内容，支持递归和显示隐藏文件。"""

    def __init__(self):
        super().__init__("list", "列出目录内容，支持递归和显示隐藏文件")

    def get_parameters(self):
        return [
            ToolParameter(name="path", type="string", description="目录路径"),
            ToolParameter(name="recursive", type="boolean", description="是否递归", required=False, default=False),
            ToolParameter(name="show_hidden", type="boolean", description="是否显示隐藏文件", required=False, default=False),
        ]

    def run(self, path: str, recursive: bool = False, show_hidden: bool = False, **kwargs) -> str:
        if not os.path.isdir(path):
            return f"❌ 目录不存在: {path}"

        try:
            results = []
            if recursive:
                for root, dirs, files in os.walk(path):
                    if not show_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]
                        files = [f for f in files if not f.startswith(".")]
                    for f in sorted(files):
                        rel_path = os.path.relpath(os.path.join(root, f), path)
                        results.append(rel_path)
                    if len(results) > 500:
                        results.append("... (超过 500 条，已截断)")
                        break
            else:
                entries = sorted(os.listdir(path))
                if not show_hidden:
                    entries = [e for e in entries if not e.startswith(".")]
                for entry in entries:
                    full = os.path.join(path, entry)
                    suffix = "/" if os.path.isdir(full) else ""
                    results.append(f"{entry}{suffix}")

            return "\n".join(results) if results else "（空目录）"

        except Exception as e:
            return f"❌ 列目录失败: {e}"
