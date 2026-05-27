"""
04-my-agent 入口模块

演示如何组合各功能模块构建完整的 Agent 应用。
运行: python main.py
"""

from llm import LLM
from context import ContextBuilder
from tools import ToolRegistry, ToolParameter
from agent import SimpleAgent, ReActAgent


def main():
    """演示 Agent 工作流程"""

    llm = LLM()
    tools = ToolRegistry()

    @tools.register(
        "get_weather",
        "获取指定城市的天气信息",
        params=[ToolParameter(name="city", type="string", description="城市名称")],
    )
    def get_weather(city: str) -> str:
        weather_data = {
            "北京": "晴天 28°C",
            "上海": "多云 25°C",
            "深圳": "雷阵雨 30°C"
        }
        return weather_data.get(city, f"未找到 {city} 的天气数据")

    # --- 演示 1: 流式输出（直接使用 LLM）---
    print("=== 流式输出演示 ===")
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手，请简洁回答。"},
        {"role": "user", "content": "用一句话解释什么是 Agent"},
    ]
    stream = llm.chat(messages, stream=True)
    if stream:
        LLM.stream_print(stream)

    # --- 演示 2: SimpleAgent + 工具调用 ---
    print("\n=== SimpleAgent 演示 ===")
    agent = SimpleAgent(
        name="小助手",
        llm=llm,
        system_prompt="你是一个天气助手，可以帮用户查询天气。",
        tools=tools,
    )

    answer = agent.run("北京今天天气怎么样？")
    print(f"\n最终回答: {answer}")


if __name__ == "__main__":
    main()
