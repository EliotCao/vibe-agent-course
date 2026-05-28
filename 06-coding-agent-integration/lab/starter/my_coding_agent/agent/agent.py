"""starter/my_coding_agent/agent/agent.py —— 填空版。

把 Day1-Day5 的零件组装成完整 CodingAgent。
需要填写 4 个 TODO。
"""

from __future__ import annotations

import json
import os
import sys
from typing import Callable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import LLM, Message  # noqa: E402
from tools import build_registry  # noqa: E402
from context import ContextManager  # noqa: E402
from memory import Memory  # noqa: E402


SYSTEM_PROMPT = """\
你是一个专业的 Coding Agent，可以帮用户阅读、修改、运行代码。

# 工作流程
1. 先用 list_dir 看工作区有什么
2. 用 read 读相关文件理解现状
3. 用 write 创建新文件 / 用 edit 改已有文件
4. 用 bash 跑测试或脚本验证
5. 完成后给用户一句话总结你做了什么、为什么

# 注意
- write 默认拒绝覆盖已有文件，要改文件请用 edit
- edit 的 old_content 必须在文件中**唯一**出现
- 工具失败时会返回 ❌ 开头的错误信息，仔细看清楚再重试
"""


SUMMARY_PROMPT = """\
请把下面这段对话压缩成 100 字以内的中文摘要。
特别保留：用户偏好、硬约束、关键事实、未完成的任务。

对话：
{transcript}
"""


class CodingAgent:
    def __init__(self, workdir: str = ".", max_tool_rounds: int = 20):
        self.workdir = os.path.abspath(workdir)
        self.max_tool_rounds = max_tool_rounds

        # TODO 1: 实例化 6 个零件 —— LLM / ToolRegistry / ContextManager / Memory
        # 提示：
        #   self.llm = LLM()
        #   self.tools = build_registry(workdir=self.workdir)
        #   self.ctx = ContextManager(keep_last=10, max_messages=30, summarize_fn=self._summarize)
        #   self.memory = Memory(min_score=0.5)
        # ------
        raise NotImplementedError("TODO 1: 实例化 6 个零件")

        self.messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\n# 工作目录\n{self.workdir}"},
        ]

    def _summarize(self, middle: list[dict]) -> str:
        transcript = "\n".join(f"{m.get('role')}: {m.get('content','')[:200]}" for m in middle)
        msg = self.llm.chat(
            messages=[{"role": "user", "content": SUMMARY_PROMPT.format(transcript=transcript)}],
        )
        return (msg.content or "").strip()

    def chat(self, user_input: str) -> str:
        # TODO 2: 在 messages 里加 user_input 之前，先从 Memory 召回相关事实
        # 提示：if len(self.memory): relevant = self.memory.search(user_input, k=3)
        # ------

        self.messages.append({"role": "user", "content": user_input})

        # 必要时压缩
        if self.ctx.should_compress(self.messages):
            self.messages = self.ctx.compress(self.messages)

        # TODO 3: Agent Loop —— 循环调 LLM，有 tool_calls 就执行、追加 tool 消息、再调 LLM
        # 提示：
        #   for turn in range(1, self.max_tool_rounds + 1):
        #       resp = self.llm.chat(messages=self.messages, tools=self.tools.to_schemas())
        #       if not resp.tool_calls: break
        #       ... 把 assistant 消息加入 messages ...
        #       ... 遍历 tool_calls、invoke、追加 tool 消息 ...
        # ------
        raise NotImplementedError("TODO 3: Agent Loop")

        # TODO 4: 循环结束后，把 resp.content 加入 messages 并 return
        raise NotImplementedError("TODO 4: 返回最终回答")
