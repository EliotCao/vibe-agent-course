"""
Demo 24 · 五阶段工作流：手动跑一遍 Coding Agent 的"思考路径"
============================================================

配套：第 24 节《Coding Agent 的工作模式》

让你**不用 LLM 也能感受 Agent 写代码的步骤**。
我们手动按"浏览 → 定位 → 理解 → 修改 → 验证"五步，调用 5 个工具，
完成一个真实任务："给 demo_xxx.py 加一句开场打印"。

这个 demo 的目的：
  - 让你看到：每一步对应的是哪个工具
  - 让你看到：工具的输出长什么样、模型怎么基于它决定下一步
  - 第 25 节会讲清这些工具背后的设计哲学

跑法：
    python demo_24_five_stages.py
"""

from __future__ import annotations

import os
import shutil
import tempfile

from coding_tools import bash, edit, list_dir, read, write


def main() -> None:
    # ============================================================
    # 准备：创建一个临时工作区，模拟一个小项目
    # ============================================================
    workspace = tempfile.mkdtemp(prefix="day5_demo_")
    print(f"📁 工作区: {workspace}\n")

    # 写两个示例文件
    write(os.path.join(workspace, "main.py"), "def greet():\n    print('hello')\n\ngreet()\n")
    write(os.path.join(workspace, "utils.py"), "def add(a, b):\n    return a + b\n")

    # ============================================================
    # 阶段 ① 浏览：用 list_dir 看看项目里有什么
    # ============================================================
    print("=" * 60)
    print("阶段 ① 浏览  —  用 list_dir 看看有什么文件")
    print("=" * 60)
    print(list_dir(workspace))

    # ============================================================
    # 阶段 ② 定位 + ③ 理解：用 read 看 main.py 内容
    # ============================================================
    print("\n" + "=" * 60)
    print("阶段 ② 定位 + ③ 理解  —  用 read 看 main.py")
    print("=" * 60)
    print(read(os.path.join(workspace, "main.py")))

    # ============================================================
    # 阶段 ④ 修改：用 edit 在 greet() 里加一句 print
    # ============================================================
    print("\n" + "=" * 60)
    print("阶段 ④ 修改  —  用 edit 给 greet 函数加一句开场")
    print("=" * 60)
    result = edit(
        os.path.join(workspace, "main.py"),
        old_content="def greet():\n    print('hello')",
        new_content="def greet():\n    print('=== Day5 Demo ===')\n    print('hello')",
    )
    print(result)

    print("\n修改后的文件：")
    print(read(os.path.join(workspace, "main.py")))

    # ============================================================
    # 阶段 ⑤ 验证：用 bash 跑一下，看输出对不对
    # ============================================================
    print("\n" + "=" * 60)
    print("阶段 ⑤ 验证  —  用 bash 跑一下脚本")
    print("=" * 60)
    print(bash("python main.py", workdir=workspace))

    # ============================================================
    # 收尾
    # ============================================================
    print("\n" + "=" * 60)
    print("🎯 关键观察")
    print("=" * 60)
    print("  ① 五个阶段在脑子里串起来 = Coding Agent 的'思考路径'")
    print("  ② 每个阶段的工具输出，**都是下一步决策的输入**")
    print("     - list 输出 → 决定 read 哪个文件")
    print("     - read 输出 → 决定 edit 改哪一段")
    print("     - bash 输出 → 决定要不要再修一轮")
    print("  ③ 把上面整段流程喂给 LLM + tool_calls 协议，就成了 Day6 的真 Agent")

    # 清理
    shutil.rmtree(workspace)


if __name__ == "__main__":
    main()
