"""测试 LLM 客户端。"""

from llm import LLM


def main():
    llm = LLM()

    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "用一句话解释什么是 Agent"},
    ]

    # 非流式
    print("=== 非流式调用 ===")
    result = llm.chat(messages, stream=False)
    print(result)

    # 流式
    print("\n=== 流式调用 ===")
    stream = llm.chat(messages, stream=True)
    if stream:
        result = LLM.stream_print(stream)


if __name__ == "__main__":
    main()
