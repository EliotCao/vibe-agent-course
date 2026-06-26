"""
Demo 21 · Agent v2：将最小 Agent Loop 接入 ContextManager + Memory
==================================================================

把 第 3/4 章的朴素 Agent Loop 升级为 v2，接入第 5 章的两大组件：

  ① ContextManager
     —— 每轮调 LLM 前自动压缩 messages，防止上下文爆炸

  ② Memory
     —— 每轮自动召回相关长期事实，注入 system prompt
     —— 对话结束时由 LLM 提炼关键事实，写入长期记忆

跑 12 轮旅行规划任务，直观对比：
  - v1 朴素 Agent 与 v2 Agent 的 token 消耗差异
  - 关键事实（早期透露的过敏 / 预算）在 Memory 加持下是否被保住

运行方式：
    source /workspace/.venv/bin/activate
    python demo_21_agent_v2.py
"""

from _env import get_model_id, chat
from demo_19_context_strategies import strategy_hierarchical
from demo_20_memory import (
    Memory,
    MemoryEntry,
    embed,
    cosine,
)


# ============================================================
# ContextManager：把 demo_19 的策略包成一个类
# ============================================================
class ContextManager:
    """对话上下文管理器，负责控制上下文窗口大小并执行分层压缩策略。

    当对话消息累积过多，超出模型上下文窗口上限时，需要对历史消息进行压缩。
    本类封装了"何时压缩"的判断逻辑和"如何压缩"的压缩策略，
    使调用方无需关心底层细节。

    核心策略（分层）：
        1. 系统提示词（role="system"）始终保留，不参与压缩。
        2. 用户硬约束 / 关键事实单独抽提，以独立 system 消息前置注入。
        3. 距离当前最近的 `keep_last` 条消息保留原文，保证即时对话质量。
        4. 超出 `keep_last` 范围的早期消息触发 LLM 摘要压缩，
           用简短摘要替代原始冗长历史。

    Attributes:
        keep_last (int): 压缩时保留的最近消息条数，这些消息不会被摘要化。
        max_messages (int): 触发压缩的阈值，当消息总数超过此值时会启动压缩流程。

    Note:
        - 实际压缩逻辑委托给外部函数 `strategy_hierarchical`，
          本类只作为配置容器和门面（Facade）。
        - 压缩阈值应小于模型真实上下文上限，为当前轮次的新消息留出空间。

    Example:
        >>> ctx = ContextManager(keep_last=4, max_messages=15)
        >>> if ctx.should_compress(messages):
        ...     messages = ctx.compress(messages)
    """

    def __init__(self, keep_last: int = 6, max_messages: int = 20) -> None:
        """初始化上下文管理器。

        Args:
            keep_last: 压缩时保留的最近消息条数，默认 6 条。
                值越小，压缩越激进，能节省越多 token，但可能丢失细节。
            max_messages: 触发压缩的消息总数阈值，默认 20 条。
                当消息列表长度超过此值时，`should_compress()` 返回 True。
        """
        self._keep_last = keep_last if keep_last > 0 else 6
        self._max_messages = max_messages if max_messages > 0 else 20

    @property
    def keep_last(self) -> int:
        return self._keep_last

    @property
    def max_messages(self) -> int:
        return self._max_messages

    def should_compress(self, messages: list[dict]) -> bool:
        """判断当前消息列表是否需要压缩。

        检查逻辑简单直观：当消息总数超过 `max_messages` 阈值时返回 True。

        Args:
            messages: 完整的消息列表，每条消息为 `{"role": str, "content": str}` 格式。

        Returns:
            True 表示需要调用 `compress()` 进行压缩，False 表示无需操作。

        Example:
            >>> ctx = ContextManager(max_messages=10)
            >>> ctx.should_compress([{"role": "user", "content": "hi"}])
            False
        """
        return len(messages) > self.max_messages

    def compress(self, messages: list[dict]) -> list[dict]:
        """对消息列表执行分层压缩，返回压缩后的消息列表。

        压缩策略由 `strategy_hierarchical` 函数 实现。

        Args:
            messages: 待压缩的完整消息列表。调用方应确保传入的是当前对话的
                全部消息（含 system prompt），而非部分切片。

        Returns:
            压缩后的消息列表，长度和内容均可能发生变化。
            返回值可直接作为新的消息列表继续使用。

        Note:
            此方法不修改传入的 `messages`（幂等），返回值是新列表。
        """
        return strategy_hierarchical(messages, keep_last=self.keep_last)


