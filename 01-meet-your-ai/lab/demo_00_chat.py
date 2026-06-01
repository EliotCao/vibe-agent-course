"""
Demo 00 · 最简单的 LLM 对话（OpenAI 原始 API）
==============================================

配套：第1章 课前热身

效果：一个最小的交互式对话循环——你输入什么，大模型回答什么。
第一次"跑通"与大模型对话的完整链路。

重点演示：
    - 如何用 openai 库创建客户端
    - 如何调用 client.chat.completions.create() 进行流式对话
    - 如何逐 chunk 解析流式响应

跑法：
    python demo_00_chat.py

输入 quit / exit / q 退出。
"""

from __future__ import annotations

import os
import readline  # noqa: F401 — 启用终端行编辑，修复中文退格问题

from openai import OpenAI

# ------------------------------------------------------------------
# 1️⃣ 配置：从环境变量读取 API 地址和密钥
#
#    CNB 平台会自动注入以下变量：
#    CNB_API_ENDPOINT — CNB 平台 API 地址
#    CNB_REPO_SLUG    — 当前仓库标识
#    CNB_TOKEN        — 平台鉴权 Token
#
#    也可手动设置 BASE_URL / API_KEY 用于本地开发
# ------------------------------------------------------------------
_endpoint = os.environ.get("CNB_API_ENDPOINT", "")
_slug = os.environ.get("CNB_REPO_SLUG", "")

if _endpoint and _slug:
    BASE_URL = f"{_endpoint}/{_slug}/-/ai-ide/v2"
else:
    BASE_URL = os.environ.get("BASE_URL", "")

API_KEY = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN") or ""
MODEL = os.environ.get("MODEL_ID", "glm-5.0")

if not BASE_URL or not API_KEY:
    raise EnvironmentError(
        "请设置环境变量：\n"
        "  方式1（CNB平台）：确保 CNB_API_ENDPOINT / CNB_REPO_SLUG / CNB_TOKEN 已注入\n"
        "  方式2（本地开发）：export BASE_URL=... API_KEY=..."
    )

# ------------------------------------------------------------------
# 2️⃣ 创建 OpenAI 客户端（兼容任何 OpenAI 协议的服务）
# ------------------------------------------------------------------
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

def chat(user_input: str) -> str:
    """单轮对话：调用 OpenAI Chat Completions API（流式），逐字打印。"""

    # ------------------------------------------------------------------
    # 3️⃣ 调用 chat.completions.create —— 这是 OpenAI API 的核心方法
    #
    #    参数说明：
    #    - model:       使用的模型 ID
    #    - messages:    对话消息列表，每条消息包含 role 和 content
    #    - temperature: 控制随机性，越大回复越有创意
    #    - stream:      True 表示流式返回，逐 token 输出
    # ------------------------------------------------------------------
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
        temperature=0.9,
        stream=True,
    )

    # ------------------------------------------------------------------
    # 4️⃣ 逐 chunk 读取流式响应
    #
    #    每个 chunk 的结构：
    #    chunk.choices[0].delta.content  —— 本次增量文本（可能为 None）
    #    chunk.choices[0].finish_reason  —— "stop" 表示生成结束
    # ------------------------------------------------------------------
    parts = []
    first = True
    for chunk in stream:
        # 检查是否有内容
        if chunk.choices and chunk.choices[0].delta.content:
            if first:
                print("\r\033[K" + "AI: ", end="", flush=True)
                first = False
            text = chunk.choices[0].delta.content
            print(text, end="", flush=True)
            parts.append(text)
    print()  # 换行
    return "".join(parts)


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Hello! 我是你的 AI 助手，有什么想聊的？")
    print("   输入 quit / exit / q 退出")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nAI: 💭 thinking...", end="", flush=True)
        chat(user_input)

    print("\n👋 再见！")
