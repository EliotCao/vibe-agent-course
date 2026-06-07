"""CodingAgent：把 第1章-第5章 的 6 个零件组装起来。

数据流（讲义第 28 节）：
    user_input
        → Memory.search           召回长期事实
        → ContextManager.compress 必要时压缩 messages
        → LLM.chat                第1章+第2章 协议
        → ToolRegistry.invoke     第5章 工具
        → 回灌到 messages
        → 给最终回答
        → Memory.distill          提炼新事实写回（可选）

整个 Agent 类不到 120 行，因为重活全在 6 个零件里。
"""

from __future__ import annotations

import json
import os
from typing import Callable

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm import LLM, Message, ToolCall  # noqa: E402
from tools import ToolRegistry, build_registry  # noqa: E402
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
- 工具失败时会返回 ❌ 开头的错误信息，请仔细看清楚再重试

# 思考方式
每次调工具前，请用 1-2 句话先说"你想做什么、为什么"，再调工具。
"""


SUMMARY_PROMPT = """\
请把下面这段对话压缩成 100 字以内的中文摘要。
**特别保留**：用户偏好、硬约束、关键事实、未完成的任务。
**可以丢弃**：客套话、重复确认、解释性回复。

对话：
{transcript}
"""


DISTILL_PROMPT = """\
阅读下面的对话，提炼出**值得长期记住的用户偏好、约束、关键事实**，
每条一行。如果没有可记的事实就输出空。

对话：
{transcript}

# 输出格式
每行一条事实，纯文本，无序号
"""


def _format_facts(relevant) -> str:
    return "[长期记忆中相关事实]\n" + "\n".join(f"- {e.text}" for _, e in relevant)


class CodingAgent:
    def __init__(
        self,
        workdir: str = ".",
        system_prompt: str = SYSTEM_PROMPT,
        max_tool_rounds: int = 20,
        memory_path: str | None = None,
        verbose: bool = True,
    ):
        self.workdir = os.path.abspath(workdir)
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds
        self.verbose = verbose

        # 6 个零件的实例化
        self.llm = LLM()
        self.tools = build_registry(workdir=self.workdir)
        self.ctx = ContextManager(
            keep_last=10,
            max_messages=30,
            summarize_fn=self._summarize,
        )
        self.memory = Memory(min_score=0.5)
        self._memory_path = memory_path
        if memory_path and os.path.isfile(memory_path):
            self.memory.load(memory_path)

        # 短期对话状态
        self.messages: list[dict] = [
            {"role": "system", "content": self._build_system_prompt()},
        ]

    # ---------- 让 ContextManager 可以调 LLM 来摘要 ----------
    def _summarize(self, middle: list[dict]) -> str:
        transcript = "\n".join(
            f"{m.get('role')}: {m.get('content', '')[:200]}" for m in middle
        )
        msg = self.llm.chat(
            messages=[{"role": "user", "content": SUMMARY_PROMPT.format(transcript=transcript)}],
        )
        return (msg.content or "").strip()

    # ---------- 注入 memory 当前快照到 system prompt ----------
    def _build_system_prompt(self) -> str:
        return self.system_prompt + f"\n\n# 工作目录\n请把所有路径都写成绝对路径，根目录是 {self.workdir}"

    # ---------- 主入口：处理一轮用户输入 ----------
    def chat(self, user_input: str, on_text: Callable[[str], None] | None = None) -> str:
        # 1) Memory 召回相关长期事实
        relevant = self.memory.search(user_input, k=3) if len(self.memory) else []
        if relevant:
            self.messages.append({"role": "system", "content": _format_facts(relevant)})

        # 2) 加用户输入
        self.messages.append({"role": "user", "content": user_input})

        # 3) 必要时压缩
        if self.ctx.should_compress(self.messages):
            if self.verbose:
                print(f"  \u2699\ufe0f  消息超过 {self.ctx.max_messages} 条，触发压缩")
            self.messages = self.ctx.compress(self.messages)

        # 4) Agent Loop（第2章 第 9 节）
        for turn in range(1, self.max_tool_rounds + 1):
            resp: Message = self.llm.chat(
                messages=self.messages,
                tools=self.tools.to_schemas(),
            )

            if not resp.tool_calls:
                # 最终回答
                final = resp.content or ""
                if on_text and final:
                    on_text(final)
                self.messages.append({"role": "assistant", "content": final})
                self._distill_to_memory()
                return final

            # 有工具调用
            if self.verbose and resp.content:
                print(f"\U0001f4ad 思考: {resp.content}")

            self.messages.append({
                "role": "assistant",
                "content": resp.content,
                "tool_calls": [tc.as_openai_dict() for tc in resp.tool_calls],
            })

            for tc in resp.tool_calls:
                args = self._safe_load_args(tc.arguments)
                if self.verbose:
                    short_args = json.dumps(args, ensure_ascii=False)
                    print(f"\u26a1 调用 {tc.name}({short_args[:120]})")
                result = self.tools.invoke(tc.name, args)
                if self.verbose:
                    snippet = result[:200] + ("..." if len(result) > 200 else "")
                    print(f"   \u2192 {snippet}")
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        return "\u26a0\ufe0f 达到最大工具调用轮次，已停止。"

    # ---------- 工具参数 JSON 解析（兜底） ----------
    @staticmethod
    def _safe_load_args(raw: str) -> dict:
        try:
            return json.loads(raw or "{}")
        except json.JSONDecodeError:
            return {}

    # ---------- 提炼事实到长期记忆 ----------
    def _distill_to_memory(self) -> None:
        """对话结束后提炼新的长期事实。"""
        recent_user = [
            m for m in self.messages[-6:]
            if m.get("role") == "user"
        ]
        if not recent_user:
            return
        transcript = "\n".join(m.get("content", "")[:200] for m in recent_user)
        try:
            msg = self.llm.chat(
                messages=[{"role": "user", "content": DISTILL_PROMPT.format(transcript=transcript)}],
            )
            text = (msg.content or "").strip()
            for line in text.splitlines():
                line = line.strip()
                if line and len(line) > 4:
                    self.memory.add(line)
            if self._memory_path:
                self.memory.save(self._memory_path)
        except Exception:
            pass  # 提炼失败不影响主流程