class MemoryV2(Memory):
    """生产增强版记忆库，在 `Memory` 基础上增加了去重能力。

    与父类 `Memory` 的唯一区别在于 `add` 方法：`Memory.add` 直接追加条目，不做任何
    去重检查；而 `MemoryV2.add` 在写入前会先执行精确匹配和语义相似度双重去重，
    避免记忆库中出现重复或高度冗余的条目。

    去重策略（三步）：
        1. 精确文本匹配：若新文本与已有记忆的文本完全一致则直接跳过；
        2. 语义相似度检查：计算新文本与所有已有记忆的余弦相似度，
           若最高相似度超过阈值（默认 0.92），则用新文本替换最相似的那条记忆
           （而非简单跳过），因为新文本通常更完整或更准确；
        3. 正常添加：若以上两步均未命中，则作为全新记忆条目追加。

    适用场景：
        - 长期运行的 Agent，记忆会随时间累积，需要防止膨胀；
        - 多次调用 `distill_to_memory` 时，LLM 可能提炼出语义相似的事实；
        - 用户反复表达相同意图但措辞不同的场景。

    Note:
        语义去重阈值 0.92 为经验值，可根据业务场景调整。阈值越高越严格（容忍的
        相似度范围越窄），阈值越低则越容易将"不同但有关联"的记忆误判为重复。

    Example:
        >>> mem = MemoryV2()
        >>> mem.add("我每天预算 500 元。")
        >>> mem.add("我每天预算 500 元。")           # 精确重复，跳过
        >>> mem.add("我的日常预算是 500 块。")       # 语义重复，更新旧条目
        >>> len(mem.entries)
        1
    """

    def add(self, text: str, **meta) -> None:
        """添加一条新记忆到记忆库中（带去重检查）。

        先将文本编码为向量，然后依次执行精确文本匹配和语义相似度双重去重，
        确认不是重复记忆后再写入。具体逻辑与父类 `Memory.add` 的差异见下方 Note。

        Args:
            text: 要存储的记忆文本内容，通常来源于 LLM 从对话中提炼的事实。
            **meta: 可选的附加元数据，会存入 MemoryEntry.meta 字典中。
                例如 `category="budget"`、`priority=1` 等。

        Note:
            与 `Memory.add` 的核心差异：

            - 精确去重：若已有记忆的 `text` 与参数完全相同，则跳过不写入；
            - 语义去重：将新文本与所有已有记忆逐一计算余弦相似度，若存在
              相似度 > 0.92 的条目，则用新文本替换该条目（而非追加），
              以保证记忆库中始终保留最新版本的表述；
            - 无重复时追加：若以上两步均未命中，行为与 `Memory.add` 一致，
              直接追加新条目。

            另外，`Memory.add` 不做去重（用于教学演示最简实现），而 `MemoryV2.add`
            面向生产场景，适合记忆持续累积的长期运行 Agent。

        Example:
            >>> mem = MemoryV2()
            >>> mem.add("用户偏好靠窗座位。", category="seating")
            >>> mem.add("用户偏好靠窗座位。")  # 精确重复，跳过
            >>> mem.add("用户喜欢坐窗边。")    # 语义相似 > 0.92，更新旧条目
        """
        # ① 精确文本匹配：文本完全相同则跳过
        for entry in self._entries:
            if entry.text == text:
                return

        v = embed(text)

        # ② 语义相似度检查：计算与所有已有记忆的余弦相似度
        if self._entries:
            similarities = [cosine(v, e.vec) for e in self._entries]
            max_sim = max(similarities)
            if max_sim > 0.92:
                # ③ 去重命中：用新文本替换相似度最高的旧条目
                # 新文本通常更完整或更准确，因此选择"替换"而非"跳过"
                print(f"🔄 检测到高相似度记忆（{max_sim:.3f}），更新现有条目")
                max_idx = similarities.index(max_sim)
                self._entries[max_idx] = MemoryEntry(text=text, vec=v, meta=meta)
                return

        # ④ 无重复，正常追加
        self._entries.append(MemoryEntry(text=text, vec=v, meta=meta))
        return


