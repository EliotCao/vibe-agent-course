"""
练习 5.2 · write_file 工具
============================

知识点：第 24-25 节《Coding Agent 工具设计》

要求：补全 write_file 函数
  - 输入：file_path、content、overwrite（默认 False）
  - 输出：成功/失败的提示信息

安全设计：
  - 默认不覆盖已有文件（除非 overwrite=True）
  - 自动创建父目录（mkdir -p）
"""

import os
import tempfile
import shutil


def write_file(file_path: str, content: str, overwrite: bool = False) -> str:
    """写入文件内容。

    Args:
        file_path: 目标文件路径
        content: 要写入的内容
        overwrite: 是否允许覆盖已有文件

    Returns:
        成功或失败的提示信息。
    """
    # TODO:
    #   1. 如果文件已存在 且 overwrite=False → 返回 f"❌ 文件已存在: {file_path}（如需覆盖请设 overwrite=True）"
    #   2. 自动创建父目录: os.makedirs(os.path.dirname(file_path), exist_ok=True)
    #      注意：dirname 可能为空字符串（当前目录），需要判断
    #   3. 写入文件
    #   4. 返回 f"✅ 已写入 {file_path}（{len(content)} 字符）"
    raise NotImplementedError("请补全此函数")


# ============================================================
# 测试（不要修改）
# ============================================================
if __name__ == "__main__":
    # 用临时目录做测试
    test_dir = tempfile.mkdtemp()

    try:
        # 测试 1：写新文件
        path1 = os.path.join(test_dir, "hello.txt")
        result = write_file(path1, "Hello, World!")
        assert "✅" in result, f"写新文件应该成功，实际: {result}"
        assert os.path.exists(path1), "文件应该被创建"
        assert open(path1).read() == "Hello, World!", "文件内容应该正确"

        # 测试 2：默认不覆盖
        result = write_file(path1, "New content")
        assert "❌" in result or "已存在" in result, f"默认不应覆盖，实际: {result}"
        assert open(path1).read() == "Hello, World!", "原内容不应该被改变"

        # 测试 3：overwrite=True 覆盖
        result = write_file(path1, "New content", overwrite=True)
        assert "✅" in result, f"overwrite=True 应该成功，实际: {result}"
        assert open(path1).read() == "New content", "内容应该被更新"

        # 测试 4：自动创建父目录
        deep_path = os.path.join(test_dir, "a", "b", "c", "deep.txt")
        result = write_file(deep_path, "deep content")
        assert "✅" in result, f"应该自动创建父目录，实际: {result}"
        assert os.path.exists(deep_path), "深层文件应该被创建"

        # 测试 5：返回字符数
        path5 = os.path.join(test_dir, "count.txt")
        result = write_file(path5, "12345")
        assert "5" in result, f"应该提示字符数，实际: {result}"

        print("✅ PASSED: write_file 全部测试通过")
    finally:
        shutil.rmtree(test_dir)
