"""
Day 5 Lab Part 2 · edit 骨架 —— 填空

精确替换：必须 old_content 唯一匹配。

参考：第 25 节 + demos/coding_tools/edit.py
"""

from __future__ import annotations

import os


def edit(path: str, old_content: str, new_content: str) -> str:
    """精确替换。"""
    # TODO ① 路径校验
    if ...:
        return "❌ ..."

    # TODO ② 读现有文件
    content = ""   # ← 你的代码

    # TODO ③ 校验 old_content 出现次数：
    #   - 0 次 → 报错"未找到匹配"
    #   - >1 次 → 报错"多次匹配，请加上下文使其唯一"
    #   - 1 次 → 替换 + 写回
    count = content.count(old_content)
    if count == 0:
        return "❌ ..."
    if count > 1:
        return "❌ ..."

    # TODO ④ 替换 + 写回
    new_full = ""   # ← 你的代码
    # ← 写回

    return f"✅ 已替换 {path} 中的内容"


if __name__ == "__main__":
    import tempfile, os as _os
    tmp = tempfile.mkdtemp()
    f = _os.path.join(tmp, "code.py")
    open(f, "w").write("def hi():\n    print('a')\n")
    print(edit(f, "print('a')", "print('b')"))
    print(open(f).read())