# ============================================================
# Memory 提炼：用 LLM 从对话里提炼"值得长期记的事实"
# ============================================================
DISTILL_PROMPT = """阅读下面的对话，提炼出**值得长期记住的用户偏好、约束、关键事实**，
每条一行，不要把一次性的问答内容也存进去。
如果没有可记的事实，输出空。

对话：
{transcript}

# 输出格式
每行一条事实，纯文本，无序号
"""


def distill_to_memory(messages: list[dict], memory: Memory) -> None:
    """将完整对话记录提炼为长期事实，并写入 Memory 持久化存储。

    本函数在「对话会话结束时」调用，利用 LLM 从本轮对话中自动抽取
    值得跨会话保留的用户偏好、硬性约束和关键事实，
    避免人工整理记忆，实现记忆的自动化沉淀。

    处理流程（共 4 步）：
      1. 构建对话抄本（transcript）：过滤掉 system 消息（避免将系统提示词
         误当作对话内容），将剩余消息拼接为 `role: content` 格式的文本。
      2. 调用 LLM 提炼：将抄本填入 `DISTILL_PROMPT` 模板，以 `temperature=0`
         调用 LLM，要求输出纯文本事实列表（每行一条）。
      3. 清洗 LLM 输出：对返回文本按行拆分，去除空行，
         并去除每行开头可能存在的 `- ` 列表符号及首尾空白。
      4. 写入 Memory：遍历清洗后的事实列表，逐条调用 `memory.add()`
         持久化。若传入的是 `MemoryV2` 实例，`add()` 会自动做精确匹配
         和语义相似度双重去重，避免重复条目；若传入的是 `Memory` 实例，
         则不做去重，多次提炼相同事实会产生重复。

    Args:
        messages: 完整对话消息列表，通常来自 `agent.messages`。
            列表元素为 `{"role": str, "content": str}` 格式的字典。
            函数内部会自动过滤 `role == "system"` 的消息，
            仅将用户与助手的对话内容提供给 LLM 进行提炼。
        memory: 长期记忆实例（`Memory` 或其子类如 `MemoryV2`），
            用于持久化存储提炼后的事实。函数会直接修改该实例
            （调用 `memory.add()`），调用方无需额外处理返回值
            即可获得更新后的记忆。推荐传入 `MemoryV2` 以获得自动去重能力。

    Note:
        - LLM 调用参数 `temperature=0` 确保输出确定性，
          避免同一次对话提炼出不同结果。
        - `max_tokens=300` 限制提炼输出长度，防止单次提炼消耗过多 token。
        - 清洗逻辑 `line.strip("- ").strip()` 可同时处理
          `- 事实内容`` 和 ``事实内容` 两种 LLM 输出格式。
        - `Memory.add()` 不做去重，若传入的是 `Memory` 实例且多次调用
          `distill_to_memory`（或手动多次 `add()` 同一内容），
          `memory.entries` 中会出现重复条目。若传入的是 `MemoryV2` 实例，
          则 `add()` 内置精确匹配 + 语义相似度双重去重，可有效避免重复。

    Example:
        >>> memory = Memory()
        >>> msgs = [
        ...     {"role": "system", "content": "你是个助手。"},
        ...     {"role": "user", "content": "我对坚果过敏。"},
        ...     {"role": "assistant", "content": "好的，已记录。"},
        ... ]
        >>> distill_to_memory(msgs, memory)
        >>> print(len(memory.entries) > 0)
        True
    """
    # 第 1 步：构建对话抄本，过滤 system 消息，避免将系统提示词送入 LLM
    transcript = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages if m["role"] != "system"
    )

    # 第 2 步：调用 LLM，将对话抄本填入模板，请求提炼长期事实
    msg = chat(
        messages=[{"role": "user", "content": DISTILL_PROMPT.format(transcript=transcript)}],
        temperature=0,       # 零温度，确保输出稳定可复现
        max_tokens=300,      # 限制输出长度，控制 token 消耗
    )

    # 第 3 步：清洗 LLM 输出，按行拆分并去除空白行和列表符号
    raw = msg.content or ""
    facts = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]

    # 第 4 步：将提炼出的事实逐条写入 Memory
    # 注意：若 memory 是 MemoryV2 实例，add() 会自动去重；
    #       若 memory 是 Memory 实例，则不做去重，可能产生重复条目。
    for f in facts:
        memory.add(f)
    return


