"""
Demo 01 · 看 LLM 是怎么"猜下一个词"的
====================================

配套：第 1 节《LLM 为什么具备智能：从概率预测到涌现》

效果：让学生当堂看到——LLM 本质是在做"下一个 token 的概率分布"，
所谓"智能"是这个过程在巨大规模下的涌现现象。

跑法：
    export BASE_URL=...
    export API_KEY=...
    export MODEL_ID=...
    python demo_01_next_token.py
"""

from __future__ import annotations

import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["BASE_URL"],
    api_key=os.environ["API_KEY"],
)
MODEL = os.environ["MODEL_ID"]


def show_top_candidates(prefix: str, top_k: int = 5) -> None:
    """让模型只生成 1 个 token，并打印它认为的 top-k 候选词与对数概率。"""
    print("=" * 60)
    print(f"输入: {prefix!r}")
    print(f"问题: 请预测下一个 token 是什么？")
    print("-" * 60)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prefix}],
        max_tokens=1,
        temperature=0,
        logprobs=True,
        top_logprobs=top_k,
    )

    choice = resp.choices[0]
    chosen = choice.message.content
    print(f"模型选择: {chosen!r}")
    print()

    if not choice.logprobs or not choice.logprobs.content:
        print("⚠️  当前 base_url 不支持 logprobs，跳过候选展示")
        return

    print(f"前 {top_k} 个候选（按概率从高到低）：")
    top = choice.logprobs.content[0].top_logprobs
    for i, item in enumerate(top, 1):
        prob = pow(2.71828, item.logprob)
        bar = "█" * int(prob * 40)
        print(f"  {i}. {item.token!r:>15s}  概率 {prob:6.2%}  {bar}")
    print()


if __name__ == "__main__":
    print("\n【实验 1】半句话补全：模型可能猜什么？")
    show_top_candidates("今天的天气真")

    print("\n【实验 2】数学：1 + 1 等于")
    show_top_candidates("一加一等于")

    print("\n【实验 3】常识：地球围绕")
    show_top_candidates("地球围绕")

    print("\n【实验 4】陷阱：故意问个不确定的")
    show_top_candidates("2026 年世界杯冠军是")

    print("\n" + "=" * 60)
    print("👀 观察：")
    print("  - 简单常识题，top1 概率接近 100%（模型很'确信'）")
    print("  - 不确定的题，top-k 概率分布散开（模型在'猜'）")
    print()
    print("💡 理解：")
    print("  LLM 的本质就是这个过程——")
    print("  对每个位置算下一个 token 的概率分布，然后采样。")
    print("  把这个过程做到 GPT-4 / Claude 那么大的规模时，")
    print("  '智能'就涌现出来了。")
    print("=" * 60)
