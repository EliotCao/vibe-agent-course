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
            # return f"{endpoint}/{repo_slug}/-/ai"
            return f"{endpoint}/{repo_slug}/-/ai-ide/v2"
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
        return os.environ.get("MODEL_ID", "glm-5.0")

    @staticmethod
    def _get_timeout() -> int:
        return int(os.environ.get("LLM_TIMEOUT", "60"))

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        stream: bool = True,
        tools: Optional[List[Dict]] = None,
    ):
        """调用大语言模型。

        - tools 非空时：始终用流式收集完整响应，返回拼装的 message 对象
        - stream=False 且无 tools：返回完整响应字符串
        - stream=True 且无 tools：返回生成器，逐块 yield 文本片段
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

            # 强制使用流式（兼容只支持流式的接口）
            kwargs["stream"] = True

            response = self.client.chat.completions.create(**kwargs)

            if tools:
                # 流式收集 Function Calling 响应，拼装为完整 message
                return self._collect_tool_stream(response)

            if not stream:
                # 流式收集后返回完整字符串
                return "".join(self._iter_stream(response))

            return self._iter_stream(response)

        except Exception as e:
            print(f"❌ 调用 LLM 时发生错误: {e}")
            return None

    @staticmethod
    def _collect_tool_stream(response):
        """流式收集 Function Calling 响应，拼装为类 message 对象。"""
        content_parts = []
        tool_calls_map = {}  # index -> {id, function_name, arguments}

        for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # 收集文本内容
            if delta.content:
                content_parts.append(delta.content)

            # 收集 tool_calls（可能分多个 chunk 到达）
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tool_calls_map:
                        tool_calls_map[idx] = {
                            "id": tc_delta.id or "",
                            "name": "",
                            "arguments": "",
                        }
                    if tc_delta.id:
                        tool_calls_map[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tool_calls_map[idx]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            tool_calls_map[idx]["arguments"] += tc_delta.function.arguments

        # 拼装为统一的 message-like 对象
        return _ToolMessage(
            content="".join(content_parts) if content_parts else None,
            tool_calls=[
                _ToolCall(
                    id=tc["id"],
                    function=_Function(name=tc["name"], arguments=tc["arguments"]),
                )
                for tc in sorted(tool_calls_map.values(), key=lambda x: x["id"])
            ] if tool_calls_map else None,
        )

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


# ---- 辅助数据类：模拟 OpenAI message 对象结构 ----

class _Function:
    """模拟 tool_call.function 结构。"""
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


class _ToolCall:
    """模拟单个 tool_call 结构。"""
    def __init__(self, id: str, function: _Function):
        self.id = id
        self.function = function


class _ToolMessage:
    """模拟 ChatCompletionMessage 结构（含 tool_calls）。"""
    def __init__(self, content: Optional[str], tool_calls: Optional[list]):
        self.content = content
        self.tool_calls = tool_calls
