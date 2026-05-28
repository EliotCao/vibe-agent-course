"""
Demo 18 · 上下文爆炸：跑一个 30 轮的任务感受失控
=============================================

配套：第 18 节《上下文工程：为什么要管、什么时候爆》

效果：直观展示——
  - 不做任何上下文管理时，messages 列表怎么膨胀
  - token 消耗如何指数级飙升
  - 最终怎么撞到上下文窗口上限

我们让一个简单 Agent 反复回答"用一段话总结之前的对话"+ "再给我一个新建议"，
每轮的回复都全量塞回历史，跑 30 轮，画一张 token 增长曲线。

跑法：
    python demo_18_context_explosion.py
"""

from __future__ import annotations

from _env import get_model_id, make_client


SEED_PROMPT = "我准备策划一场北京 7 日深度游，请给我一个建议。"

FOLLOW_UP = (
    "总结一下我们之前讨论过的所有要点，然后**再补充 3 个新建议**。"
    "建议要具体、可执行，不要重复之前的内容。"
)


def main(rounds: int = 30) -> None:
    client = make_client()
    MODEL = get_model_id()

    messages = [
        {"role": "system", "content": "你是一个旅行规划助手，回答尽量详细。"},
        {"role": "user", "content": SEED_PROMPT},
    ]

    history_tokens: list[int] = []
    history_chars: list[int] = []

    for turn in range(1, rounds + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.4,
                max_tokens=400,
            )
        except Exception as e:
            print(f"\n💥 第 {turn} 轮调用失败: {e}")
            print("   这往往就是上下文撞窗口或者 timeout 了。")
            break

        reply = resp.choices[0].message.content or ""
        usage = resp.usage

        prompt_tk = usage.prompt_tokens
        total_tk = usage.total_tokens
        history_tokens.append(prompt_tk)
        history_chars.append(sum(len(m["content"]) for m in messages))

        print(
            f"[第 {turn:2d} 轮] "
            f"prompt={prompt_tk:>5d} tokens · "
            f"total={total_tk:>5d} tokens · "
            f"messages 字符数={history_chars[-1]}"
        )

        # 全量塞回历史，并继续追问
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": FOLLOW_UP})

    # 简易 ASCII 折线图
    print("\n" + "=" * 60)
    print("📈 prompt_tokens 随轮次的增长（横向 ASCII 图）")
    print("=" * 60)
    if history_tokens:
        peak = max(history_tokens)
        for i, tk in enumerate(history_tokens, 1):
            bar = "█" * int(tk / peak * 40)
            print(f"第 {i:2d} 轮 [{tk:>5d} tk] {bar}")

    print("\n💡 关键观察")
    print(f"  - 起始 prompt：{history_tokens[0]} tokens")
    print(f"  - 最终 prompt：{history_tokens[-1]} tokens")
    if len(history_tokens) > 1:
        growth = history_tokens[-1] / history_tokens[0]
        print(f"  - 增长倍率：{growth:.1f}x")
    print("\n  Day4 后面要解决的问题：")
    print("    1. 上下文窗口虽然 128K，但不能任由它涨")
    print("    2. token 是按用量计费的，全量塞回去成本飙升")
    print("    3. Lost in the Middle：长上下文里中间的信息会被忽略（Day1 第 3 节讲过）")


if __name__ == "__main__":
    main(rounds=20)
