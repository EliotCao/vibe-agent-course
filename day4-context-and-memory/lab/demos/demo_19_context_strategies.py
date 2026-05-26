"""
Demo 19 · ContextManager：四种上下文管理策略对比
================================================

配套：第 19 节《上下文管理策略：截断 / 摘要 / 分层 / GSSC》

跑同一个 30 轮对话历史，分别用 4 种策略处理，对比：
  - 处理后的 messages 长度（条数 / 字符数）
  - 信息保留度（早期重要信息有没有保住）
  - 实现复杂度

策略：
  ① RAW           —— 不做任何处理（baseline）
  ② TRUNCATE      —— 保留 system + 最近 N 轮，中间砍掉
  ③ SUMMARY       —— system + 早期摘要 + 最近 N 轮原文
  ④ HIERARCHICAL  —— system + 关键长期事实 + 早期摘要 + 最近 N 轮

跑法：
    python demo_19_context_strategies.py
"""

from __future__ import annotations

from _env import get_model_id, make_client


# ============================================================
# 模拟历史：30 轮对话（包含 1 个早期重要事实 + 1 个晚期重要事实）
# ============================================================
def build_fake_history(n_rounds: int = 30) -> list[dict]:
    """生成一段假对话，把'重要事实'埋在第 2 轮和第 28 轮。"""
    msgs = [{"role": "system", "content": "你是个旅行助手。"}]

    # 第 1-2 轮：用户透露一个关键偏好（早期重要事实）
    msgs += [
        {"role": "user", "content": "我准备 6 月去北京玩 7 天。"},
        {"role": "assistant", "content": "好的，6 月北京天气合适。先问您几个问题..."},
        {"role": "user", "content": "重要：我对花粉过敏，户外活动要避开花期。"},  # ⭐ 埋点 1
        {"role": "assistant", "content": "明白，会注意避开花季景点。"},
    ]

    # 中间一堆灌水
    for i in range(n_rounds - 5):
        msgs += [
            {"role": "user", "content": f"再给我推荐 1 个第 {i+3} 天的活动。"},
            {"role": "assistant", "content": f"第 {i+3} 天可以考虑..."},
        ]

    # 倒数第二轮再透露一个关键约束（晚期重要事实）
    msgs += [
        {"role": "user", "content": "对了，我的预算是每天 500 元。"},  # ⭐ 埋点 2
        {"role": "assistant", "content": "我会把每天行程控制在预算内。"},
    ]

    return msgs


# ============================================================
# 策略 ②：截断 —— 保留 system + 最近 N 轮
# ============================================================
def strategy_truncate(messages: list[dict], keep_last: int = 6) -> list[dict]:
    sys_msgs = [m for m in messages if m["role"] == "system"]
    recent = messages[-keep_last:]
    return sys_msgs + recent


# ============================================================
# 策略 ③：摘要 —— 把中间一段总结成一条 system message
# ============================================================
def strategy_summary(messages: list[dict], keep_last: int = 6) -> list[dict]:
    """system + 中间用 LLM 摘要 + 最近 N 轮。"""
    sys_msgs = [m for m in messages if m["role"] == "system"]
    middle = [m for m in messages if m["role"] != "system"][:-keep_last]
    recent = messages[-keep_last:]

    if not middle:
        return sys_msgs + recent

    # 调一次 LLM 把中间生成摘要
    client = make_client()
    MODEL = get_model_id()
    middle_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in middle
    )
    summary_prompt = (
        "请把下面这段对话压缩成一段 100 字以内的中文摘要，"
        "**特别保留任何用户偏好、约束、关键事实**：\n\n" + middle_text
    )
    summary = (
        client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0,
            max_tokens=300,
        ).choices[0].message.content or ""
    )

    return (
        sys_msgs
        + [{"role": "system", "content": f"[早期对话摘要]\n{summary}"}]
        + recent
    )


# ============================================================
# 策略 ④：分层 —— system + 关键事实槽 + 早期摘要 + 最近 N 轮
# ============================================================
KEY_FACT_KEYWORDS = ["过敏", "预算", "重要", "对了", "一定要", "不要"]


def extract_key_facts(messages: list[dict]) -> list[str]:
    """简易关键事实提取：从 user 消息里捞包含关键词的句子。"""
    facts = []
    for m in messages:
        if m["role"] == "user":
            for kw in KEY_FACT_KEYWORDS:
                if kw in m["content"]:
                    facts.append(m["content"].strip())
                    break
    return facts


def strategy_hierarchical(messages: list[dict], keep_last: int = 6) -> list[dict]:
    sys_msgs = [m for m in messages if m["role"] == "system"]
    facts = extract_key_facts(messages)

    # 中间用摘要替代
    summarized = strategy_summary(messages, keep_last)
    # 在 system 之后插入"关键事实"
    fact_block = "\n".join(f"- {f}" for f in facts)
    if fact_block:
        return (
            sys_msgs
            + [{"role": "system", "content": f"[关键事实，永远记住]\n{fact_block}"}]
            + [m for m in summarized if m not in sys_msgs]
        )
    return summarized


# ============================================================
# 评估：处理后的 messages 长度
# ============================================================
def stats(messages: list[dict]) -> dict:
    chars = sum(len(m["content"]) for m in messages)
    return {"count": len(messages), "chars": chars}


# ============================================================
# 检查：四种策略下，"过敏"和"预算"两个事实在不在 messages 里
# ============================================================
def fact_check(messages: list[dict]) -> tuple[bool, bool]:
    text = " ".join(m["content"] for m in messages)
    return ("过敏" in text, "预算" in text)


# ============================================================
# 主测试
# ============================================================
def main() -> None:
    history = build_fake_history(n_rounds=30)
    print(f"原始 messages: {len(history)} 条 / {sum(len(m['content']) for m in history)} 字符\n")

    strategies = {
        "① RAW（不处理）": history,
        "② TRUNCATE（最近 6 轮）": strategy_truncate(history, keep_last=6),
        "③ SUMMARY（摘要 + 最近 6 轮）": strategy_summary(history, keep_last=6),
        "④ HIERARCHICAL（关键事实 + 摘要 + 最近 6 轮）": strategy_hierarchical(history, keep_last=6),
    }

    print(f"{'策略':<45s} {'条数':>6s} {'字符数':>8s} {'有过敏':>8s} {'有预算':>8s}")
    print("-" * 80)
    for name, msgs in strategies.items():
        s = stats(msgs)
        has_aller, has_budget = fact_check(msgs)
        print(
            f"{name:<45s} {s['count']:>6d} {s['chars']:>8d} "
            f"{'✅' if has_aller else '❌':>8s} {'✅' if has_budget else '❌':>8s}"
        )

    print("\n💡 重点观察：")
    print("  - ② 截断：最省字符，但可能把'过敏'这个早期重要事实砍掉")
    print("  - ③ 摘要：保留 token 但靠 LLM 摘要质量，过敏/预算可能被压缩成一句话")
    print("  - ④ 分层：用关键词主动提取关键事实，跨越摘要也能保住")
    print()
    print("  工业版 Coding Agent 普遍用 ④：")
    print("   - system: 角色 + 工具 + 规则")
    print("   - 关键事实：从 user 消息里抽出来的'硬约束'")
    print("   - 早期摘要：LLM 压缩")
    print("   - 最近 N 轮：原文")


if __name__ == "__main__":
    main()
