"""my_coding_agent 入口。

用法：
    cd day6-coding-agent-integration/lab/demos/my_coding_agent
    python main.py [工作目录]

默认工作目录 = 当前目录的上一级（即 demos/），方便直接操作 day6 的课程文件。
"""

import os
import sys

# 把当前目录加入 sys.path 让相对 import 正常工作
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import CodingAgent  # noqa: E402
from ui import run_repl  # noqa: E402


def main():
    # 命令行可选传入工作目录
    if len(sys.argv) > 1:
        workdir = sys.argv[1]
    else:
        workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Memory 持久化文件放在工作目录下
    memory_path = os.path.join(workdir, ".agent_memory.json")

    agent = CodingAgent(
        workdir=workdir,
        memory_path=memory_path,
        verbose=True,
    )
    run_repl(agent)


if __name__ == "__main__":
    main()
