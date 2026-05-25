"""智能体核心：Thought-Action-Observation 循环。"""

import re

from llm import OpenAICompatibleClient
from prompt import AGENT_SYSTEM_PROMPT
from tools import AVAILABLE_TOOLS

MAX_LOOPS = 5


def run_agent(llm: OpenAICompatibleClient, user_prompt: str) -> str:
    """运行智能体主循环，返回最终答案。"""
    prompt_history = [f"用户请求: {user_prompt}"]
    print(f"用户输入: {user_prompt}\n" + "=" * 40)

    for i in range(MAX_LOOPS):
        print(f"\n--- 循环 {i + 1} ---\n")

        # 1. 构建 Prompt
        full_prompt = "\n".join(prompt_history)

        # 2. 调用 LLM 进行思考
        llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)

        # 截断多余的 Thought-Action 对，只保留第一对
        match = re.search(
            r"(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)",
            llm_output,
            re.DOTALL,
        )
        if match:
            truncated = match.group(1).strip()
            if truncated != llm_output.strip():
                llm_output = truncated
                print("已截断多余的 Thought-Action 对")

        print(f"模型输出:\n{llm_output}\n")
        prompt_history.append(llm_output)

        # 3. 解析并执行行动
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            observation = (
                "错误: 未能解析到 Action 字段。"
                "请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
            )
            observation_str = f"Observation: {observation}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue

        action_str = action_match.group(1).strip()

        # 检查是否结束
        if action_str.startswith("Finish"):
            finish_match = re.match(r"Finish\[(.*)\]", action_str, re.DOTALL)
            if finish_match:
                final_answer = finish_match.group(1)
                print(f"任务完成，最终答案: {final_answer}")
                return final_answer

        # 解析工具调用
        tool_match = re.search(r"(\w+)\(", action_str)
        args_match = re.search(r"\((.*)\)", action_str)
        if not tool_match or not args_match:
            observation = f"错误: 无法解析工具调用 '{action_str}'"
            observation_str = f"Observation: {observation}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue

        tool_name = tool_match.group(1)
        args_str = args_match.group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        if tool_name in AVAILABLE_TOOLS:
            observation = AVAILABLE_TOOLS[tool_name](**kwargs)
        else:
            observation = f"错误:未定义的工具 '{tool_name}'"

        # 4. 记录观察结果
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)

    return "错误: 达到最大循环次数，智能体未能完成任务。"