# ============================================================
# Agent v2：组合 ContextManager + Memory
# ============================================================
class AgentV2:
    """增强版 Agent，整合了上下文压缩与长期记忆能力。

    相比第 4 章的朴素 Agent Loop，v2 新增以下能力：

    1. 上下文压缩：当消息列表超过阈值时，通过 ContextManager 自动压缩
       （截断 / 摘要 / 分层），避免 token 浪费。
    2. 记忆召回：每轮对话前，用用户输入检索 Memory 中的相关长期事实，
       将高置信度结果临时注入 system prompt，帮助模型"回忆"跨轮次信息。

    Attributes:
        system_prompt: 系统提示词（只读，初始化后不可修改）。
        memory: 长期记忆存储，提供语义搜索与事实存取。
        ctx: 上下文管理器，负责消息列表的压缩策略。
        messages: 当前会话的消息历史（首条为 system prompt）。

    Note:
        `system_prompt` 是只读属性，内部存储为 `_system_prompt`，
        且 `chat` 函数构建注入消息时直接复用 `self.messages[0]`，
        确保两处始终一致。

    Examples:
        >>> agent = AgentV2(system_prompt="你是旅行规划师。")
        >>> agent.memory.add("用户对花粉过敏。")
        >>> reply, prompt_tk, total_tk = agent.chat("推荐户外活动")
        >>> print(reply)
        '建议选择室内场所，因为您对花粉过敏……'
    """

    def __init__(
        self,
        system_prompt: str = "你是一个有用的助手。",
        memory: Memory | None = None,
        ctx_manager: ContextManager | None = None,
    ) -> None:
        """初始化 AgentV2 实例。

        Args:
            system_prompt: 系统提示词，决定 Agent 的角色与行为准则。
                默认值：`"你是一个有用的助手。"`
            memory: 长期记忆实例。传 `None` 时自动创建空的 `MemoryV2()`
                （带去重能力）。可传入 `Memory` 实例以获得无去重的原始行为。
            ctx_manager: 上下文压缩管理器。传 `None` 时使用默认
                `ContextManager(keep_last=6, max_messages=20)`。
        """
        self._system_prompt = system_prompt
        self.memory = memory or MemoryV2()
        self.ctx = ctx_manager or ContextManager()
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]

    @property
    def system_prompt(self) -> str:
        """只读的系统提示词。

        外部可读取，但不可修改，防止与 `self.messages[0]["content"]` 不一致。
        """
        return self._system_prompt

    def chat(self, user_input: str) -> tuple[str, int, int]:
        """处理一轮用户对话，返回模型回复及 token 消耗统计。

        处理流程（共 5 步）：

        1. 记忆召回 — 用 `user_input` 检索 Memory，将相似度 > 0.5
           的事实临时注入 system prompt（仅本轮有效，不写入 `self.messages`）。
        2. 构建消息列表 — 构造 `injected` 列表用于调 LLM，
           若触发了记忆召回则注入额外 system 消息。
        3. 上下文压缩 — 若消息数超过阈值，调用 ContextManager 压缩，
           压缩结果同样仅作用于本轮。
        4. 调用 LLM — 以 `temperature=0.3` 获取回复。
        5. 写回历史 — 将用户输入和助手回复追加到 `self.messages`，
           供后续轮次使用（不含临时注入的记忆消息）。

        Args:
            user_input: 用户本轮输入的文本。

        Returns:
            三元组 `(reply, prompt_tokens, total_tokens)`：
            - `reply`: 模型回复文本（可能为空字符串）。
            - `prompt_tokens`: 本轮 prompt 消耗的 token 数（含系统、历史与记忆）。
            - `total_tokens`: 本轮总 token 消耗（prompt + completion）。
        """
        injected = list(self.messages)
        # 1. 用 user_input 去 Memory 召回相关长期事实
        relevant = [(score, e) for score, e in self.memory.search(user_input, k=3) if score > 0.5]
        if relevant:
            facts_block = "\n".join(f"- {e.text}" for _, e in relevant)
            injected = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"[相关长期事实]\n{facts_block}"},
            ] + [m for m in self.messages[1:] if m["role"] != "system"]

        injected.append({"role": "user", "content": user_input})

        # 3. 检查是否需要压缩
        if self.ctx.should_compress(injected):
            print(f"  ⚙️  消息超过 {self.ctx.max_messages} 条，触发压缩")
            injected = self.ctx.compress(injected)

        # 4. 调 LLM（chat 函数内部强制流式，适配接口限制）
        msg = chat(
            messages=injected,
            temperature=0.3,
            max_tokens=400,
            model=get_model_id(),
        )
        reply = msg.content or ""
        usage = msg.usage

        # 5. 写回 messages（不含临时注入的那一条）
        self.messages.append({"role": "user", "content": user_input})
        self.messages.append({"role": "assistant", "content": reply})

        prompt_tk = usage.prompt_tokens if usage else 0
        total_tk = usage.total_tokens if usage else 0
        return reply, prompt_tk, total_tk


