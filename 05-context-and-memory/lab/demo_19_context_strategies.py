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
    cd /workspace/05-context-and-memory/lab/
    source /workspace/.venv/bin/activate
    python demo_19_context_strategies.py
"""

from prettytable import PrettyTable

from _env import chat


# ============================================================
# 模拟历史：30 轮对话（包含 1 个早期重要事实 + 1 个晚期重要事实）
# ============================================================
def build_fake_history(n_rounds: int = 30) -> list[dict]:
    """构造一段模拟的多轮对话历史，用于测试不同上下文管理策略的效果。

    该函数生成一个结构化的消息列表，模拟用户与旅行助手之间的完整对话。
    对话中故意埋入两个"重要事实"，分布在对话早期的不同位置，
    用以考察各策略（截断、摘要、分层）在压缩上下文时对关键信息的保留能力。

    对话结构：
        1. system 消息：设定角色为旅行助手。
        2. 第 1-2 轮（早期重要事实）：用户透露关键偏好——
           `"重要：我对花粉过敏，户外活动要避开花期。"`
           此事实位于对话前段，容易被截断策略丢弃、或被摘要策略压缩丢失。
        3. 中间填充轮：由预定义的 25 组问答模板循环填充，生成
           `n_rounds - 5` 轮真实感的旅行话题对话（如门票、交通、美食等），
           模拟对话中大量"噪音"信息。
        4. 倒数第二轮（晚期重要事实）：用户补充关键约束——
           `"对了，我的预算是每天 500 元。"`
           此事实位于对话末尾附近，通常能被所有策略保留，
           作为对照组验证策略是否正常保留了近期信息。

    Args:
        n_rounds: 期望生成的对话轮数，默认 30。每轮包含一条 user 消息
            和一条 assistant 消息（共 2 条）。取值应不小于 6，
            否则中间填充轮数不足，返回值长度过短。

    Returns:
        扁平的消息列表，格式为 `[{"role": str, "content": str}, ...]`，
        可直接传入 OpenAI Chat Completions API 的 `messages` 参数。
        总条数为 `1（system）+ 4（对话早期事实）+ n_rounds * 2 + 2（对话晚期重要事实）`，
        实际条数可能因取整略有偏差。

    Note:
        - 返回的列表是全新构造的，每次调用都会创建独立副本。
        - 中间填充轮使用取模循环，当 `n_rounds` 较大时，
          同一组问答会重复出现，这不会影响策略对比实验。
        - 两个埋点事实分别以 `"过敏"` 和 `"预算"` 为关键词，
          便于在 :func:`fact_check` 中通过简单子串匹配做检测。

    Example:
        >>> history = build_fake_history(n_rounds=30)
        >>> len(history)
        67
        >>> history[0]["role"]
        'system'
        >>> "花粉过敏" in history[6]["content"]  # 第 2 轮 user 消息
        True
        >>> "500 元" in history[-2]["content"]    # 倒数第二轮 user 消息
        True
    """
    n_rounds = n_rounds if n_rounds > 0 else 30

    msgs = [{"role": "system", "content": "你是个旅行助手。"}]

    # 第 1-2 轮：用户透露一个关键偏好（早期重要事实）
    msgs += [
        {"role": "user", "content": "我准备 6 月去北京玩 7 天。"},
        {"role": "assistant", "content": "好的，6 月北京天气合适。先问您几个问题..."},
        {"role": "user", "content": "重要：我对花粉过敏，户外活动要避开花期。"},  # ⭐ 埋点 1
        {"role": "assistant", "content": "明白，会注意避开花季景点。"},
    ]

    # 中间是一段真实感的旅行对话（每轮一问一答，约 25 轮）
    _filler_qa = [
        ("故宫门票需要提前预约吗？", "建议提前在官网预约，现场票经常售罄，尤其旺季。"),
        ("从故宫到颐和园怎么走方便？", "地铁 4 号线直达北宫门站，大约 40 分钟。"),
        ("北京 6 月天气怎么样？", "6 月已经偏热，白天 30°C 左右，注意防晒补水。"),
        ("有没有适合拍照的胡同？", "南锣鼓巷、杨梅竹斜街都不错，建议早上去人少。"),
        ("长城哪个段落人少一点？", "慕田峪比八达岭人少很多，景色也更好。"),
        ("天坛几点开门？", "公园 6:00 开门，祈年殿等核心景点 8:00 开放。"),
        ("北京烤鸭哪家好？", "全聚德、便宜坊是老字号，四季民福性价比也不错。"),
        ("需要带现金吗？", "基本不用，手机支付覆盖几乎所有场景。"),
        ("798 艺术区值得去吗？", "喜欢当代艺术的话很推荐，周末还有各种展览和集市。"),
        ("早晚高峰地铁挤吗？", "8-9 点和 17-19 点非常拥挤，建议错峰出行。"),
        ("什刹海晚上有什么玩的？", "可以坐游船、逛酒吧街，夏天夜晚很热闹。"),
        ("国家博物馆需要身份证吗？", "是的，需要身份证或护照，提前预约可以走快速通道。"),
        ("簋街有什么推荐菜？", "麻辣小龙虾是招牌，很多店营业到凌晨。"),
        ("从大兴机场到市区怎么走？", "乘坐地铁最实惠，非高峰期最快；打车约 100-400 元，看路况和车型。"),
        ("圆明园和颐和园选一个？", "颐和园更完整更好逛，圆明园偏历史遗迹感。"),
        ("有没有免费的景点？", "奥林匹克公园、前门大街、琉璃厂都免费，值得逛。"),
        ("北京的出租车好打吗？", "路边招手不容易，建议用打车软件。"),
        ("王府井小吃街还值得去吗？", "本地人很少去，更推荐牛街或护国寺小吃。"),
        ("后海白天好看还是晚上好看？", "各有味道，白天安静看景，晚上热闹泡吧。"),
        ("香山现在有红叶吗？", "6 月没有红叶，夏天爬山看绿野也不错。"),
        ("鸟巢可以进去参观吗？", "可以的，买票进内部参观，水立方也挨在一起。"),
        ("北京的公共交通用什么卡？", "亿通行 App 扫码就行，地铁公交都能用。"),
        ("景山公园值得爬吗？", "很值得！山顶俯瞰故宫全景是经典机位。"),
        ("北大清华能进去逛吗？", "需要预约，一般提前在公众号上申请参观名额。"),
        ("回程想带点特产，推荐什么？", "稻香村糕点、张一元茶叶、内联升布鞋都挺有特色。"),
    ]
    for index in range(n_rounds - 5):
        question, answer = _filler_qa[index % len(_filler_qa)]
        msgs += [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]

    # 倒数第二轮再透露一个关键约束（晚期重要事实）
    msgs += [
        {"role": "user", "content": "对了，我的预算是每天 500 元。"},  # ⭐ 埋点 2
        {"role": "assistant", "content": "我会把每天行程控制在预算内。"},
    ]

    return msgs


def strategy_truncate(messages: list[dict], keep_last: int = 6) -> list[dict]:
    """截断策略：保留所有 system 消息 + 最近 N 轮对话。

    先从完整消息列表中提取所有 system 消息，再取末尾 `keep_last`
    条非 system 消息，最后拼接返回。这样无论 `keep_last` 多大，
    也不会导致 system 消息重复出现。

    Args:
        messages: 完整的消息列表。
        keep_last: 保留的最近消息条数（不含 system），默认 6。

    Returns:
        截断后的消息列表。
    """
    keep_last = keep_last if keep_last > 0 else 6

    sys_msgs = [m for m in messages if m["role"] == "system"]
    non_sys = [m for m in messages if m["role"] != "system"]
    recent = non_sys[-keep_last:] if keep_last < len(non_sys) else non_sys
    return sys_msgs + recent


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
    keep_last = keep_last if keep_last > 0 else 6

    non_sys = [m for m in messages if m["role"] != "system"]
    # 消息量不足，无需压缩，直接返回原文
    if len(non_sys) <= keep_last:
        return messages

    sys_msgs = [m for m in messages if m["role"] == "system"]
    # 将非 system 消息切分为中间段和最近段（两者无重叠、无遗漏）
    middle = non_sys[:-keep_last]
    recent = non_sys[-keep_last:]

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


KEY_FACT_KEYWORDS = {"过敏", "预算", "重要", "对了", "一定要", "不要"}


def _contains_key_fact(text: str) -> bool:
    """判断文本是否包含关键事实关键词。"""
    return any(kw in text for kw in KEY_FACT_KEYWORDS)


def extract_key_facts(messages: list[dict]) -> list[str]:
    """基于关键词匹配从历史消息中提取用户的关键事实（硬约束）。

    遍历所有消息，筛选出 `role == "user"` 且内容包含预定义关键词
    （由模块常量 `KEY_FACT_KEYWORDS` 定义，当前为 `{"过敏", "预算",
    "重要", "对了", "一定要", "不要"}`）的句子，提取后作为"关键事实槽"
    注入到上下文中，确保这些硬约束在上下文压缩后仍然显式可见。

    这是分层策略（strategy_hierarchical）的核心组件之一：即便早期对话
    被 LLM 摘要压缩后丢失了部分细节，通过关键词预先"打捞"出的关键事实
    仍会以独立 system 消息的形式保留在上下文中。

    Args:
        messages: 完整的消息列表，每条消息为 `{"role": str, "content": str}`
            格式。仅检查 `role == "user"` 的消息，system 和 assistant
            消息会被跳过。

    Returns:
        提取到的关键事实列表，每个元素是一条 user 消息的完整 `content`
        文本（已去首尾空白）。顺序保持原消息的出现顺序。如果没有任何消息
        命中关键词，返回空列表 `[]`。

    Note:
        - 当前实现是纯规则匹配（关键词子串查找），而非语义理解。
          生产环境中可升级为 LLM 驱动的语义提取，以识别隐式约束
          （如"我不能吃辣"虽不含关键词，但同样属于硬约束）。
        - 关键词集合 `KEY_FACT_KEYWORDS` 是模块级常量，可根据业务
          场景增删，无需修改函数逻辑。
        - 返回的每条事实可能与原始 user 消息完全相同（包含整句话），
          而非仅提取关键词所在的子句。

    Example:
        >>> msgs = [
        ...     {"role": "user", "content": "我对花粉过敏"},
        ...     {"role": "assistant", "content": "好的"},
        ...     {"role": "user", "content": "今天天气不错"},
        ...     {"role": "user", "content": "预算是每天 500 元"},
        ... ]
        >>> extract_key_facts(msgs)
        ['我对花粉过敏', '预算是每天 500 元']
    """
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

    # 委托 strategy_summary 做中间段压缩 + 保留最近 N 轮原文
    # strategy_summary 的返回值结构为：sys_msgs + [摘要] + recent
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
    return "过敏" in text, "预算" in text


# ============================================================
# 主测试
# ============================================================
def main() -> None:
    history = build_fake_history(n_rounds=30)
    print(f"历史 messages: {len(history)} 条 / {sum(len(m['content']) for m in history)} 字符\n")

    keep_last = 6
    strategies = {
        "① RAW (not process)": history,
        f"② TRUNCATE (Last {keep_last} rounds)": strategy_truncate(history, keep_last=keep_last),
        f"③ SUMMARY (summary + Last {keep_last} rounds)": strategy_summary(history, keep_last=keep_last),
        f"④ HIERARCHICAL (Key Facts + summary + Last {keep_last} rounds)": strategy_hierarchical(history, keep_last=keep_last),
    }

    # 用 prettytable 打印对比表（无边框）
    table = PrettyTable()
    table.field_names = ["Strategy", "Item", "Character", "Allergy", "Budget"]
    table.border = False       # 去掉所有边框线
    table.align["Strategy"] = "l"  # 左对齐
    table.align["Item"] = "r"
    table.align["Character"] = "r"
    table.align["Allergy"] = "c"
    table.align["Budget"] = "c"

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
