"""edit 工具：精确替换文件中的已有内容。"""

import os
from tools import Tool, ToolParameter


class EditTool(Tool):
    """精确替换文件中的内容，要求 old_content 在文件中唯一。"""

    def __init__(self):
        super().__init__("edit", "精确替换文件中的已有内容（old_content 必须唯一）")

    def get_parameters(self):
        return [
            ToolParameter(name="path", type="string", description="文件路径"),
            ToolParameter(name="old_content", type="string", description="要替换的原始内容"),
            ToolParameter(name="new_content", type="string", description="替换后的新内容"),
        ]

    def run(self, path: str, old_content: str, new_content: str, **kwargs) -> str:
        if not os.path.isfile(path):
            return f"❌ 文件不存在: {path}"

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            count = content.count(old_content)
            if count == 0:
                return f"❌ 未找到匹配内容，请检查 old_content 是否正确"
            if count > 1:
                return f"❌ old_content 匹配了 {count} 处，请提供更多上下文使其唯一"

            new_file_content = content.replace(old_content, new_content, 1)

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_file_content)

            return f"✅ 已替换 {path} 中的内容"

        except Exception as e:
            return f"❌ 编辑失败: {e}"
