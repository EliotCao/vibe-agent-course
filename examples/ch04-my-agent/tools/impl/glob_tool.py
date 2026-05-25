"""glob 工具：按 glob 模式匹配文件名。"""

import glob as glob_mod
import os
from tools import Tool, ToolParameter


class GlobTool(Tool):
    """按 glob 模式匹配文件，支持递归（**）。"""

    def __init__(self):
        super().__init__("glob", "按 glob 模式匹配文件名（支持 ** 递归）")

    def get_parameters(self):
        return [
            ToolParameter(name="pattern", type="string", description="glob 模式，如 '**/*.py'"),
            ToolParameter(name="path", type="string", description="搜索根目录", required=False, default="."),
        ]

    def run(self, pattern: str, path: str = ".", **kwargs) -> str:
        try:
            full_pattern = os.path.join(path, pattern)
            matches = sorted(glob_mod.glob(full_pattern, recursive=True))

            if not matches:
                return f"未找到匹配: {pattern}"

            # 转为相对路径
            results = [os.path.relpath(m, path) for m in matches]

            if len(results) > 200:
                results = results[:200]
                results.append(f"... (共匹配 {len(matches)} 个文件，已截断)")

            return "\n".join(results)

        except Exception as e:
            return f"❌ glob 失败: {e}"
