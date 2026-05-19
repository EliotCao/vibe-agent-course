"""
ch04-my-agent 入口模块

演示如何组合各功能模块构建完整的 Agent 应用。
运行: python main.py
"""

from llm import LLM
from context_builder import ContextBuilder
from tools import ToolRegistry, ToolParameter
from agent import SimpleAgent, ReActAgent


def main():
    """演示 Agent 完整工作流程：初始化 -> 注册工具 -> 执行任务"""

    # 初始化 LLM 客户端（从环境变量读取配置）
    llm = LLM()

    # 创建工具注册表
    tools = ToolRegistry()

    # 注册天气查询工具
    @tools.register(
        "get_weather",
        "获取指定城市的天气信息",
        params=[ToolParameter(name="city", type="string", description="城市名称")],
    )
    def get_weather(city: str) -> str:
        """查询城市天气（当前使用模拟数据）"""
        weather_data = {
            "北京": "晴天 28°C",
            "上海": "多云 25°C",
            "深圳": "雷阵雨 30°C"
        }
        return weather_data.get(city, f"未找到 {city} 的天气数据")

    # 创建 Agent 实例
    agent = SimpleAgent(
        name="小助手",
        llm=llm,
        system_prompt="你是一个天气助手，可以帮用户查询天气。",
        tools=tools,
    )

    # 执行任务
    answer = agent.run("北京今天天气怎么样？")
    print(f"\n最终回答: {answer}")


if __name__ == "__main__":
    main()
