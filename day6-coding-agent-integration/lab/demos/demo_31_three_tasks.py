"""Demo 31：3 个真实任务 —— 用完整 CodingAgent 跑端到端。

任务 1：在当前目录建一个 hello_test/ 项目 + test_hello.py + 跑 pytest
任务 2：读一个有 bug 的文件，找到 bug，用 edit 修复
任务 3：故意刁难 —— 让 Agent 完成一件它"理论上做不到"的事

运行：python demo_31_three_tasks.py
"""

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "my_coding_agent"))

from agent import CodingAgent  # noqa: E402

# 创建一个临时工作区
WORKDIR = tempfile.mkdtemp(prefix="agent_demo31_")
print(f"📂 临时工作区: {WORKDIR}\n")


def run_task(agent: CodingAgent, title: str, user_input: str) -> None:
    print("=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)
    print(f"用户: {user_input}\n")
    reply = agent.chat(user_input)
    print(f"\n🤖 最终回答: {reply}\n\n")


def main():
    agent = CodingAgent(workdir=WORKDIR, verbose=True)

    # ---------- 任务 1：从零建项目 + 跑测试 ----------
    run_task(
        agent,
        "任务 1：建项目 + 跑测试",
        "请在工作区里创建一个 calculator.py（含 add/subtract 函数），"
        "再创建 test_calculator.py（用 assert 写两个测试），最后用 bash 跑 python -m pytest -v。",
    )

    # ---------- 任务 2：修 bug ----------
    # 先手动放一个有 bug 的文件
    buggy_file = os.path.join(WORKDIR, "buggy.py")
    with open(buggy_file, "w") as f:
        f.write('''\
def greet(name):
    """返回问候语"""
    return f"Hello, {namee}!"


def add(a, b):
    """两数相加"""
    return a - b  # 这里写反了
''')

    run_task(
        agent,
        "任务 2：修复 bug",
        f"请阅读 {buggy_file}，找出所有 bug 并修复。修完后跑一下确保没语法错误。",
    )

    # ---------- 任务 3：故意刁难 ----------
    run_task(
        agent,
        "任务 3：刁难题（Agent 应该诚实拒绝 / 或用现有工具变通）",
        "请帮我访问 https://example.com 并把网页内容保存到 page.html。",
    )

    # 清理
    print("\n🧹 清理临时目录...")
    shutil.rmtree(WORKDIR, ignore_errors=True)
    print("✅ Done!")


if __name__ == "__main__":
    main()
