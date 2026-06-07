"""极简上下文构建器 —— 实现 GSSC 流水线。

GSSC = Gather → Select → Structure → Compress

核心思想：在每次调用 LLM 前，以可控的方式拼装最优上下文。
支持普通对话和 Function Calling 两种消息格式。
"""

from dataclasses import dataclass, field
from datetime import datetime
from math import exp
from typing import Any, Dict, List, Self
from enum import StrEnum, auto


class Source(StrEnum):
    """信息包的来源标签，决定它在 `_structure` 阶段被组装到哪个 role。

    设计上，`Source` 不是 OpenAI 的 `role` 的别名，而是一层**业务语义**：
    多个 `Source` 可能映射到同一个 `role`（如 `TOOL` 和 ``MEMORY`` 都被
    汇总进 `system` 的 `[参考信息]` 段），用于在打分、排序、组装阶段做
    更细粒度的策略控制。

    Members:
        USER: 用户的历史发言。**默认值**，会被组装进 `role="user"` 的历史
            对话段；保留 `timestamp` 用于时间序还原。
        SYSTEM: 外部传入的系统级提示。**当前实现下被 `_structure` 静默忽略**
            ——system prompt 由 `ContextBuilder(system_prompt=...)` 统一注入，
            不要通过 `add()` 走这条来源。保留该枚举值是为了未来支持多段
            system 拼接（如人格/规则/安全策略分层）。
        MEMORY: 长期记忆 / RAG 检索回来的历史片段（如向量库命中、对话摘要）。
            被视为“外部参考资料”，与 `TOOL` 一起拼入 system 的 `[参考信息]`
            段，避免冒充用户发言。
        TOOL: 工具调用的执行结果（普通对话模式下的 GSSC 流水线使用）。同样
            归入 system 的 `[参考信息]` 段。
            注意：Function Calling 模式（`append` / `get_messages`）下的
            tool 结果走的是 `role="tool"` 协议字段，与本枚举无关。
        ASSISTANT: 助手的历史回复。会被组装进 `role="assistant"` 的历史对话
            段，与 `USER` 交替形成完整对话上下文。
    """

    USER = auto()
    SYSTEM = auto()
    MEMORY = auto()
    TOOL = auto()
    ASSISTANT = auto()


@dataclass(frozen=True)
class ContextPacket:
    """候选信息包：上下文构建的最小单元。"""

    content: str
    source: Source = Source.USER
    relevance: float = 0.5  # 相关性 0.0~1.0
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int = field(init=False, repr=False, compare=False, hash=False)

    def __post_init__(self) -> None:
        if not 0.0 <= self.relevance <= 1.0:
            raise ValueError(
                f"relevance must be in [0.0, 1.0], got {self.relevance!r}"
            )
        if not self.content:
            raise ValueError("content must not be empty")

        # 2. 预计算 token_count（frozen 下必须用 object.__setattr__ 绕过守卫）
        cn_chars = sum(1 for c in self.content if "\u4e00" <= c <= "\u9fff")
        en_words = len(self.content.split()) - cn_chars
        token_count = cn_chars + max(0, int(en_words * 1.3))
        object.__setattr__(self, "token_count", token_count)


@dataclass
class ContextConfig:
    """上下文构建配置。"""

    max_tokens: int = 3000  # 总 token 预算
    reserve_ratio: float = 0.2  # 系统指令预留比例
    recency_weight: float = 0.3  # 新近性权重
    relevance_weight: float = 0.7  # 相关性权重
    min_relevance: float = 0.1  # 最低相关性阈值
    keep_recent: int = 10  # 压缩时保留最近消息数


