"""最小 REPL UI（讲义第 29 节 · 模式 A：终端 REPL）。

循环：读输入 → agent.chat → 打印输出 → 重复。
退出：输入 exit / quit / 空行。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent import CodingAgent


def run_repl(agent: "CodingAgent") -> None:
    """阻塞式运行一个简单的终端 REPL。"""
    print("\n\U0001f916 Coding Agent 已启动（输入 exit 退出）")
    print(f"\U0001f4c2 工作目录: {agent.workdir}\n")
    while True:
        try:
            user_input = input("\U0001f9d1 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\U0001f44b 再见！")
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            print("\U0001f44b 再见！")
            break

        print()  # 空行分隔
        reply = agent.chat(user_input)
        print(f"\n\U0001f916 Agent: {reply}\n")
