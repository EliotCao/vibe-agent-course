"""
Day1 产出：LLMClient
=====================

补全这个类，让 tests/test_llm.py 全部通过。

依赖：
  - openai SDK
  - tiktoken
  - 环境变量：BASE_URL / API_KEY / MODEL_ID
"""

from __future__ import annotations

import os
from typing import Generator

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMClient:
    def __init__(self):
        # TODO: 初始化 OpenAI 客户端和 tiktoken 编码器
        #   self.client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
        #   self.model = os.getenv("MODEL_ID")
        #   self.enc = tiktoken.get_encoding("cl100k_base")
        raise NotImplementedError("请补全 __init__")

    def chat(self, messages: list[dict], **kwargs) -> str:
        """非流式调用，返回完整回复文本。"""
        # TODO:
        #   resp = self.client.chat.completions.create(model=self.model, messages=messages, **kwargs)
        #   return resp.choices[0].message.content
        raise NotImplementedError("请补全 chat")

    def chat_stream(self, messages: list[dict], **kwargs) -> Generator[str, None, None]:
        """流式调用，逐 chunk yield 文本片段。"""
        # TODO:
        #   resp = self.client.chat.completions.create(model=self.model, messages=messages, stream=True, **kwargs)
        #   for chunk in resp:
        #       if chunk.choices and chunk.choices[0].delta.content:
        #           yield chunk.choices[0].delta.content
        raise NotImplementedError("请补全 chat_stream")

    def count_tokens(self, text: str) -> int:
        """统计文本的 token 数。"""
        # TODO:
        #   return len(self.enc.encode(text))
        raise NotImplementedError("请补全 count_tokens")
