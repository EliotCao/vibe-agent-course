"""第 4 章：LLM —— 不依赖 hello_agents 框架的独立 LLM 客户端。

封装一个兼容 OpenAI 接口的客户端，支持流式响应输出。
"""

import os
from typing import Dict, Generator, List, Optional, Union

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLM:
    """独立的 LLM 客户端，兼容 OpenAI 接口。"""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.model = model or self._get_model_id()
        api_key = api_key or self._get_api_key()
        base_url = base_url or self._get_base_url()
        timeout = timeout or self._get_timeout()

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    @staticmethod
    def _get_base_url() -> str:
        base_url = os.environ.get("BASE_URL")
        if base_url:
            return base_url
        endpoint = os.environ.get("CNB_API_ENDPOINT", "")
        repo_slug = os.environ.get("CNB_REPO_SLUG", "")
        if endpoint and repo_slug:
            return f"{endpoint}/{repo_slug}/-/ai/"
        raise EnvironmentError(
            "请设置 BASE_URL，或同时设置 CNB_API_ENDPOINT 和 CNB_REPO_SLUG 环境变量"
        )

    @staticmethod
    def _get_api_key() -> str:
        api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN")
        if not api_key:
            raise EnvironmentError("请设置 API_KEY 或 CNB_TOKEN 环境变量")
        return api_key

    @staticmethod
    def _get_model_id() -> str:
        return os.environ.get("MODEL_ID", "hunyuan-turbos-latest")

    @staticmethod
    def _get_timeout() -> int:
        return int(os.environ.get("LLM_TIMEOUT", "60"))

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        stream: bool = True,
        tools: Optional[List[Dict]] = None,
    ) -> Union[Optional[str], Generator[str, None, None]]:
        """调用大语言模型。

        - stream=False: 返回完整响应字符串（无 tools）或完整 message 对象（有 tools）
        - stream=True:  返回一个生成器，逐块 yield 文本片段
        - tools: OpenAI function calling schema 列表
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["stream"] = False  # function calling 不用流式

            response = self.client.chat.completions.create(**kwargs)

            if tools:
                # 有 tools 时返回完整 message 对象（含 tool_calls）
                return response.choices[0].message

            if not stream:
                # 无 tools，非流式：返回字符串
                return response.choices[0].message.content

            return self._iter_stream(response)

        except Exception as e:
            print(f"❌ 调用 LLM 时发生错误: {e}")
            return None

    @staticmethod
    def _iter_stream(response) -> Generator[str, None, None]:
        """将流式响应转为生成器。"""
        for chunk in response:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content or ""
            if content:
                yield content

    @staticmethod
    def stream_print(stream: Generator[str, None, None]) -> str:
        """消费流式生成器，逐块打印并返回完整文本。"""
        collected = []
        for chunk in stream:
            print(chunk, end="", flush=True)
            collected.append(chunk)
        print()
        return "".join(collected)

