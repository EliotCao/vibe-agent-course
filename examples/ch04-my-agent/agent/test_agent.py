"""测试 Agent 范式（SimpleAgent + ReActAgent）。"""

from llm import LLM
from tools import ToolRegistry, ToolParameter
from agent import SimpleAgent, ReActAgent


def test_simple_agent():
    """SimpleAgent：对话 + 工具调用。"""
    llm = LLM()
    tools = ToolRegistry()

    @tools.register(
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
        tools=tools,
    )

    print("--- SimpleAgent 运行 ---")
    answer = agent.run("北京今天天气怎么样？")
    print(f"\n最终回答: {answer}")


def test_react_agent():
    """ReActAgent：推理-行动循环。"""
    llm = LLM()
    tools = ToolRegistry()

    @tools.register(
        "calculate",
        "数学计算，参数为数学表达式",
        params=[ToolParameter(name="input", type="string", description="数学表达式")],
    )
    def calculate(input: str) -> str:
        try:
            result = eval(input, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"计算失败: {e}"

    agent = ReActAgent(
        name="推理助手",
        llm=llm,
        tools=tools,
        max_steps=5,
    )

    print("--- ReActAgent 运行 ---")
    answer = agent.run("计算 (15 + 27) * 3 的结果是多少？")
    print(f"\n最终回答: {answer}")


if __name__ == "__main__":
    print("=" * 50)
    print("  Test 1: SimpleAgent")
    print("=" * 50)
    test_simple_agent()

    print("\n")
    print("=" * 50)
    print("  Test 2: ReActAgent")
    print("=" * 50)
    test_react_agent()
