"""
Day 5 Lab · list_dir 骨架 —— 学生填空

要求：
  ① 不是目录 → 友好报错
  ② 区分文件和目录，文件前缀 [F]，目录前缀 [D]/
  ③ 默认不显示隐藏文件（.开头）
  ④ 文件后面带字节数

参考：demos/coding_tools/list_dir.py
"""

from __future__ import annotations

import os


def list_dir(path: str = ".", show_hidden: bool = False, max_items: int = 200) -> str:
    """列出目录内容。"""
    # TODO ① 校验是目录
    if ...:
        return ""

    # TODO ② 列举条目，过滤隐藏文件
    items: list[str] = []   # ← 你的代码

    # TODO ③ 分类：dirs / files，各自字母序
    dirs: list[str] = []    # ← 你的代码
    files: list[str] = []

    # TODO ④ 拼输出：[D] xxx/  / [F] xxx (123 bytes)
    return ""   # ← 你的代码


if __name__ == "__main__":
    print(list_dir("."))
    print(list_dir("/nonexistent"))
