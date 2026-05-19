from llm import LLM
from context_builder import ContextBuilder
from tools import ToolRegistry, ToolParameter


def demo_context_builder():
    """演示：上下文构建器。"""
    llm = LLM()

    builder = ContextBuilder(
        system_prompt="你是一个 Python 编程专家，擅长解释技术概念。"
    )

    builder.add(
        "Agent 是一种利用 LLM 作为推理引擎，能自主规划、使用工具并完成任务的系统。",
        source="memory",
        relevance=0.9,
    )
    builder.add(
        "上下文工程关注如何在每次模型调用前拼装最优输入上下文，提升正确性与效率。",
        source="tool",
        relevance=0.8,
    )

    user_input = "请结合 Agent 的概念，解释上下文工程为什么重要？"
    messages = builder.build(user_input)

    print("=== 构建的上下文 ===")
    for msg in messages:
        print(f"  [{msg['role']}] {msg['content']}")
    print("=== end ===\n")

    print("--- 调用 LLM ---")
    stream = llm.chat(messages, stream=True)
    if stream:
        result = LLM.stream_print(stream)
        print("\n--- 完整响应 ---")
        print(result)


def demo_tools():
    """演示：工具系统。"""
    # 创建工具注册表
    registry = ToolRegistry()

    # 用装饰器注册一个简单工具
    @registry.register(
        "get_weather",
        "获取指定城市的天气信息",
        params=[ToolParameter(name="city", type="string", description="城市名称")],
    )
    def get_weather(city: str) -> str:
        # 模拟天气查询
        weather_data = {"北京": "晴天 28°C", "上海": "多云 25°C", "深圳": "雷阵雨 30°C"}
        return weather_data.get(city, f"未找到 {city} 的天气数据")

    @registry.register(
        "calculate",
        "简单数学计算",
        params=[ToolParameter(name="expression", type="string", description="数学表达式")],
    )
    def calculate(expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"计算失败: {e}"

    # 查看已注册工具
    print("=== 已注册工具 ===")
    print(registry.get_tools_description())
    print()

    # 执行工具
    print("=== 工具调用 ===")
    print(f"  get_weather(北京) → {registry.execute('get_weather', city='北京')}")
    print(f"  calculate(2**10)  → {registry.execute('calculate', expression='2**10')}")
    print()

    # 查看 OpenAI schema
    print("=== OpenAI Function Calling Schema ===")
    import json
    schemas = registry.to_openai_schema()
    print(json.dumps(schemas, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("=" * 50)
    print("  Demo 1: 工具系统")
    print("=" * 50)
    demo_tools()

    print("\n")
    print("=" * 50)
    print("  Demo 2: 上下文构建器 + LLM 调用")
    print("=" * 50)
    demo_context_builder()

