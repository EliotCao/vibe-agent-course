"""智能旅行助手 - 入口。"""

from hello_agent.agent import run_agent
from hello_agent.config import MODEL_ID, get_api_key, get_base_url
from hello_agent.llm import OpenAICompatibleClient


def main():
    base_url = get_base_url()
    api_key = get_api_key()

    print(f"模型: {MODEL_ID}")
    print(f"API 地址: {base_url}\n")

    llm = OpenAICompatibleClient(
        model=MODEL_ID,
        api_key=api_key,
        base_url=base_url,
    )

    user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
    run_agent(llm, user_prompt)


if __name__ == "__main__":
    main()
