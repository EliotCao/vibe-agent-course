"""
Day1 综合实操起手脚手架：流式 LLM REPL

在这个文件上填空 / 改造。每个 TODO 都对应今天讲过的一个概念。
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# TODO（第 2 节）：从环境变量读取配置
BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL_ID")

if not (BASE_URL and API_KEY and MODEL):
    raise SystemExit("请在 .env 里配置 BASE_URL / API_KEY / MODEL_ID")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# TODO（第 2 节）：定义初始 system prompt
messages = [
    {"role": "system", "content": "你是一个简洁的编程助手。"}
]
total_tokens = 0


def stream_chat(msgs):
    """
    TODO（第 3 节）：调 LLM 流式输出。
    要求：
      - stream=True
      - 逐字 print（注意 flush=True）
      - 同时累计本轮 token 消耗
      - 返回 (full_text, usage)
    """
    raise NotImplementedError("请实现 stream_chat")


def main():
    global total_tokens
    print(f"[Day1 LLM REPL] system: {messages[0]['content']}")
    print("命令：/system <prompt>  /reset  /save <file>  exit\n")

    while True:
        try:
            user = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not user:
            continue
        if user.lower() in ("exit", "quit"):
            break

        # TODO（第 2 节）：实现 /system <prompt> 切换 system

        # TODO（第 2 节）：实现 /reset 清空历史（保留 system）

        # TODO：实现 /save <file> 把对话保存成 JSON

        messages.append({"role": "user", "content": user})
        print("AI: ", end="")
        text, usage = stream_chat(messages)
        messages.append({"role": "assistant", "content": text})

        if usage:
            total_tokens += usage.total_tokens
            print(f"[本轮 {usage.total_tokens} · 累计 {total_tokens}]\n")


if __name__ == "__main__":
    main()
