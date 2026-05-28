"""
练习 5.1 · read_file 工具
==========================

知识点：第 24 节《Coding Agent 工作流》

要求：补全 read_file 函数
  - 输入：file_path（str）、offset（可选起始行）、limit（可选读取行数）
  - 输出：带行号的文件内容字符串

格式要求：每行前面加行号，如：
  1: import os
  2: import sys
  3:
  4: def main():

错误处理：
  - 文件不存在 → 返回友好错误信息（不抛异常）
  - 不是文件（是目录） → 返回友好错误信息
"""

import os
import tempfile


def read_file(file_path: str, offset: int = 1, limit: int | None = None) -> str:
    """读取文件内容，返回带行号的字符串。

    Args:
        file_path: 文件路径
        offset: 从第几行开始（1-based）
        limit: 最多读几行（None 表示全部）
    """
    # TODO:
    #   1. 检查 file_path 是否存在，不存在返回 f"❌ 文件不存在: {file_path}"
    #   2. 检查是否是文件（不是目录），否则返回 f"❌ 不是文件: {file_path}"
    #   3. 读取文件所有行
    #   4. 按 offset 和 limit 切片（offset 是 1-based）
    #   5. 给每行加上行号前缀，格式: f"{lineno}: {line}"
    #   6. 拼接返回
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 创建临时测试文件
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    tmp.write("import os\nimport sys\n\ndef main():\n    print('hello')\n")
    tmp.close()

    try:
        # 测试 1：读取全部
        content = read_file(tmp.name)
        assert "1:" in content or "1 :" in content, "应该有行号"
        assert "import os" in content, "应该包含文件内容"
        lines = content.strip().split("\n")
        assert len(lines) == 5, f"应该有 5 行，实际: {len(lines)}"

        # 测试 2：offset + limit
        partial = read_file(tmp.name, offset=2, limit=2)
        assert "import sys" in partial, "offset=2 应该从第二行开始"
        partial_lines = partial.strip().split("\n")
        assert len(partial_lines) == 2, f"limit=2 应该只有 2 行，实际: {len(partial_lines)}"

        # 测试 3：文件不存在
        result = read_file("/nonexistent/path/file.txt")
        assert "❌" in result or "不存在" in result, f"应该返回错误信息，实际: {result!r}"

        # 测试 4：目录而非文件
        result = read_file(tempfile.gettempdir())
        assert "❌" in result or "不是文件" in result, f"目录应该报错，实际: {result!r}"

        # 测试 5：行号正确
        content = read_file(tmp.name, offset=3, limit=1)
        assert "3:" in content or "3 :" in content, "第三行的行号应该是 3"

        print("✅ PASSED: read_file 全部测试通过")
    finally:
        os.unlink(tmp.name)
