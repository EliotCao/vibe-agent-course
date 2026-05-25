"""grep 工具：在文件内容中搜索文本或正则。"""

import os
import re
from tools import Tool, ToolParameter


class GrepTool(Tool):
    """在文件中搜索文本或正则，返回 file:line: content 格式。"""

    def __init__(self):
        super().__init__("grep", "在文件中搜索文本或正则表达式")

    def get_parameters(self):
        return [
            ToolParameter(name="pattern", type="string", description="搜索模式（支持正则）"),
            ToolParameter(name="path", type="string", description="搜索路径（文件或目录）"),
            ToolParameter(name="recursive", type="boolean", description="是否递归搜索目录", required=False, default=True),
            ToolParameter(name="max_results", type="integer", description="最大返回条数", required=False, default=50),
        ]

    def run(self, pattern: str, path: str, recursive: bool = True, max_results: int = 50, **kwargs) -> str:
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return f"❌ 无效正则: {e}"

        results = []

        if os.path.isfile(path):
            results = self._search_file(path, regex, max_results)
        elif os.path.isdir(path):
            results = self._search_dir(path, regex, recursive, max_results)
        else:
            return f"❌ 路径不存在: {path}"

        if not results:
            return f"未找到匹配: {pattern}"

        return "\n".join(results)

    def _search_file(self, filepath: str, regex, max_results: int) -> list:
        results = []
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, 1):
                    if regex.search(line):
                        results.append(f"{filepath}:{i}: {line.rstrip()}")
                        if len(results) >= max_results:
                            break
        except (IOError, OSError):
            pass
        return results

    def _search_dir(self, dirpath: str, regex, recursive: bool, max_results: int) -> list:
        results = []
        for root, dirs, files in os.walk(dirpath):
            # 跳过隐藏目录和常见无关目录
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".git")]
            for fname in sorted(files):
                if fname.startswith("."):
                    continue
                filepath = os.path.join(root, fname)
                results.extend(self._search_file(filepath, regex, max_results - len(results)))
                if len(results) >= max_results:
                    results.append(f"... (已达到 {max_results} 条上限)")
                    return results
            if not recursive:
                break
        return results
