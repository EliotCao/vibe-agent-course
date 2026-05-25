"""
Demo 01 · 看 LLM 是怎么"猜下一个词"的
====================================

配套：第 1 节《LLM 为什么具备智能：从概率预测到涌现》

效果：让学生当堂看到——LLM 本质是在做"下一个 token 的概率分布"，
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

from _env import get_model_id, make_client

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
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1,
        temperature=0,
        logprobs=True,
        top_logprobs=top_k,
    )

    choice = resp.choices[0]
    chosen = choice.message.content
    print(f"模型选择: {chosen!r}")
    print()

    # 展示 logprobs（如果后端支持）
    if choice.logprobs and choice.logprobs.content:
        print(f"前 {top_k} 个候选（按概率从高到低，来源：logprobs）：")
        top = choice.logprobs.content[0].top_logprobs
        for i, item in enumerate(top, 1):
            prob = math.exp(item.logprob)
            bar = "█" * int(prob * 40)
            print(f"  {i}. {item.token!r:>15s}  概率 {prob:6.2%}  {bar}")
        print()
    else:
        print("⚠️  当前 base_url 不支持 logprobs，无法展示候选词分布")
        print("   （需要支持 logprobs 的后端才能看到完整概率分布）")
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

    print("\n" + "=" * 60)
    print("👀 观察：")
    print("  - 同一个输入，chat 模式 vs complete 模式，第一个 token 完全不同")
    print("    · chat：模型把输入当'对话'，会回应（'哈哈'/'是'/'我觉得'…）")
    print("    · complete：模型把输入当'要续写的文本'，会接着写（'好'/'不错'…）")
    print("  - 简单常识题，top1 概率接近 100%（模型很'确信'）")
    print("  - 不确定的题，top-k 概率分布散开（模型在'猜'）")
    print()
    print("💡 理解：")
    print("  LLM 的本质就是这个过程——")
    print("  对每个位置算下一个 token 的概率分布，然后采样。")
    print("  把这个过程做到 GPT-4 / Claude 那么大的规模时，")
    print("  '智能'就涌现出来了。")
    print()
    print("  一个有趣的副产物：")
    print("  仅仅一句 system prompt 就能彻底改变 token 分布——")
    print("  这就是 demo_02 要讲的'system prompt 是改变 AI 行为最便宜的方式'。")
    print("=" * 60)
