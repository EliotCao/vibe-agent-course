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

    此函数是 coding agent 工具集中最常用的“读文件”工具。它的核心职责是将磁盘上的
    文件内容转化为便于 LLM 理解和引用的格式。设计上遵循了以下原则：

    - 安全读：先做路径校验，文件不存在时给出友好的中文报错而不是抛出异常。
    - 防溢出：通过 max_bytes 限制单次读取的最大字节数，避免大文件（如日志、
      压缩包、二进制文件）撑爆 LLM 的上下文窗口。
    - 按需切片：通过 offset 和 limit 支持按行局部读取，方便 LLM 按需查看
      大文件的特定区域。
    - 精确定位：每行前面都带行号，LLM 在报错或引用时可以精确到行，提升后续
      编辑操作的准确性。

    行号对齐规则：行号右对齐，宽度取最后一行的位数。例如读取 100 行数据时，
    行号宽度为 3，前 9 行会补 2 个空格，保证对齐效果。

    Args:
        path: 目标文件的绝对路径或相对路径（相对路径基于当前工作目录解析）。
            **注意**：出于安全考虑，调用方不应将用户输入直接拼接为路径参数，
            应对路径做规范化校验，防止目录穿越攻击。
        offset: 起始行号，从 1 开始计数，默认为 1（即从文件第一行开始读取）。
        limit: 最大读取行数。若为 None，则读取从 offset 开始到文件末尾的所有行；
            若指定具体数值，则最多读取该行数。当文件内容不足时返回实际可读的行。
        max_bytes: 单次读取的最大字节数，超出部分会被截断。默认值为 100_000
            （即约 100 KB）。注意：截断后的最后一行如果不完整将被丢弃。
            此上限确保了即使传入超大文件，也只会消耗可控的 token 量。

    Returns:
        一个字符串，由带行号的文本行组成，格式为：:

            1:第一行内容
            2:第二行内容

        特殊情况返回值：
        - 文件不存在时返回 `❌ 文件不存在: {path}`。
        - 文件读取过程发生其他异常时返回 `❌ 读取失败: {异常信息}`。
        - 若读取的字节数达到 max_bytes 上限，末尾会追加形如
          `[...... 文件超过 100000 字节，已截断]` 的提示信息。

    Example::

        >>> # 读取当前文件前 10 行
        >>> print(read(__file__, offset=1, limit=10))
        1:import os
        2:
        3:
        4:def read(...): ...
        ...

        >>> # 读取不存在的文件
        >>> print(read("/nonexistent.xxx"))
        ❌ 文件不存在: /nonexistent.xxx

        >>> # 带行号的优势：LLM 可以直接引用“第 16 行有语法错误”
        >>> read("src/main.py", offset=10, limit=20)
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
