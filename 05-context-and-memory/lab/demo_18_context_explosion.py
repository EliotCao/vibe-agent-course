"""
Demo 18 · 上下文爆炸：跑一个 30 轮的任务，亲眼看着它失控
====================================================

配套：第 18 节《上下文工程：为什么必须管，不管会怎样》

不做任何上下文管理，让你直观看到三件事同时发生：
  - messages 列表如何随轮次不断膨胀
  - prompt_tokens 如何飙升
  - 按这个趋势，多少轮就会撞上上下文窗口上限

做法：让一个简单的旅行规划 Agent 反复执行同一个任务——
「总结之前讨论的所有要点 + 再补充 3 个新建议」，每轮回复都全量塞回历史，
连跑 30 轮，最后画一张 token 增长曲线。

运行方式：
    cd /workspace/05-context-and-memory/lab/
    source /workspace/.venv/bin/activate
    python demo_18_context_explosion.py
"""

from _env import get_model_id, make_client


SEED_PROMPT = "我准备策划一场北京 7 日深度游，请给我一个建议。"

FOLLOW_UP = (
    "总结一下我们之前讨论过的所有要点，然后**再补充 3 个新建议**。"
    "建议要具体、可执行，不要重复之前的内容。"
)


def main(rounds: int = 30) -> None:
    rounds = rounds if rounds > 0 else 30

    client = make_client()

    messages = [
        {"role": "system", "content": "你是一个旅行规划助手，回答尽量详细。"},
        {"role": "user", "content": SEED_PROMPT},
    ]

    history_tokens: list[int] = []
    history_chars: list[int] = []

    for turn in range(1, rounds + 1):
        try:
            # 当前接口仅支持流式输出（stream=True）；
            # 想拿到 usage 字段需显式打开 stream_options.include_usage=True，
            # 这样最后一个 chunk 会带上 usage。
            stream = client.chat.completions.create(
                model=get_model_id(),
                messages=messages,
                temperature=0.4,
                max_tokens=400,
                stream=True,
                stream_options={"include_usage": True},
            )

            reply_parts: list[str] = []
            usage = None
            for chunk in stream:
                # 注意：带 usage 的最后一个 chunk，choices 通常是空列表
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if getattr(delta, "content", None):
                        reply_parts.append(delta.content)
                if getattr(chunk, "usage", None):
                    usage = chunk.usage
        except Exception as e:
            print(f"\n💥 第 {turn} 轮调用失败: {e}")
            print("   这往往就是上下文撞窗口或者 timeout 了。")
            break

        reply = "".join(reply_parts)

        if usage is None:
            # 极少数兼容性问题：没拿到 usage 就跳过本轮统计，但仍然把对话累积下去
            print(f"[第 {turn:2d} 轮] ⚠️ 无 usage 字段，跳过统计")
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": FOLLOW_UP})
            continue

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
    if not history_tokens:
        print("  - 一轮都没跑成功，无法统计 token 增长。请先排查接口/网络。")
    else:
        print(f"  - 起始 prompt：{history_tokens[0]} tokens")
        print(f"  - 最终 prompt：{history_tokens[-1]} tokens")
        if len(history_tokens) > 1:
            growth = history_tokens[-1] / history_tokens[0]
            print(f"  - 增长倍率：{growth:.1f}x")
    print("\n  第4章 后面要解决的问题：")
    print("    1. 上下文窗口虽然 128K，但不能任由它涨")
    print("    2. token 是按用量计费的，全量塞回去成本飙升")
    print("    3. Lost in the Middle：长上下文里中间的信息会被忽略（第1章 第 3 节讲过）")


if __name__ == "__main__":
    main(rounds=20)
