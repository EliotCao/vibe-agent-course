"""智能体可调用的外部工具。"""

import requests

from config import get_api_key, get_base_url, MODEL_ID
from llm import OpenAICompatibleClient


def get_weather(city: str) -> str:
    """通过调用 wttr.in API 查询真实的天气信息。"""
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        current_condition = data["current_condition"][0]
        weather_desc = current_condition["weatherDesc"][0]["value"]
        temp_c = current_condition["temp_C"]

        return f"{city}当前天气:{weather_desc}，气温{temp_c}摄氏度"
    except requests.exceptions.RequestException as e:
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"


def get_attraction(city: str, weather: str) -> str:
    """根据城市和天气，调用 LLM 推荐合适的旅游景点。"""
    try:
        llm = OpenAICompatibleClient(
            model=MODEL_ID,
            api_key=get_api_key(),
            base_url=get_base_url(),
        )
        prompt = (
            f"请推荐3个{city}在{weather}天气下最适合游览的旅游景点。\n"
            f"要求：每个景点给出名称、推荐理由（结合天气），以及一句实用小贴士。\n"
            f"请直接给出推荐内容，不要多余的开场白。"
        )
        return llm.generate(prompt, system_prompt="你是一个专业的旅行顾问。")
    except Exception as e:
        return f"错误:获取景点推荐时出现问题 - {e}"


# 工具注册表
AVAILABLE_TOOLS: dict[str, callable] = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}
