"""
Day 5 Lab Part 2 · bash 骨架 —— 学生填空

四道闸门（讲义第 25 节）：
  ① 超时
  ② 输出截断
  ③ 工作目录限定
  ④ 危险命令拦截（黑名单）

参考：demos/coding_tools/bash.py
"""

from __future__ import annotations

import os
import re
import subprocess


# TODO ① 至少列 3 条危险模式（建议覆盖 rm -rf / sudo / 远程脚本下载执行）
DANGER_PATTERNS: list[str] = [
    # ← 你的代码
]


def _is_dangerous(command: str) -> str | None:
    for pat in DANGER_PATTERNS:
        if re.search(pat, command):
            return pat
    return None


def bash(
    command: str,
    workdir: str | None = None,
    timeout: int = 30,
    max_output: int = 50_000,
) -> str:
    cwd = workdir or os.getcwd()
    if not os.path.isdir(cwd):
        return f"❌ 工作目录不存在: {cwd}"

    # TODO ② 危险命令拦截
    danger = _is_dangerous(command)
    if danger:
        return f"❌ 拦截危险命令: {danger}"

    # TODO ③ 调用 subprocess.run，传 timeout / capture_output / text
    # 捕获 TimeoutExpired 返回友好错误
    try:
        result = subprocess.run(
            ...,   # ← 你的代码
        )
    except subprocess.TimeoutExpired:
        return f"❌ 命令超时（{timeout}s）"

    # TODO ④ 拼输出：stdout + stderr + exit code，超过 max_output 截断
    return ""   # ← 你的代码


if __name__ == "__main__":
    print(bash("pwd"))
    print(bash("ls / | head -3"))
    print(bash("rm -rf /"))   # 应被拦
    print(bash("sleep 5", timeout=2))   # 应超时
