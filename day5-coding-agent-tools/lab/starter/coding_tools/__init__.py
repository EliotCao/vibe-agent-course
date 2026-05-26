"""
Day 5 Lab · coding_tools 包入口

填好 5 个工具后，把它们 import 进来，跑下面的 self_test 应该全过。
"""

from .read import read
from .write import write
from .edit import edit
from .list_dir import list_dir
from .bash import bash


def self_test() -> None:
    """跑一遍 5 个工具的最小自测。"""
    import os
    import tempfile

    tmp = tempfile.mkdtemp()
    print(f"工作区: {tmp}\n")

    # 1) write
    p = os.path.join(tmp, "main.py")
    print("[1] write:", write(p, "def f():\n    return 1\n"))

    # 2) read
    print("[2] read:")
    print(read(p))

    # 3) edit
    print("\n[3] edit:", edit(p, "return 1", "return 42"))
    print(read(p))

    # 4) list_dir
    print("\n[4] list_dir:")
    print(list_dir(tmp))

    # 5) bash
    print("\n[5] bash:")
    print(bash(f"python {p} && echo OK", workdir=tmp))


if __name__ == "__main__":
    self_test()
