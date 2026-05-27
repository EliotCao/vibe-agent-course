"""
Day 5 工具集 · 选做：grep（正则搜文本）

只是一个 ripgrep / grep -rn 的简化版，方便老师课堂演示。
真生产里直接用 ripgrep 调 bash 工具更快、功能更全。
"""

from __future__ import annotations

import os
import re


def grep(pattern: str, path: str = ".", file_glob: str = "*", max_matches: int = 100) -> str:
    """递归搜索包含 pattern 的行。

    参数：
      pattern: 正则表达式
      path: 起始目录
      file_glob: 简易通配（暂只支持 *.ext / *）
      max_matches: 最多返回多少行
    """
    if not os.path.isdir(path):
        return f"❌ 不是目录: {path}"
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return f"❌ 正则非法: {e}"

    ext = None
    if file_glob.startswith("*."):
        ext = file_glob[1:]   # ".py"

    results: list[str] = []
    for root, dirs, files in os.walk(path):
        # 跳过常见的"垃圾目录"
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv"}]
        for f in files:
            if ext and not f.endswith(ext):
                continue
            full = os.path.join(root, f)
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as fp:
                    for i, line in enumerate(fp, 1):
                        if rx.search(line):
                            results.append(f"{full}:{i}: {line.rstrip()}")
                            if len(results) >= max_matches:
                                results.append(f"\n[...... 已达 {max_matches} 上限]")
                                return "\n".join(results)
            except Exception:
                continue

    return "\n".join(results) if results else "(无匹配)"


if __name__ == "__main__":
    print(grep("def ", path=".", file_glob="*.py", max_matches=10))
