"""
第3章产出：Agent 主循环
========================

补全这个类，让 tests/test_agent.py 全部通过。

核心逻辑：Agent = LLM + Tools + Loop
"""

from __future__ import annotations

import json

from llm import LLMClient
from tools import ToolRegistry


class Agent:
    def __init__(self, llm: LLMClient, tools: ToolRegistry, system_prompt: str = "你是一个有用的助手。"):
        # TODO: 保存 llm, tools, system_prompt
        raise NotImplementedError("请补全 __init__")

    def run(self, user_message: str, max_iterations: int = 10) -> str:
        """执行任务：循环调用 LLM，有 tool_calls 就执行，没有就返回最终回答。"""
        # TODO:
        #   1. 构造 messages = [system, user]
        #   2. for i in range(max_iterations):
        #        调用 LLM（带 tools schema）
        #        如果没有 tool_calls → 返回 content
        #        有 tool_calls → 执行每个工具，结果追加到 messages
        #   3. 达到上限 → 返回提示信息
        raise NotImplementedError("请补全 run")
