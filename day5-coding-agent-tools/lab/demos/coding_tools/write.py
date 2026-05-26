"""
Day 5 工具集 · write：写新文件 / 完整覆盖文件

设计要点：
  - **不能用来改已有文件** —— 改用 edit 工具（更精确、不会无意覆盖）
  - 默认创建父目录（mkdir -p 等价物）
  - 已存在文件时强制要求 overwrite=True，避免误覆盖
"""

from __future__ import annotations

import os


def write(path: str, content: str, overwrite: bool = False) -> str:
    """新建文件或完整覆盖。

    参数：
      path: 文件路径
      content: 文件内容
      overwrite: 已存在文件时是否覆盖（默认 False，安全优先）
    """
    if os.path.isfile(path) and not overwrite:
        return (
            f"❌ 文件已存在: {path}\n"
            "   如需修改请用 edit；如需强制覆盖请传 overwrite=True"
        )

    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        try:
            os.makedirs(parent, exist_ok=True)
        except Exception as e:
            return f"❌ 创建父目录失败: {e}"

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 已写入 {path}（{len(content)} 字符）"
    except Exception as e:
        return f"❌ 写入失败: {e}"


if __name__ == "__main__":
    import tempfile

    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "demo/hello.txt")

    print(write(p, "Hello, Day5!"))     # ✅ 创建
    print(write(p, "新内容"))             # ❌ 已存在
    print(write(p, "新内容", overwrite=True))   # ✅ 覆盖
