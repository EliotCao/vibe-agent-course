"""read 工具：读取文件内容，返回带行号的文本。"""

import os
from tools import Tool, ToolParameter


class ReadTool(Tool):
    """读取文件内容，支持 offset/limit/max_bytes。"""

    def __init__(self):
        super().__init__("read", "读取文件内容，返回带行号的文本")

    def get_parameters(self):
        return [
            ToolParameter(name="path", type="string", description="文件路径"),
            ToolParameter(name="offset", type="integer", description="起始行号（从 1 开始）", required=False, default=1),
            ToolParameter(name="limit", type="integer", description="读取行数", required=False, default=None),
            ToolParameter(name="max_bytes", type="integer", description="最大读取字节数", required=False, default=100000),
        ]

    def run(self, path: str, offset: int = 1, limit: int = None, max_bytes: int = 100000, **kwargs) -> str:
        if not os.path.isfile(path):
            return f"❌ 文件不存在: {path}"

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(max_bytes)

            lines = content.splitlines()
            start = max(0, offset - 1)
            end = start + limit if limit else len(lines)
            selected = lines[start:end]

            # 带行号输出
            width = len(str(end))
            numbered = [f"{i:>{width}}:{line}" for i, line in enumerate(selected, start=start + 1)]
            return "\n".join(numbered)

        except Exception as e:
            return f"❌ 读取失败: {e}"
