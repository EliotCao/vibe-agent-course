"""测试工具系统。"""

import json

from tools import ToolRegistry, ToolParameter


def main():
    tools = ToolRegistry()

    @tools.register(
        "get_weather",
        "获取指定城市的天气信息",
        params=[ToolParameter(name="city", type="string", description="城市名称")],
    )
    def get_weather(city: str) -> str:
        weather_data = {"北京": "晴天 28°C", "上海": "多云 25°C", "深圳": "雷阵雨 30°C"}
        return weather_data.get(city, f"未找到 {city} 的天气数据")

    @tools.register(
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
    print(tools.get_tools_description())
    print()

    # 执行工具
    print("=== 工具调用 ===")
    print(f"  get_weather(北京) → {tools.execute('get_weather', city='北京')}")
    print(f"  get_weather(广州) → {tools.execute('get_weather', city='广州')}")
    print(f"  calculate(2**10)  → {tools.execute('calculate', expression='2**10')}")
    print(f"  calculate(3.14*2) → {tools.execute('calculate', expression='3.14*2')}")
    print()

    # OpenAI schema
    print("=== OpenAI Function Calling Schema ===")
    print(json.dumps(tools.to_openai_schema(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
