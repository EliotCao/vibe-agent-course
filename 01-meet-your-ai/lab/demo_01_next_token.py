"""
Demo 01 · 看 LLM 是怎么"猜下一个词"的
====================================

配套：第 1 节《LLM 为什么具备智能：从概率预测到涌现》

效果：直观展示——LLM 本质是在做"下一个 token 的概率分布"，
所谓"智能"是这个过程在巨大规模下的涌现现象。

本 demo 演示两种模式，让你看到 chat 模板对"下一个 token"的巨大影响：
  ① chat 模式（默认）：把输入当成"用户在跟模型说话"，模型会做出回应
     输入 "今天的天气真" → 模型可能输出 "哈哈" / "是" / "哎"（社交反应）
  ② complete 模式：用 system prompt 把模型伪装成"续写引擎"
     输入 "今天的天气真" → 模型可能输出 "好" / "不错" / "棒"（语言续写）

跑法：
    # 方式 A：显式设置
    export BASE_URL=...
    export API_KEY=...
    export MODEL_ID=...
    python demo_01_next_token.py

    # 方式 B：在 CNB 平台运行，使用平台注入的 CNB_API_ENDPOINT / CNB_REPO_SLUG / CNB_TOKEN
    python demo_01_next_token.py
"""

from __future__ import annotations

import math
from typing import Literal

from _env import get_model_id, make_client, chat as llm_chat

client = make_client()
MODEL = get_model_id()

# 把模型伪装成"续写引擎"用的 system prompt
COMPLETE_SYSTEM_PROMPT = (
    "你是一个文本续写引擎。用户给你一段话，你直接把这段话接着往下写，"
    "保持与原文相同的语气、风格、人称。"
    "严格禁止：回应用户、解释、加引号、换行、加任何额外说明。"
    "只输出续写的内容本身。"
)


def _build_messages(prefix: str, mode: Literal["chat", "complete"]) -> list:
    """根据模式构造 messages。"""
    if mode == "complete":
        return [
            {"role": "system", "content": COMPLETE_SYSTEM_PROMPT},
            {"role": "user", "content": prefix},
        ]
    # chat 模式：直接把 prefix 当成用户消息
    return [{"role": "user", "content": prefix}]


def show_top_candidates(
    prefix: str,
    mode: Literal["chat", "complete"] = "chat",
    top_k: int = 5,
) -> None:
    """让模型只生成 1 个 token，并打印它认为的 top-k 候选词与对数概率。

    若后端不支持 logprobs，则自动回退到"多次采样统计频率"的方式。
    """
    mode_label = "续写模式（complete）" if mode == "complete" else "对话模式（chat）"
    print("=" * 60)
    print(f"输入: {prefix!r}   [{mode_label}]")
    print(f"问题: 请预测下一个 token 是什么？")
    print("-" * 60)

    messages = _build_messages(prefix, mode)
    msg = llm_chat(messages, temperature=0)

    chosen = msg.content
    print(f"模型选择: {chosen!r}")
    print()

    # logprobs 在流式模式下不一定支持
    print("⚠️  流式模式下不支持 logprobs，仅展示模型选择的 token")
    print()


PREFIXES = [
    ("【实验 1】半句话补全：模型可能猜什么？", "今天的天气真"),
    ("【实验 2】数学：1 + 1 等于", "一加一等于"),
    ("【实验 3】常识：地球围绕", "地球围绕"),
    ("【实验 4】陷阱：故意问个不确定的", "2026 年世界杯冠军是"),
]


if __name__ == "__main__":
    for title, prefix in PREFIXES:
        print(f"\n{title}")
        # 同一个输入跑两种模式，对比下一个 token 分布
        show_top_candidates(prefix, mode="chat")
        show_top_candidates(prefix, mode="complete")
