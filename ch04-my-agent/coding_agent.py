"""CodingAgent —— 极简版 Claude Code。

基于 Function Calling + 对话循环 + 多工具，实现一个交互式编程助手。
通过 ContextBuilder 管理上下文预算，对话过长时自动压缩。
"""

import json
from typing import List, Optional

from llm import LLM
from tools import ToolRegistry
from tools_impl import ALL_TOOLS
from context_builder import ContextBuilder, ContextConfig

SYSTEM_PROMPT = """你是一个专业的编程助手（Coding Agent），可以帮助用户阅读、编写和修改代码。

## 能力
- 阅读和分析文件内容
- 创建和编辑文件
- 在项目中搜索代码
- 执行 shell 命令（安装依赖、运行测试等）
- 管理任务列表
- 抓取网页参考资料

## 工作原则
1. 先理解再动手：修改代码前先阅读相关文件
2. 最小改动：只修改必要的部分，避免重写整个文件
3. 解释清楚：告诉用户你做了什么、为什么这么做
4. 安全优先：危险操作前说明风险
"""


class CodingAgent:
    """交互式编程助手，基于 Function Calling 驱动工具调用。

    核心循环:
        用户输入 → ContextBuilder 管理上下文 → LLM 推理
        → [工具调用 → 结果注入 → LLM 再推理]* → 输出回答
    """

    def __init__(
        self,
        workdir: str = ".",
        system_prompt: str = SYSTEM_PROMPT,
        max_tool_rounds: int = 20,
        max_context_tokens: int = 30000,
    ):
        self.llm = LLM()
        self.tools = self._create_registry(workdir)
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds

        # ContextBuilder 负责上下文预算管理
        self.context = ContextBuilder(
            system_prompt=system_prompt,
            config=ContextConfig(max_tokens=max_context_tokens, reserve_ratio=0.1),
        )

        # 完整 messages 历史（含 tool_calls 等特殊结构）
        self.messages: List[dict] = [
            {"role": "system", "content": system_prompt}
        ]

    @staticmethod
    def _create_registry(workdir: str) -> ToolRegistry:
        """注册所有工具。"""
        registry = ToolRegistry()
        for ToolClass in ALL_TOOLS:
            # BashTool 需要 workdir 参数
            if ToolClass.__name__ == "BashTool":
                registry.register_tool(ToolClass(workdir=workdir))
            else:
                registry.register_tool(ToolClass())
        return registry

    def chat(self, user_input: str) -> str:
        """处理一轮用户输入，返回最终回答。

        流程:
        1. 用户消息加入 messages + context
        2. 如果对话过长，通过 ContextBuilder 压缩历史
        3. 调用 LLM（带 tools schema）
        4. 如果 LLM 要求调用工具 → 执行工具 → 结果注入 → 再次调用 LLM
        5. 循环直到 LLM 给出文本回答（或达到最大轮次）
        """
        self.messages.append({"role": "user", "content": user_input})
        # 记录到 context 中，用于长对话时的相关性评估
        self.context.add(user_input, source="user", relevance=0.6)

        # 压缩过长的对话历史
        self._compress_if_needed()

        tools_schema = self.tools.to_openai_schema()

        for _ in range(self.max_tool_rounds):
            response = self.llm.chat(
                self.messages,
                tools=tools_schema,
            )

            if response is None:
                return "❌ 调用 LLM 失败"

            # 检查是否有工具调用
            if response.tool_calls:
                # 将 assistant 消息（含 tool_calls）加入历史
                self.messages.append(self._message_to_dict(response))

                # 逐个执行工具
                for tool_call in response.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    # 工具结果加入历史
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                    # 工具结果也记录到 context（高相关性）
                    self.context.add(
                        f"[{tool_call.function.name}] {result[:200]}",
                        source="tool",
                        relevance=0.8,
                    )
                    print(f"  🔧 {tool_call.function.name} → {result[:100]}{'...' if len(result) > 100 else ''}")

                continue  # 继续让 LLM 处理

            # 无工具调用，LLM 给出了最终回答
            content = response.content or ""
            self.messages.append({"role": "assistant", "content": content})
            self.context.add(content, source="assistant", relevance=0.5)
            return content

        return "⚠️ 达到最大工具调用轮次，已停止。"

    def _compress_if_needed(self):
        """对话历史过长时，压缩中间部分，保留 system + 最近 N 轮。"""
        total_chars = sum(len(m.get("content", "")) for m in self.messages)
        # 粗略估算：1 字符 ≈ 1 token（中文），超过预算的 80% 时压缩
        budget = self.context.config.max_tokens
        if total_chars < budget * 0.8:
            return

        # 保留 system（第一条）和最近的消息
        keep_recent = 10  # 保留最近 10 条
        if len(self.messages) <= keep_recent + 1:
            return

        # 将被压缩的中间部分生成摘要
        middle = self.messages[1:-keep_recent]
        summary_parts = []
        for m in middle:
            role = m.get("role", "")
            content = m.get("content", "")
            if role == "user":
                summary_parts.append(f"用户: {content[:50]}")
            elif role == "assistant" and content:
                summary_parts.append(f"助手: {content[:50]}")

        summary = "[对话历史摘要]\n" + "\n".join(summary_parts[-5:])  # 只保留最近 5 条摘要

        # 重建 messages：system + 摘要 + 最近消息
        self.messages = (
            [self.messages[0]]  # system
            + [{"role": "user", "content": summary}, {"role": "assistant", "content": "好的，我已了解之前的对话内容。"}]
            + self.messages[-keep_recent:]  # 最近消息
        )

    def _execute_tool_call(self, tool_call) -> str:
        """执行单个工具调用。"""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return f"❌ 参数解析失败: {tool_call.function.arguments}"

        return self.tools.execute(name, **args)

    @staticmethod
    def _message_to_dict(message) -> dict:
        """将 OpenAI message 对象转为 dict。"""
        msg = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        return msg

    def reset(self):
        """重置对话历史和上下文。"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.context.clear()


def main():
    """交互式 REPL 入口。"""
    import sys

    workdir = sys.argv[1] if len(sys.argv) > 1 else "."
    agent = CodingAgent(workdir=workdir)

    print("🤖 Coding Agent 已启动")
    print(f"📁 工作目录: {workdir}")
    print(f"🔧 已加载 {len(agent.tools.get_tool_names())} 个工具")
    print("输入 /quit 退出, /reset 重置对话\n")

    while True:
        try:
            user_input = input("👤 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            print("👋 再见！")
            break
        if user_input == "/reset":
            agent.reset()
            print("🔄 对话已重置\n")
            continue

        print()
        answer = agent.chat(user_input)
        print(f"\n🤖 {answer}\n")


if __name__ == "__main__":
    main()