class ContextBuilder:
    """上下文构建器，实现 GSSC 四阶段流水线。

    支持两种使用模式：

    模式 A（普通对话）：
        builder = ContextBuilder(system_prompt="你是一个助手")
        builder.add("历史对话", source=Source.MEMORY, relevance=0.6)
        messages = builder.build(user_input="当前问题")

    模式 B（Function Calling）：
        builder = ContextBuilder(system_prompt="你是编程助手")
        builder.append({"role": "user", "content": "..."})
        builder.append({"role": "assistant", "tool_calls": [...]})
        builder.append({"role": "tool", "tool_call_id": "...", "content": "..."})
        messages = builder.get_messages()
    """

    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant.",
        config: ContextConfig | None = None,
    ):
        self.system_prompt = system_prompt if system_prompt != "" else "You are a helpful assistant."
        self.config = config or ContextConfig()
        self._packets: List[ContextPacket] = []
        # Function Calling 模式的完整消息列表
        self._messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]

    # ========== 模式 A：基于 ContextPacket 的 GSSC 流水线 ==========

    def add(
        self,
        content: str,
        source: Source = Source.USER,
        relevance: float = 0.5,
        timestamp: datetime | None = None,
    ) -> Self:
        """添加一条候选信息包（支持链式调用）。

        Example:
            >>> messages = (
            ...     ContextBuilder()
            ...     .add("memory chunk", source=Source.MEMORY)
            ...     .add("tool result", source=Source.TOOL)
            ...     .build("当前问题")
            ... )

        source 既接受 Source 枚举，也接受合法字符串（如 "user"）；
        传入非法值会直接抛出 ValueError。

        relevance 仅支持 [0, 1.0]，超出边界也会直接抛出 ValueError。
        """
        packet = ContextPacket(
            content=content,
            source=Source(source),
            relevance=relevance,
            timestamp=timestamp or datetime.now(),
        )
        self._packets.append(packet)
        return self

    def build(self, user_input: str) -> List[Dict[str, str]]:
        """执行 GSSC 流水线，输出可直接喂给 LLM 的 messages 列表（模式 A）。

        四阶段与代码的映射关系：
            - Gather    ：由历次 `add()` 累积到 `self._packets`，本方法直接复用，
                          不在此处再做收集。
            - Select    ：`_select()` 按“相关性 × 权重 + 新近性 × 权重”打分，
                          在 token 预算（`max_tokens × (1 - reserve_ratio)`）内贪心挑选。
            - Structure ：`_structure()` 组装成 OpenAI 风格的
                          `system / user / assistant` 消息序列。
            - Compress  ：`_compress_simple()` 在仍超预算时从中间截断历史消息。

        Args:
            user_input: 当前用户输入（必填）。会作为最末一条 `user` 消息追加，
                即便候选集为空也保证 messages 非空、可直接调用 LLM。

        Returns:
            OpenAI 兼容的 messages 列表，形如::

                [
                    {"role": "system",    "content": "..."},
                    {"role": "user",      "content": "..."},
                    {"role": "assistant", "content": "..."},
                    {"role": "user",      "content": user_input},
                ]
        """
        packets = self._packets.copy()
        selected = self._select(packets, user_input)
        messages = self._structure(selected, user_input)
        messages = self._compress_simple(messages)
        return messages

    # ========== 模式 B：Function Calling 消息管理 ==========

    def append(self, message: Dict[str, Any]) -> Self:
        """追加一条完整消息（支持 tool_calls、tool 等特殊格式）。"""
        self._messages.append(message)
        return self

    def get_messages(self) -> List[Dict[str, Any]]:
        """获取完整的 messages 列表（自动压缩如果超预算）。"""
        self._compress_messages()
        return self._messages.copy()

    def _compress_messages(self):
        """压缩 Function Calling 格式的对话历史。

        策略：保留 system（首条）+ 最近 N 条消息，中间部分生成摘要。
        注意保持 tool_calls 和 tool 的配对完整性。
        """
        total_tokens = self._estimate_messages_tokens(self._messages)
        budget = self.config.max_tokens

        if total_tokens < budget * 0.8:
            return  # 还没超预算

        keep_recent = self.config.keep_recent
        if len(self._messages) <= keep_recent + 1:
            return  # 消息太少，不压缩

        # 找到安全的分割点：不能切断 tool_calls 和 tool 的配对
        cut_end = len(self._messages) - keep_recent
        # 向后调整，确保不切断 tool/tool_calls 配对
        while cut_end < len(self._messages) and self._messages[cut_end].get("role") == "tool":
            cut_end += 1

        if cut_end >= len(self._messages) - 2:
            return  # 没有可压缩的空间

        # 提取被压缩部分的摘要
        middle = self._messages[1:cut_end]
        summary = self._summarize_messages(middle)

        # 重建：system + 摘要伪对话 + 最近消息
        self._messages = (
            [self._messages[0]]  # system
            + [
                {"role": "user", "content": f"[对话历史摘要]\n{summary}"},
                {"role": "assistant", "content": "好的，我已了解之前的对话内容，请继续。"},
            ]
            + self._messages[cut_end:]
        )

    @staticmethod
    def _summarize_messages(messages: List[Dict[str, Any]]) -> str:
        """将一组消息压缩为文本摘要。"""
        parts = []
        for m in messages:
            role = m.get("role", "")
            content = m.get("content", "") or ""
            if role == "user" and content:
                parts.append(f"- 用户: {content[:80]}")
            elif role == "assistant" and content:
                parts.append(f"- 助手: {content[:80]}")
            elif role == "tool" and content:
                parts.append(f"- 工具结果: {content[:60]}")
        # 只保留最近几条摘要
        return "\n".join(parts[-8:]) if parts else "（无历史）"

    def _estimate_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """估算一组 messages 的总 token 数。"""
        total = 0
        for m in messages:
            content = m.get("content", "") or ""
            total += self._estimate_tokens(content)
            # tool_calls 的 arguments 也占 token
            for tc in m.get("tool_calls", []):
                args = tc.get("function", {}).get("arguments", "")
                total += self._estimate_tokens(args)
        return total

    # ========== 通用方法 ==========

    def clear(self) -> None:
        """清空所有状态。"""
        self._packets.clear()
        self._messages = [{"role": "system", "content": self.system_prompt}]

    # ========== 内部方法（GSSC） ==========

    def _score(self, packet: ContextPacket, _query: str) -> float:
        """计算综合分数 = 相关性权重×相关性 + 新近性权重×新近性。

        相关性直接读取 `packet.relevance`（由上游检索/记忆模块在 `add`
        时预先打分），新近性按 `timestamp` 做 24 小时衰减的指数函数；
        两者按 `config` 中的权重线性加权得到最终分数，供 `_select`
        做贪心排序。

        Args:
            packet: 候选信息包，其 ``relevance`` 字段应已由上游写入。

            _query: 当前用户查询。**目前未使用**，以下划线前缀显式标注
                “故意不用”，作为接口预留位：未来若引入动态相关性
                （如关键词命中、向量相似度、LLM rerank），可在此函数内
                直接消费该参数，`_select` 调用点无需改动。

        Returns:
            加权综合分数（未归一化），数值越大表示该信息包越值得纳入上下文。
        """
        cfg = self.config
        relevance = packet.relevance
        age_hours = (datetime.now() - packet.timestamp).total_seconds() / 3600

        # exp(-age_hours / 24) → 映射到 (0, 1]
        recency = exp(-age_hours / 24)
        return cfg.relevance_weight * relevance + cfg.recency_weight * recency

    def _select(
        self,
        packets: List[ContextPacket],
        query: str,
    ) -> List[ContextPacket]:
        """在 token 预算内贪心挑选价值最高的信息包。

        策略：按综合分数（相关性 + 新近性）从高到低排序，依次尝试纳入；
        分数低于阈值或会撑爆预算的直接跳过，最终返回入选子集。

        Args:
            packets: 候选信息包集合（顺序无要求，本方法不会就地修改）。
            query: 当前用户查询，用于驱动 `_score` 的相关性计算。

        Returns:
            入选的信息包列表，按分数降序排列；总 token 数不超过预算。
        """

        cfg = self.config
        # 预留 reserve_ratio 比例给 system prompt、当前输入与模型回复
        budget = int(cfg.max_tokens * (1 - cfg.reserve_ratio))

        # 打分并按分数降序排序，越靠前价值越高
        scored = [(p, self._score(p, query)) for p in packets]
        scored.sort(key=lambda x: x[1], reverse=True)

        # 贪心装包：跳过低分项与超预算项，遍历完即得近似最优解
        selected: List[ContextPacket] = []
        used_tokens = 0
        for packet, score in scored:
            if score < cfg.min_relevance:
                # 分数已降序，理论上后续都不达标，但保留 continue 以兼容
                # 未来可能引入的非单调评分函数
                continue
            if used_tokens + packet.token_count > budget:
                # 当前包放不下，但后面可能有更小的包能塞进剩余预算
                continue
            selected.append(packet)
            used_tokens += packet.token_count

        return selected

    def _structure(
        self,
        selected: List[ContextPacket],
        user_input: str,
    ) -> List[Dict[str, str]]:
        """GSSC 的 **Structure** 阶段：把扁平的信息包列表组装成 OpenAI 消息序列。

        `_select` 输出的是一组无结构的 `ContextPacket`，但 LLM 需要的是
        `[{"role": ..., "content": ...}, ...]`。本方法负责按 `Source` 把信息
        分门别类、放到正确的 role 中，并保证最终 messages 序列**符合对话语义、
        可直接调用 LLM**。

        组装规则（按输出顺序）：

        1. **system 消息（恒有且唯一）**

           - 起手是 `self.system_prompt`。
           - `Source.TOOL` / `Source.MEMORY` 视为“外部参考资料”，统一拼到
             system 里、用 `[参考信息]` 标题与 `---` 分隔，避免冒充用户发言
             造成模型误解。无参考资料时不插入空标题。

        2. **历史对话（user / assistant 交替）**

           - `Source.USER` → `role="user"`，`Source.ASSISTANT` → `role="assistant"`。
           - 按 `timestamp` **升序**（注意：`_select` 是按分数降序的，这里要
             重新按时间排，否则对话语义会乱）。
           - **同角色相邻自动合并**：用 `"\\n"` 连接 content，避免出现
             `user / user / user` 这种被部分 LLM 接口拒绝的非法序列，同时减少
             消息条数、节省协议开销。

        3. **当前用户输入（必有，且一定在末尾）**

           - 若末条已是 `user` 角色，`user_input` 直接续写到它后面，保持
             “历史 user 与当前问题”同条；否则追加一条新的 `user` 消息。
           - 这条规则确保**返回的 messages 末尾永远是 user**，是后续 LLM 调用
             `chat.completions.create` 的硬性要求。

        被忽略的 `Source.SYSTEM` 信息包：当前实现**不会**把 `Source.SYSTEM`
        的包放进任何 role——system prompt 由构造器统一注入，外部传入的“系统级
        提示”应通过 `ContextBuilder(system_prompt=...)` 而非 `add()`。

        Args:
            selected: `_select` 选出的信息包子集，**顺序无要求**（本方法内部
                会按 source 分流并按时间重排）。
            user_input: 当前用户原始输入，作为最末一条 user 消息追加；即便
                `selected` 为空也保证 messages 至少包含 ``[system, user]``
                两条。

        Returns:
            OpenAI 兼容的 messages 列表，结构形如::

                [
                    {"role": "system",    "content": "<sys> + [参考信息]..."},
                    {"role": "user",      "content": "历史 user1\\n历史 user2"},
                    {"role": "assistant", "content": "..."},
                    {"role": "user",      "content": "<历史 user> + user_input"},
                ]

            其中 system 必为首条、user 必为末条；中间的 user/assistant 严格按
            时间序交替排列，且不会出现两条相邻同角色消息。
        """
        messages: List[Dict[str, str]] = []

        # ---- ① system：基础指令 + 外部参考资料 ----
        system_parts = [self.system_prompt]
        context_pieces = [
            p.content for p in selected if p.source in (Source.TOOL, Source.MEMORY)
        ]
        if context_pieces:
            # 仅当真有参考资料时才插标题，避免空段落污染 prompt
            system_parts.append("\n[参考信息]\n" + "\n---\n".join(context_pieces))
        messages.append({"role": "system", "content": "\n\n".join(system_parts)})

        # ---- ② 历史对话：按时间升序还原对话脉络，相邻同角色自动合并 ----
        history = [p for p in selected if p.source in (Source.USER, Source.ASSISTANT)]
        history.sort(key=lambda p: p.timestamp)
        for p in history:
            role = "user" if p.source == Source.USER else "assistant"
            if messages and messages[-1]["role"] == role:
                # 合并到上一条同角色消息，避免产生 user/user 这种非法序列
                messages[-1]["content"] += "\n" + p.content
            else:
                messages.append({"role": role, "content": p.content})

        # ---- ③ 当前用户输入：必须放在末尾，且整条 messages 以 user 收口 ----
        if messages[-1]["role"] == "user":
            messages[-1]["content"] += "\n" + user_input
        else:
            messages.append({"role": "user", "content": user_input})

        return messages

    def _compress_simple(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """GSSC 的 **Compress** 阶段（模式 A）：超预算时从中间截断历史消息。

        这是兜底压缩器，用在 `_select` 之后再做一次“保险”——尽管 `_select`
        已经按预算贪心装包，但拼接 system prompt + 当前 user_input 之后整体
        长度仍可能越界（尤其是 system 里塞了大段 `[参考信息]` 时）。本方法
        负责把 messages 强制压回预算之内。

        策略：**保头保尾、从中间截断**。

        - **首条 system 永不动**：它承载着角色设定与参考资料，丢了 LLM 行为
          会立刻跑偏。
        - **末条永不动**：约定是“当前用户输入”，丢了对话就没意义了。
        - **中间从最旧开始丢**（``messages.pop(1)``）：旧消息相关性已经被
          时间衰减压低，丢起来代价最小；同时实现简单，无需重新打分。

        与 `_compress_messages` 的分工：

        - `_compress_simple`（本方法）：模式 A，messages 只可能是 `system /
          user / assistant` 三种 role，**没有 tool_calls 配对**问题，可以放心
          逐条 pop。
        - `_compress_messages`：模式 B（Function Calling），需要保护
          `tool_calls` 与 `role="tool"` 的配对完整性，逻辑复杂得多。
          两者**不可互换**。

        Args:
            messages: `_structure` 输出的完整 messages，至少含 `[system, user]`
                两条。**会被就地修改**（`list.pop`），同时也作为返回值返回，
                调用方无需关心是原地还是复制。

        Returns:
            压缩后的 messages，满足 `总 tokens ≤ config.max_tokens`；
            首条 system 与末条 user_input 必定保留。

        Note:
            1. 本方法是**有损压缩**——被 `pop` 掉的中间历史消息**完全丢弃**，
               不会做摘要。需要“压缩 + 摘要”的语义保留，请用模式 B 的
               `_compress_messages`。
            2. 极端情况下若 system + 末条 user 自身就已超预算，循环条件
               `len(messages) > 2` 会兜底退出，此时返回的 messages 仍可能
               超预算——这种情况说明 `max_tokens` 配得太小，应在配置层修复，
               而不是在压缩层硬截断关键信息。
            3. token 估算用的是 `_estimate_tokens`（粗略规则），与真实
               tokenizer 有一定误差，预算建议留足余量。
        """
        total = sum(self._estimate_tokens(m["content"]) for m in messages)
        if total <= self.config.max_tokens:
            # 没超预算，直接放行，避免无谓的内存写
            return messages

        # 保头（system，index 0）+ 保尾（当前 user_input，index -1）
        # 反复 pop(1) 即"从最旧的中间消息开始丢"
        while total > self.config.max_tokens and len(messages) > 2:
            removed = messages.pop(1)
            total -= self._estimate_tokens(removed["content"])

        return messages

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """粗略估算 token 数。"""
        cn_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        en_words = len(text.split()) - cn_chars
        return cn_chars + max(0, int(en_words * 1.3))
