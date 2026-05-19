"""write 工具：写入文件，自动创建父目录。"""

import os
from tools import Tool, ToolParameter


class WriteTool(Tool):
    """写入文件内容，支持覆盖或追加模式。"""

    def __init__(self):
        super().__init__("write", "写入文件内容，自动创建父目录，支持覆盖或追加")

    def get_parameters(self):
        return [
            ToolParameter(name="path", type="string", description="文件路径"),
            ToolParameter(name="content", type="string", description="要写入的内容"),
            ToolParameter(name="append", type="boolean", description="是否追加模式", required=False, default=False),
        ]

    def run(self, path: str, content: str, append: bool = False, **kwargs) -> str:
        try:
            # 自动创建父目录
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)

            mode = "a" if append else "w"
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)

            action = "追加" if append else "写入"
            return f"✅ 已{action}到 {path}（{len(content)} 字符）"

        except Exception as e:
            return f"❌ 写入失败: {e}"
