"""第 3 章：用 `hello-agents` 框架快速搭一个 Agent。

前两章我们手写了：
- ch01：ReAct 循环（Thought-Action-Observation）
- ch02：流式 LLM 客户端

本章直接使用社区开源的 `hello-agents` 框架（v0.1.1），看看同样的能力
在框架里只需要几行代码就能搭起来。

本 demo 包含两个最小示例：
1. `SimpleAgent`：纯对话 agent，多轮上下文由框架自动维护。
2. `ReActAgent` + `CalculatorTool`：带工具调用的 ReAct agent，
   让模型自己思考并调用计算器解决一道数学题。

参考：https://github.com/jjyaoao/HelloAgents
"""

from hello_agents import (
    CalculatorTool,
    HelloAgentsLLM,
    ReActAgent,
    SimpleAgent,
    ToolRegistry,
)
from hello_agents.core.exceptions import HelloAgentsException

from config import get_api_key, get_base_url, get_model_id, get_timeout


def patch_react_agent_logging_and_parser() -> None:
    """给 ReActAgent 加调试日志，并放宽 Thought/Action 的解析正则。

    背景：
    框架默认的 prompt 里写的是 markdown 加粗格式 `**Thought:**` / `**Action:**`，
    但解析器（`_parse_output`）的正则却是严格的 `r"Thought: (.*)"`——只认
    "无星号、ASCII 冒号、紧跟一个空格"这一种写法。

    很多模型（DeepSeek、Qwen 等）会照抄 prompt 里的 markdown 加粗输出
    `**Thought:** ...`，结果正则匹配失败，agent 就在第 1 步打出
    "⚠️ 未能解析出有效的 Action，流程终止。"——看起来"啥都没干"。

    本补丁做两件事：
    1. 打印模型每一步的**原始响应全文**，便于排查这类格式问题。
    2. 用一条更宽松的正则同时识别：
         - `Thought:` / `**Thought:**` / `### Thought:` 等前缀变体
         - 英文冒号 `:` 与中文冒号 `：`
         - 冒号后允许 0~多个空格

    后续框架若收紧 prompt 或放宽正则，可删除此补丁。
    """
    import re
    from hello_agents.agents import react_agent as _ra

    # 同时认 `Thought:` / `**Thought:**` / `**Thought**:` / 中文冒号等变体；
    # 末尾的 `\**` 用来吃掉 `**Thought:** xxx` 里冒号之后紧跟的星号。
    THOUGHT_RE = re.compile(r"\**\s*Thought\s*\**\s*[:：]\s*\**\s*(.*)")
    ACTION_RE = re.compile(r"\**\s*Action\s*\**\s*[:：]\s*\**\s*(.*)")

    def lenient_parse(self, text):  # type: ignore[no-untyped-def]
        # —— 调试日志：把模型这一步的原始响应整段打出来 ——
        print("───── LLM 原始响应 ─────")
        print(text)
        print("──────────────────────")

        thought_match = THOUGHT_RE.search(text)
        action_match = ACTION_RE.search(text)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        # 模型可能把 action 写成 `**python_calculator[...]**`，去掉两端的装饰
        if action:
            action = action.strip("* ").strip()

        print(f"[parse] thought={thought!r}")
        print(f"[parse] action  ={action!r}")
        return thought, action

    _ra.ReActAgent._parse_output = lenient_parse  # type: ignore[assignment]


def patch_invoke_to_streaming() -> None:
    """让 `HelloAgentsLLM.invoke` 走流式底层，再把 chunk 拼回完整字符串。

    某些 OpenAI 兼容服务（部分企业网关、流式优化代理等）只支持 `stream=True`，
    非流式调用会被服务端直接 400 返回：
        'Non-stream chat request is currently not supported'

    框架原版 `invoke` 没有传 `stream=True`，因此 `ReActAgent` 这类内部走 `invoke`
    的 agent 在这种服务上完全不可用。本补丁的策略是：底层永远开 `stream=True`，
    把 chunk 聚合成完整字符串再返回——对调用方而言接口完全不变。

    后续框架版本若把 `invoke` 改为流式底层，可直接删掉此函数。
    """

    def invoke_via_stream(self, messages, **kwargs):  # type: ignore[no-untyped-def]
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                stream=True,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in ("temperature", "max_tokens", "stream")
                },
            )
            parts: list[str] = []
            for chunk in response:
                if not chunk.choices:  # 末尾的 usage 统计 chunk
                    continue
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    parts.append(delta)
            return "".join(parts)
        except Exception as e:  # 与原实现保持一致的异常类型
            raise HelloAgentsException(f"LLM调用失败: {e}") from e

    HelloAgentsLLM.invoke = invoke_via_stream  # type: ignore[assignment]


