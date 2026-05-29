"""coding_tools：5 个必做 + 1 个选做工具。

来自 第5章。第6章 整合时**原样使用**，不修改任何工具实现。
"""

from .read import read
from .write import write
from .edit import edit
from .list_dir import list_dir
from .bash import bash
from .grep import grep

__all__ = ["read", "write", "edit", "list_dir", "bash", "grep"]
