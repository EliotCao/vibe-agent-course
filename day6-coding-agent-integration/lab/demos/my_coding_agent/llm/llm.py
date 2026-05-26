"""LLM 客户端封装（来自 Day1）。

把 OpenAI 兼容客户端封装成一个 LLM 类，提供：
- chat(messages, tools=None, stream=False)：非流式 / 流式两种调用
- 流式调用会自动把 tool_calls 分片拼回完整的 Message 对象

这是整个 Agent 跟外部 LLM 交互的**唯一出口**。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Iterable

from _env import get_model_id, make_client


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # 原始 JSON 字符串

    def as_openai_dict(self) -> dict:
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": self.arguments},
        }


@dataclass
class Message:
    """统一的 LLM 响应数据结构（屏蔽 SDK 内部对象差异）。"""

    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLM:
    def __init__(self, model: str | None = None):
        self.client = make_client()
        self.model = model or get_model_id()

    # ---------- 非流式 ----------
    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0,
    ) -> Message:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        resp = self.client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        return Message(
            content=msg.content or "",
            tool_calls=[
                ToolCall(id=tc.id, name=tc.function.name, arguments=tc.function.arguments)
                for tc in (msg.tool_calls or [])
            ],
        )

    # ---------- 流式 ----------
    def chat_stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0,
        on_text=None,  # callable(chunk_text) -> None，用来给 UI 实时打字
    ) -> Message:
        """流式版本，最终也返回完整的 Message。

        on_text 回调用来给 UI 实时显示文字（每个 chunk 调一次）。
        tool_calls 部分会自动从分片合并，调用方拿到的还是完整的。
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        stream = self.client.chat.completions.create(**kwargs)

        content_buf: list[str] = []
        # tool_calls 是按 index 分片的，必须按 index 累积
        tc_buf: dict[int, dict] = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                content_buf.append(delta.content)
                if on_text:
                    on_text(delta.content)
                else:
                    sys.stdout.write(delta.content)
                    sys.stdout.flush()

            for tc_delta in (delta.tool_calls or []):
                idx = tc_delta.index
                if idx not in tc_buf:
                    tc_buf[idx] = {"id": "", "name": "", "args": ""}
                if tc_delta.id:
                    tc_buf[idx]["id"] = tc_delta.id
                if tc_delta.function and tc_delta.function.name:
                    tc_buf[idx]["name"] = tc_delta.function.name
                if tc_delta.function and tc_delta.function.arguments:
                    tc_buf[idx]["args"] += tc_delta.function.arguments

        return Message(
            content="".join(content_buf),
            tool_calls=[
                ToolCall(id=v["id"], name=v["name"], arguments=v["args"])
                for v in sorted(tc_buf.values(), key=lambda x: x["id"] or "")
                if v["name"]
            ],
        )
