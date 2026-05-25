"""第 2 章：Hello LLM —— 一个最小可用的流式 LLM 客户端。

封装一个兼容 OpenAI 接口的客户端 `HelloAgentsLLM`，默认使用流式响应，
便于直观感受大模型逐 token 输出的过程。
"""

from typing import Dict, List, Optional

from openai import OpenAI

from config import get_api_key, get_base_url, get_model_id, get_timeout


class HelloAgentsLLM:
    """为本书 "Hello Agents" 定制的 LLM 客户端。

    用于调用任何兼容 OpenAI 接口的服务，并默认使用流式响应。
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """初始化客户端。

        优先使用传入参数；未提供时从环境变量加载（见 `config.py`）。
        """
        self.model = model or get_model_id()
        api_key = api_key or get_api_key()
        base_url = base_url or get_base_url()
        timeout = timeout or get_timeout()

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def think(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
    ) -> Optional[str]:
        """调用大语言模型进行思考，并以流式方式返回完整响应文本。"""
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            print("✅ 大语言模型响应成功:")
            collected: List[str] = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected.append(content)
            print()  # 流式输出结束后换行
            return "".join(collected)

        except Exception as e:
            print(f"❌ 调用 LLM API 时发生错误: {e}")
            return None


# --- 客户端使用示例 ---
if __name__ == "__main__":
    try:
        llm_client = HelloAgentsLLM()

        example_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes Python code.",
            },
            {"role": "user", "content": "写一个快速排序算法"},
        ]

        print("--- 调用 LLM ---")
        response_text = llm_client.think(example_messages)
        if response_text:
            print("\n--- 完整模型响应 ---")
            print(response_text)

    except EnvironmentError as e:
        print(e)