def build_llm() -> HelloAgentsLLM:
    """构造一个 `HelloAgentsLLM`，把项目统一的环境变量显式注入。

    这样就不需要再额外维护一套 `LLM_BASE_URL` / `LLM_API_KEY` 环境变量。
    """
    return HelloAgentsLLM(
        model=get_model_id(),
        api_key=get_api_key(),
        base_url=get_base_url(),
        timeout=get_timeout(),
    )


def demo_simple_agent(llm: HelloAgentsLLM) -> None:
    """Demo 1：最小对话 agent。"""
    print("=" * 60)
    print("Demo 1: SimpleAgent —— 多轮对话")
    print("=" * 60)

    agent = SimpleAgent(
        name="travel-buddy",
        llm=llm,
        system_prompt="你是一个简洁、专业的旅行助手，回答控制在 3 句话以内。",
    )

    questions = [
        "我下周想去成都玩 3 天，重点想吃。",
        "那行程里安排 1 天去都江堰会不会太赶？",
    ]
    for q in questions:
        print(f"\n👤 用户：{q}")
        print("🤖 助手：", end="", flush=True)
        # 注意：hello-agents 的 `think()` 内部已经会 print 每个 chunk，
        # 所以我们 **不再** 自己 `print(chunk)`，否则同一段内容会被打印两次
        # （表现为"推推荐荐住住在在春春熙熙路路…"的双字假象）。
        # 这里只把生成器消费完，让框架完成它的副作用即可。
        for _ in agent.stream_run(q):
            pass
        print()


def demo_react_agent(llm: HelloAgentsLLM) -> None:
    """Demo 2：ReAct agent + 计算器工具。

    让模型自己在「Thought → Action → Observation」循环里决定何时调用
    `calculator` 工具，框架已经把 prompt 和解析都封装好了。
    """
    print("\n" + "=" * 60)
    print("Demo 2: ReActAgent + CalculatorTool —— 工具调用")
    print("=" * 60)

    # 1) 注册工具
    registry = ToolRegistry()
    registry.register_tool(CalculatorTool())

    # 2) 构造 ReAct agent
    agent = ReActAgent(
        name="math-tutor",
        llm=llm,
        tool_registry=registry,
        system_prompt="你是一个会调用计算器工具的数学助教。",
        max_steps=10,
    )

    question = (
        "一家奶茶店第一周营业额 12,580 元，第二周比第一周多 18%，"
        "第三周比第二周少 350 元。请问三周总营业额是多少？"
    )
    print(f"\n👤 用户：{question}\n")
    answer = agent.run(question)
    print(f"\n✅ 最终答案：{answer}")


def main() -> None:
    # 当前 LLM 服务只支持流式调用，框架原版 `invoke` 是非流式会被 400 拒掉，
    # 这里把 `invoke` 也改成"流式底层 + 聚合返回字符串"。ReActAgent 依赖 `invoke`，
    # 不打这个补丁就跑不起来。
    patch_invoke_to_streaming()
    # 默认正则不认 `**Thought:**` 这种 markdown 加粗格式；这里放宽，
    # 同时打印每步原始响应，方便排查模型输出格式问题。
    patch_react_agent_logging_and_parser()

    try:
        llm = build_llm()
    except EnvironmentError as e:
        print(f"❌ 环境变量未配置：{e}")
        return

    # demo_simple_agent(llm)
    demo_react_agent(llm)


if __name__ == "__main__":
    main()