# ============================================================
# 跑一个 12 轮对话，把 第 2 章 vs 第 5 章 的 token 消耗对比一下
# ============================================================
def run_comparison() -> None:
    print("=" * 60)
    print("【对比测试】30 轮对话 v2 Agent 各轮 token 消耗")
    print("=" * 60)

    agent = AgentV2(
        system_prompt="你是旅行规划师。回答简洁、可执行。",
    )

    # 第 1 轮先存 2 个用户硬约束（模拟用户告诉过 Agent 的事）
    agent.memory.add("用户对花粉过敏，户外活动避开花期。")
    agent.memory.add("用户每日预算 500 元。")

    questions = [
        "我准备 6 月去北京玩 7 天。",
        "第 1 天有什么推荐？",
        "第 2 天呢？",
        "第 3 天去户外好不好？",  # ⭐ 应该触发"过敏"事实召回
        "第 4 天就在城里逛吧。",
        "第 5 天有没有什么文化体验？",
        "第 6 天我想体验下夜景。",
        "总结一下整体预算。",  # ⭐ 应该触发"预算"事实召回
        "改一下，第 3 天换室内景点。",
        "再给我推荐 2 个咖啡馆。",
        "夜场票好买吗？",
        "总结所有 7 天的行程，按天列出。",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n--- 第 {i} 轮 ---")
        print(f"用户: {q}")
        reply, prompt_tk, total_tk = agent.chat(q)
        print(f"助手: {reply[:150]}{'...' if len(reply) > 150 else ''}")
        print(f"      [prompt={prompt_tk} total={total_tk} messages={len(agent.messages)}]")

    print("\n\n" + "=" * 60)
    print("📝 对话结束，提炼记忆 → Memory")
    print("=" * 60)

    distill_to_memory(agent.messages, agent.memory)

    print(f"\n💾 Memory 现在有 {len(agent.memory.entries)} 条事实：")
    for entry in agent.memory.entries:
        print(f"  - {entry}")

    print("   下次会话时这些事实会自动召回，跨会话也'记得'用户。")


if __name__ == "__main__":
    run_comparison()

    print("\n\n" + "=" * 60)
    print("🎯 v2 Agent 跟 第 4 章 朴素版的区别")
    print("=" * 60)
    print("  ① ContextManager：messages 超过阈值时主动压缩（截断/摘要/分层）")
    print("  ② Memory 召回：每轮用 user_input 检索相关长期事实，注入到 system")
    print("  ③ Memory 提炼：对话结束时用 LLM 提炼新事实，写回 Memory")
    print()
    print("  这三件事加在一起，让你的 Agent 第一次有了'跨会话的记忆'。")
    print("  下一步（第 6/7 章）要做的：把这些组件接进真实的 Coding Agent。")
