"""
Day 5 工具集 · list_dir：列目录内容

注意：函数名叫 list_dir 不叫 list（list 是 Python 内置类型，会撞名）。

设计要点：
  - 区分文件和目录（文件名前缀 [F]，目录前缀 [D]）
  - 隐藏文件默认不列（show_hidden=False）
  - 输出截断（避免大目录爆 messages，默认上限 200 项）
  - 排序稳定：目录在前，文件在后，各自字母序
"""

from __future__ import annotations

import os


def list_dir(path: str = ".", show_hidden: bool = False, max_items: int = 200) -> str:
    """列出目录的内容，文件 / 目录分类。"""
    if not os.path.isdir(path):
        return f"❌ 不是目录: {path}"

    try:
        items = os.listdir(path)
    except Exception as e:
        return f"❌ 读取目录失败: {e}"

    if not show_hidden:
        items = [n for n in items if not n.startswith(".")]

    dirs, files = [], []
    for n in items:
        full = os.path.join(path, n)
        if os.path.isdir(full):
            dirs.append(n)
        else:
            files.append(n)
    dirs.sort()
    files.sort()

    lines = []
    for d in dirs:
        lines.append(f"[D] {d}/")
    for f in files:
        try:
            size = os.path.getsize(os.path.join(path, f))
            lines.append(f"[F] {f}  ({size} bytes)")
        except OSError:
            lines.append(f"[F] {f}")

    truncated = ""
    if len(lines) > max_items:
        truncated = f"\n[...... 共 {len(lines)} 项，已截断显示前 {max_items} 项]"
        lines = lines[:max_items]

    header = f"# {os.path.abspath(path)}\n共 {len(dirs)} 个目录, {len(files)} 个文件\n"
    return header + "\n".join(lines) + truncated


if __name__ == "__main__":
    print(list_dir("."))
    print()
    print(list_dir("/nonexistent"))
