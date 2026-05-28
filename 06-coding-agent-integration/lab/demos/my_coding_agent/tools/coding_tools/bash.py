"""
Day 5 工具集 · bash：在工作区内跑 shell 命令

四道安全闸门（讲义第 25 节）：
  ① 超时：默认 30s，防止挂死
  ② 输出截断：默认 50KB，防止爆 messages
  ③ 工作目录限定：cwd 限制在传入的 workdir 内
  ④ 危险命令拦截：rm -rf / sudo / curl 远程脚本 等关键字

注意：这是一个**最小演示版**，真生产应该再加：
  - 不允许写到 cwd 外
  - 命令白名单 / 黑名单可配置
  - subprocess 用 shell=False + 解析参数
  - 完全沙箱化（容器 / Firejail）
"""

from __future__ import annotations

import os
import re
import subprocess


# 一些"明显危险"的模式，命中就直接拒绝
DANGER_PATTERNS = [
    r"\brm\s+-rf\s+/",          # 整盘删除
    r"\bsudo\b",                # 提权
    r"\bdd\s+if=",              # 写盘
    r"\b(curl|wget)\s+.*\|\s*(sh|bash)",   # 远程脚本下载执行
    r":\s*\(\s*\)\s*\{\s*:",    # fork 炸弹
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
]


def _is_dangerous(command: str) -> str | None:
    """命中某条危险模式就返回该模式描述；安全则返回 None。"""
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
    """在工作区内执行 shell 命令并返回输出（含 stdout、stderr、exit code）。"""
    cwd = workdir or os.getcwd()
    if not os.path.isdir(cwd):
        return f"❌ 工作目录不存在: {cwd}"

    danger = _is_dangerous(command)
    if danger:
        return f"❌ 拦截危险命令模式: {danger}"

    try:
        result = subprocess.run(
            ["/bin/sh", "-lc", command],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return f"❌ 命令超时（{timeout}s）: {command}"
    except Exception as e:
        return f"❌ 执行失败: {e}"

    parts = []
    if result.stdout:
        parts.append(result.stdout[:max_output])
        if len(result.stdout) > max_output:
            parts.append(f"\n[stdout 截断, 实际 {len(result.stdout)} 字节]")
    if result.stderr:
        parts.append(f"[stderr]\n{result.stderr[:max_output]}")
    out = "\n".join(parts) if parts else "(无输出)"

    if result.returncode != 0:
        out = f"[exit code: {result.returncode}]\n{out}"
    return out


if __name__ == "__main__":
    print(bash("pwd"))
    print()
    print(bash("ls / | head -5"))
    print()
    print(bash("rm -rf /"))   # 应该被拦截
    print()
    print(bash("sleep 100", timeout=2))   # 应该超时
