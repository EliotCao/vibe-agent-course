"""
Day 5 Lab Part 2 · write 骨架 —— 填空

写新文件 / 覆盖文件。注意：默认拒绝覆盖已有文件！

参考：demos/coding_tools/write.py
"""

from __future__ import annotations

import os


def write(path: str, content: str, overwrite: bool = False) -> str:
    """新建文件或覆盖。"""
    # TODO ① 安全约束：文件已存在且 overwrite=False → 拒绝
    if ...:
        return "❌ ..."   # ← 你的代码

    # TODO ② 自动创建父目录（mkdir -p）
    parent = os.path.dirname(path)
    # ← 你的代码

    # TODO ③ 写入，捕获异常
    # ← 你的代码
    return f"✅ 已写入 {path}（{len(content)} 字符）"


if __name__ == "__main__":
    import tempfile
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "demo/x.txt")
    print(write(p, "hello"))
    print(write(p, "覆盖测试"))   # 应被拒
    print(write(p, "覆盖测试", overwrite=True))   # OK
