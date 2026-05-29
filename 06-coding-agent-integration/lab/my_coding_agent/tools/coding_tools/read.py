"""
第5章工具集 · read：读文件，带行号输出

设计要点：
  - 路径校验（文件不存在友好报错）
  - 大小限制（默认 max_bytes=100KB，避免大文件爆 messages）
  - offset/limit（按行切片，方便看大文件局部）
  - 输出带行号（让 LLM 报错时能精确指位置）
"""

from __future__ import annotations

import os


def read(path: str, offset: int = 1, limit: int | None = None, max_bytes: int = 100_000) -> str:
    """读取文件内容，返回带行号的文本。

    参数：
      path: 文件路径
      offset: 起始行号（从 1 开始）
      limit: 最多读多少行（None = 全部）
      max_bytes: 最多读多少字节，超出截断（默认 100KB）

    返回：带行号的字符串，如：
        1:第一行内容
        2:第二行内容
    """
    if not os.path.isfile(path):
        return f"❌ 文件不存在: {path}"

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)
    except Exception as e:
        return f"❌ 读取失败: {e}"

    lines = content.splitlines()
    start = max(0, offset - 1)
    end = start + limit if limit else len(lines)
    selected = lines[start:end]

    width = len(str(end))
    numbered = [f"{i:>{width}}:{line}" for i, line in enumerate(selected, start=start + 1)]
    body = "\n".join(numbered)

    truncated_note = ""
    if len(content) >= max_bytes:
        truncated_note = f"\n[...... 文件超过 {max_bytes} 字节，已截断]"

    return body + truncated_note


if __name__ == "__main__":
    # 自测
    print(read(__file__, offset=1, limit=10))
    print()
    print("===")
    print(read("/etc/hosts"))   # macOS / Linux 常有
    print()
    print("===")
    print(read("/nonexistent.xxx"))   # 错误路径
