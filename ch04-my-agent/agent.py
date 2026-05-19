"""极简 Agent 范式实现。

提供两种经典 Agent 范式：
- SimpleAgent: 单轮对话 + 可选工具调用
- ReActAgent: Thought → Action → Observation 循环

所有 Agent 通过 ContextBuilder 统一构建传递给 LLM 的 messages。
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from llm import LLM
from tools import ToolRegistry
from context_builder import ContextBuilder


class Agent(ABC):
    """Agent 抽象基类：定义统一接口。"""

    def __init__(
        self,
        name: str,
        llm: LLM,
        system_prompt: str = "你是一个有用的 AI 助手。",
        tools: Optional[ToolRegistry] = None,
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools
        self.context = ContextBuilder(system_prompt=self._enhanced_prompt())

    @abstractmethod
    def run(self, user_input: str) -> str:
        """执行 Agent，返回最终回答。"""
        pass

    def clear_history(self) -> None:
        """清空对话历史。"""
        self.context.clear()

    def _enhanced_prompt(self) -> str:
        """构建增强的 system prompt（含工具描述）。"""
        prompt = self.system_prompt
        if self.tools and self.tools.get_tool_names():
            prompt += f"\n\n## 可用工具\n{self.tools.get_tools_description()}\n"
            prompt += "\n## 工具调用格式\n"
            prompt += "需要使用工具时，输出: [TOOL_CALL:工具名:参数名=值]\n"
            prompt += "例如: [TOOL_CALL:get_weather:city=北京]\n"
            prompt += "可以不使用工具直接回答。\n"
        return prompt


class SimpleAgent(Agent):
    """简单对话 Agent：支持可选工具调用。

    工作流程：
      1. 通过 ContextBuilder 构建 messages
      2. 调用 LLM
      3. 如果响应中包含 [TOOL_CALL:name:params]，执行工具并将结果注入
      4. 再次调用 LLM 生成最终回答
    """

    def __init__(
        self,
        name: str,
        llm: LLM,
        system_prompt: str = "你是一个有用的 AI 助手。",
        tools: Optional[ToolRegistry] = None,
        max_iterations: int = 3,
    ):
        super().__init__(name, llm, system_prompt, tools)
        self.max_iterations = max_iterations

    def run(self, user_input: str) -> str:
        # 通过 ContextBuilder 构建 messages
        messages = self.context.build(user_input)

        for _ in range(self.max_iterations):
            response = self.llm.chat(messages, stream=False)
            if response is None:
                return "调用 LLM 失败"

            # 解析工具调用
            tool_calls = self._parse_tool_calls(response)
            if not tool_calls:
                # 无工具调用，即为最终回答
                # 将本轮对话记录到 context 中，供下次调用使用
                self.context.add(user_input, source="user", relevance=0.5)
                self.context.add(response, source="assistant", relevance=0.5)
                return response

            # 执行工具，将结果注入上下文
            results = []
            for call in tool_calls:
                result = self.tools.execute(call["name"], **call["params"])
                results.append(f"[{call['name']}] {result}")

            # 工具结果以高相关性注入 context
            tool_output = "\n".join(results)
            self.context.add(tool_output, source="tool", relevance=1.0)

            # 重新构建 messages（含工具结果），再次调用 LLM
            messages = self.context.build(
                f"工具执行结果:\n{tool_output}\n\n请基于结果回答用户的问题: {user_input}"
            )

        # 达到最大迭代次数，返回最后一次响应
        return response

    @staticmethod
    def _parse_tool_calls(text: str) -> List[Dict]:
        """解析 [TOOL_CALL:name:params] 标记。"""
        pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)
        calls = []
        for name, params_str in matches:
            params = {}
            for pair in params_str.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k.strip()] = v.strip()
                else:
                    params["input"] = pair.strip()
            calls.append({"name": name.strip(), "params": params})
        return calls


class ReActAgent(Agent):
    """ReAct Agent：Thought → Action → Observation 循环。

    工作流程：
      1. 通过 ContextBuilder 构建 prompt（含工具描述 + 问题 + 历史）
      2. LLM 输出 Thought + Action
      3. 如果 Action = Finish[答案]，返回答案
      4. 否则执行工具，获取 Observation，注入 context，回到步骤 1
    """

    PROMPT_TEMPLATE = """你是一个具备推理和行动能力的 AI 助手。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式回应，每次只执行一个步骤:

Thought: 分析当前问题，思考下一步行动
Action: 选择以下之一:
  - `工具名[参数]` — 调用工具
  - `Finish[最终答案]` — 给出最终答案

## 规则
1. 每次回应必须包含 Thought 和 Action
2. 确信有足够信息时才使用 Finish
3. 工具格式: 工具名[参数]

## 问题
{question}

## 执行历史
{history}

现在开始:"""

    def __init__(
        self,
        name: str,
        llm: LLM,
        tools: ToolRegistry,
        system_prompt: str = "",
        max_steps: int = 5,
    ):
        super().__init__(name, llm, system_prompt, tools)
        self.max_steps = max_steps

    def run(self, user_input: str) -> str:
        history_lines: List[str] = []

        for step in range(1, self.max_steps + 1):
            prompt = self.PROMPT_TEMPLATE.format(
                tools=self.tools.get_tools_description(),
                question=user_input,
                history="\n".join(history_lines) if history_lines else "（无）",
            )

            # 用 ContextBuilder 构建（ReAct 每步重建上下文）
            messages = self.context.build(prompt)
            response = self.llm.chat(messages, stream=False)
            if response is None:
                return "调用 LLM 失败"

            # 解析 Thought 和 Action
            thought, action = self._parse_response(response)

            print(f"  [Step {step}]")
            if thought:
                print(f"  💭 Thought: {thought}")
            if action:
                print(f"  ⚡ Action: {action}")

            # 检查是否结束
            if action and action.lower().startswith("finish"):
                answer = self._extract_finish(action)
                self.context.add(user_input, source="user", relevance=0.5)
                self.context.add(answer, source="assistant", relevance=0.5)
                return answer

            # 执行工具
            if action:
                tool_name, tool_input = self._parse_action(action)
                observation = self.tools.execute(tool_name, **{"input": tool_input})
                print(f"  👁 Observation: {observation}")

                # 将每步结果注入 context，供后续步骤参考
                self.context.add(
                    f"Step {step}: {thought} → {action} → {observation}",
                    source="tool",
                    relevance=0.8,
                )
                history_lines.append(f"Thought: {thought}")
                history_lines.append(f"Action: {action}")
                history_lines.append(f"Observation: {observation}")

        return "抱歉，我无法在限定步数内完成这个任务。"

    @staticmethod
    def _parse_response(text: str):
        """解析 Thought 和 Action。"""
        thought = None
        action = None

        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|$)', text, re.DOTALL)
        if thought_match:
            thought = thought_match.group(1).strip()

        action_match = re.search(r'Action:\s*(.+?)$', text, re.MULTILINE)
        if action_match:
            action = action_match.group(1).strip().strip("`")

        return thought, action

    @staticmethod
    def _parse_action(action: str):
        """解析 tool_name[input] 格式。"""
        match = re.match(r'(\w+)\[(.+)\]', action)
        if match:
            return match.group(1), match.group(2)
        return action, ""

    @staticmethod
    def _extract_finish(action: str) -> str:
        """提取 Finish[答案] 中的答案。"""
        match = re.match(r'[Ff]inish\[(.+)\]', action)
        if match:
            return match.group(1)
        return action.replace("Finish", "").strip("[]")
