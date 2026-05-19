"""ch04-my-agent 入口。

各模块的独立测试请运行:
  python test_llm.py       # 测试 LLM 客户端
  python test_tools.py     # 测试工具系统
  python test_context.py   # 测试上下文构建器
  python test_agent.py     # 测试 Agent 范式
"""

from llm import LLM
from context_builder import ContextBuilder
from tools import ToolRegistry, ToolParameter
from agent import SimpleAgent, ReActAgent


def main():
    """综合演示：SimpleAgent + 工具 + 上下文。"""
    llm = LLM()
    registry = ToolRegistry()

    @registry.register(
        "get_weather",
        "获取指定城市的天气信息",
        params=[ToolParameter(name="city", type="string", description="城市名称")],
    )
    def get_weather(city: str) -> str:
        weather_data = {"北京": "晴天 28°C", "上海": "多云 25°C", "深圳": "雷阵雨 30°C"}
        return weather_data.get(city, f"未找到 {city} 的天气数据")

    agent = SimpleAgent(
        name="小助手",
        llm=llm,
        system_prompt="你是一个天气助手，可以帮用户查询天气。",
        tools=registry,
    )

    answer = agent.run("北京今天天气怎么样？")
    print(f"\n最终回答: {answer}")


if __name__ == "__main__":
    main()
