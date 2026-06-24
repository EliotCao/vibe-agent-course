"""
Demo 19 · 四种上下文管理策略对比
================================

配套：第 19 节《上下文管理策略：截断 / 摘要 / 分层 / GSSC》

承接 18 节示例暴露的"上下文爆炸"问题，这里给出解法并横向对比。

实验设计：构造同一段 30 轮对话历史，故意埋两个"重要事实"——
  - 早期事实：第 2 轮的"花粉过敏"（容易被截断/摘要丢掉）
  - 晚期事实：倒数第二轮的"每天预算 500 元"（一般都能保住）
再用 4 种策略分别处理，对比三个维度：
  - 处理后的 messages 规模（条数 / 字符数）
  - 信息保留度（两个埋点事实还在不在）
  - 实现复杂度

四种策略（keep_last 默认保留最近 6 轮）：
  ① RAW           —— 不做任何处理，作为对照基线（baseline）
  ② TRUNCATE      —— 保留 system + 最近 N 轮，中间直接砍掉
  ③ SUMMARY       —— system + 中间段 LLM 摘要 + 最近 N 轮原文
  ④ HIERARCHICAL  —— system + 关键事实槽 + 早期摘要 + 最近 N 轮原文

注：讲稿里的第四种策略 GSSC 是工程级流水线，本 demo 不实现，
    这里的"④ 分层"对应讲稿中的"③ 分层"。

运行方式：
    source /workspace/.venv/bin/activate
    python demo_19_context_strategies.py
"""

from prettytable import PrettyTable

from _env import chat


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
    """摘要压缩策略：system + LLM 摘要（中间段）+ 最近 N 轮原文。

    将消息列表划分为三个区域，对中间区域调用 LLM 生成一段简短摘要，
    以此替代冗长的早期对话历史。相比纯截断策略，摘要在节省 token 的同时
    仍有概率保留跨轮次的关键信息（如用户偏好、约束条件）。

    处理流程：

    1. 提取 system 消息：所有 role 为 `"system"` 的消息原样保留，
       不参与摘要压缩。

    2. 划分中间段：将非 system 消息切分为"中间段"和"最近段"：
       中间段 = 除 system 外的全部消息去掉最后 `keep_last` 条；
       最近段 = 消息列表最后 `keep_last` 条（含 system）。

    3. LLM 摘要生成：将中间段拼接为 `角色: 内容` 格式的文本，
       调用 LLM（`_env.chat()`）压缩为 100 字以内的中文摘要。
       摘要提示词明确要求保留用户偏好和关键事实，以提高信息留存率。

    4. 组装输出：最终返回 `system 消息 + 摘要 system 消息 + 最近 N 条`。

    Args:
        messages: 完整的消息列表，每条消息为 `{"role": str, "content": str}`
            格式。应包含至少一条 system 消息作为角色/工具定义。
        keep_last: 保留原始内容的最近消息条数（含 system），默认 6 条。
            值越小压缩越激进、token 越省，但可能丢失更多细节。

    Returns:
        压缩后的消息列表。如果中间段为空（消息总数未超过 `keep_last`
        或减去 system 后不足 ``keep_last`` 条），则直接返回
        `system 消息 + 全部非 system 消息`，不触发 LLM 调用。

    Note:
        - 摘要质量依赖于 LLM 能力，温度参数固定为 0 以提高确定性。
        - LLM 调用会引入网络延迟和费用成本，实际使用时应设置合理的
          `keep_last` 值以平衡压缩频率和开销。
        - 返回值总是包含至少一条 system 消息（假设输入至少有一条）。
        - 此函数不修改传入的 `messages`，返回值为新列表。

    Example:
        >>> history = build_fake_history(n_rounds=30)
        >>> compressed = strategy_summary(history, keep_last=4)
        >>> # compressed 中包含一条 "[早期对话摘要]" 的 system 消息
        >>> any("早期对话摘要" in m["content"] for m in compressed)
        True
    """
    if keep_last < 1:
        keep_last = 6

    non_sys = [m for m in messages if m["role"] != "system"]
    # 消息量不足，无需压缩，直接返回原文
    if len(non_sys) <= keep_last:
        return messages

    sys_msgs = [m for m in messages if m["role"] == "system"]
    # 将非 system 消息切分：去掉最后 keep_last 条，剩余为"中间段"
    middle = [m for m in messages if m["role"] != "system"][:-keep_last]
    recent = messages[-keep_last:]

    # 中间段为空时无需压缩，直接返回
    if not middle:
        return sys_msgs + recent

    # 将中间段拼接为文本，调用 LLM 生成摘要
    middle_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in middle
    )
    summary_prompt = (
        "请把下面这段对话压缩成一段 100 字以内的中文摘要，"
        "**特别保留任何用户偏好、约束、关键事实**：\n\n" + middle_text
    )
    msg = chat(
        [{"role": "user", "content": summary_prompt}],
        temperature=0,
        stream=True,
    )
    summary = msg.content or ""

    return (
        sys_msgs
        + [{"role": "system", "content": f"[早期对话摘要]\n{summary}"}]
        + recent
    )


