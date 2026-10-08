"""
Demo 26 · 端到端：让 LLM 用 5 个工具完成一个真实任务
=====================================================

把 第2章 的 Agent Loop + 第5章 的 5 个工具拼起来。
任务："在工作区里创建一个简单的 Python 计算器，并跑通它"

观察：
  - LLM 会怎么编排 list / read / write / edit / bash 五个工具
  - 哪一步 LLM 出错了？怎么自己纠正？
  - 完整跑下来要几轮？

跑法：
    python demo_26_end_to_end.py
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile

from coding_tools import build_registry
from _env import get_model_id, make_client


SYSTEM_PROMPT = """你是一个 Coding Agent。用工具完成用户的编程任务。

# 工作流程
1. 先用 list_dir 看工作区有什么
2. 用 read 读已有文件理解现状
3. 用 write 创建新文件 / 用 edit 改已有文件
4. 用 bash 跑测试验证

# 注意
- write 工具不能修改已有文件，会报错；改文件请用 edit
- edit 的 old_content 必须在文件中唯一出现
- 完成后给用户一句话总结
"""


def run_coding_agent(question: str, workdir: str, max_iters: int = 12) -> str:
    client = make_client()
    MODEL = get_model_id()
    registry = build_registry()

    # 把 bash 的默认 workdir 锁定到工作区
    # 简单做法：让 system prompt 告诉模型"用 bash 时记得传 workdir"
    sys_prompt = SYSTEM_PROMPT + f"\n# 工作目录\n请所有文件操作都使用绝对路径，cwd={workdir}"

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": question},
    ]

    for turn in range(1, max_iters + 1):
        print(f"\n========== 第 {turn} 轮 ==========")
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=registry.to_schemas(),
            tool_choice="auto",
            temperature=0,
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            print(f"\n🎯 模型给出最终回答")
            print(msg.content)
            return msg.content or ""

        if msg.content:
            print(f"💭 思考: {msg.content}")

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name,
                              "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"⚡ 调用 {tc.function.name}({args})")
            result = registry.invoke(tc.function.name, args)
            short = result[:200] + ("..." if len(result) > 200 else "")
            print(f"   → {short}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "⚠️ 达到最大轮次"


if __name__ == "__main__":
    workdir = tempfile.mkdtemp(prefix="05_e2e_")
    print(f"📁 工作区: {workdir}")

    task = (
        f"请在 {workdir} 里创建一个 Python 文件 calculator.py，"
        "实现一个支持 add / sub / mul / div 四则运算的 Calculator 类，"
        "然后再创建一个 test_calc.py 写 4 个简单测试，"
        "最后用 python -m unittest 跑一遍测试，确认全部通过。"
    )
    run_coding_agent(task, workdir, max_iters=15)

    print(f"\n📁 最终工作区文件：")
    for root, dirs, files in os.walk(workdir):
        for f in files:
            print(f"  - {os.path.relpath(os.path.join(root, f), workdir)}")

    print("\n💡 删除工作区？")
    print(f"   rm -rf {workdir}")
