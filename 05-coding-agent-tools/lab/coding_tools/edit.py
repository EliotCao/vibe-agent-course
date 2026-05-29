"""
第5章工具集 · edit：精确替换已有文件中的一段文本

为什么不用行号？
  - LLM 看到的是文本，不是行号
  - 任何修改都会让后面的行号偏移，多步编辑时崩溃
  - old/new 替换是"按内容定位"，永远精确

唯一性约束：
  - old_content 必须在文件中**只出现一次**，否则不知道改哪个
  - 出现 0 次 → 模型搞错了
  - 出现 N 次 → 让模型加更多上下文使其唯一
"""

from __future__ import annotations

import os


def edit(path: str, old_content: str, new_content: str) -> str:
    """精确替换文件中的一段内容。

    参数：
      path: 文件路径
      old_content: 要被替换的原内容（必须在文件中唯一出现）
      new_content: 替换后的新内容
    """
    if not os.path.isfile(path):
        return f"❌ 文件不存在: {path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"❌ 读取失败: {e}"

    count = content.count(old_content)
    if count == 0:
        return (
            f"❌ 未找到匹配内容: {path}\n"
            "   提示：请用 read 工具确认文件当前内容，"
            "old_content 必须**逐字符**对得上（含空格、缩进、换行）"
        )
    if count > 1:
        return (
            f"❌ old_content 在文件中出现 {count} 次，无法确定改哪一处\n"
            "   提示：请把 old_content 加更多上下文（前后多取几行），"
            "让它在文件中唯一"
        )

    new_full = content.replace(old_content, new_content, 1)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_full)
        return f"✅ 已替换 {path} 中的内容"
    except Exception as e:
        return f"❌ 写入失败: {e}"


if __name__ == "__main__":
    import tempfile

    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "code.py")
    with open(p, "w", encoding="utf-8") as f:
        f.write("def hello():\n    print('hi')\n\nhello()\n")

    print(edit(p, "print('hi')", "print('hi, 05!')"))
    print(open(p).read())
    print()
    print(edit(p, "不存在的内容", "xxx"))   # ❌ 未找到
    print()
    print(edit(p, "(", "[ "))   # ❌ 多次匹配