# ============================================================
# 策略 ④：分层 —— system + 关键事实槽 + 早期摘要 + 最近 N 轮
# ============================================================
KEY_FACT_KEYWORDS = {"过敏", "预算", "重要", "对了", "一定要", "不要"}


def _contains_key_fact(text: str) -> bool:
    """判断文本是否包含关键事实关键词。"""
    return any(kw in text for kw in KEY_FACT_KEYWORDS)


def extract_key_facts(messages: list[dict]) -> list[str]:
    """简易关键事实提取：从 user 消息里捞包含关键词的句子。"""
    facts = []
    for m in messages:
        if m["role"] == "user" and _contains_key_fact(m["content"]):
            facts.append(m["content"].strip())
    return facts


def strategy_hierarchical(messages: list[dict], keep_last: int = 6) -> list[dict]:
    """分层压缩策略：system + 关键事实槽 + 早期摘要 + 最近 N 轮原文。

    这是四种策略中信息保留度最高的方案，广泛应用于工业级 Agent（如 Claude Code、
    Cursor 等）。其核心理念是将消息按"重要性层级"分别处理：

    处理流程（四层结构）：
    1. System 消息：从原始消息列表中提取所有 system 消息，原样保留。
       这些通常是角色设定、工具定义、规则等，不能被压缩。

    2. 关键事实槽：调用 :func:`extract_key_facts` 从全部历史消息中
       提取用户的硬约束（如"过敏""预算"等关键词匹配的句子），
       以一条独立 system 消息前置注入。这样即使早期原文被摘要覆盖，
       关键约束仍然显式可见。

    3. 早期摘要：委托 :func:`strategy_summary` 对中间段消息做
       LLM 摘要压缩，用一段简短文本替代冗长的早期对话。

    4. 最近 N 轮原文：由 `strategy_summary` 内部保留最近
       `keep_last` 条消息的原始内容，保证即时上下文质量。

    Args:
        messages: 完整的消息列表，每条消息为 `{"role": str, "content": str}`
            格式。应包含至少一条 system 消息。
        keep_last: 保留原文的最近消息条数，默认 6 条。值越小压缩越激进，
            值越大信息丢失越少但 token 消耗越高。

    Returns:
        压缩后的消息列表，结构为：

        .. code-block:: text

            [system_1, ..., system_n, 关键事实槽, 早期摘要 system, 最近 N 条原文]

        如果 `extract_key_facts` 未提取到任何关键事实，
        则退化为与 ``strategy_summary`` 相同的输出（无关键事实槽）。

    Note:
        - 关键事实提取依赖 `KEY_FACT_KEYWORDS` 关键词列表，
          当前为规则匹配，生产环境中可升级为 LLM 驱动的语义提取。
        - 此函数不修改传入的 `messages`，返回值是新列表。
        - 当消息量较小时，`strategy_summary` 可能不做压缩直接返回原文，
          此时分层策略仅多出一个关键事实槽。

    Example:
        >>> history = build_fake_history(n_rounds=30)
        >>> compressed = strategy_hierarchical(history, keep_last=6)
        >>> # compressed 中包含一条 "[关键事实，永远记住]" 的 system 消息
        >>> any("关键事实" in m.get("content", "") for m in compressed)
        True
    """
    sys_msgs = [m for m in messages if m["role"] == "system"]

    # 中间消息用摘要替代（内部保留最近 keep_last 轮原文）
    summarized = strategy_summary(messages, keep_last)

    # 从全部历史中提取关键事实，以独立 system 消息插入
    facts = extract_key_facts(messages)
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

    # 用 prettytable 打印对比表（无边框）
    table = PrettyTable()
    table.field_names = ["策略", "条数", "字符数", "有过敏", "有预算"]
    table.border = False       # 去掉所有边框线
    table.align["策略"] = "l"  # 左对齐
    table.align["条数"] = "r"
    table.align["字符数"] = "r"
    table.align["有过敏"] = "c"
    table.align["有预算"] = "c"

    for name, msgs in strategies.items():
        s = stats(msgs)
        has_aller, has_budget = fact_check(msgs)
        table.add_row([
            name,
            s["count"],
            s["chars"],
            "✅" if has_aller else "❌",
            "✅" if has_budget else "❌",
        ])

    print(table)

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
