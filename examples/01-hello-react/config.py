"""应用配置，从环境变量加载。"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_base_url() -> str:
    """获取 LLM API 的 Base URL。

    优先读取 BASE_URL 环境变量；
    若未设置，则从 CNB_API_ENDPOINT 和 CNB_REPO_SLUG 拼接。
    """
    base_url = os.environ.get("BASE_URL")
    if base_url:
        return base_url

    endpoint = os.environ.get("CNB_API_ENDPOINT", "")
    repo_slug = os.environ.get("CNB_REPO_SLUG", "")
    if endpoint and repo_slug:
        return f"{endpoint}/{repo_slug}/-/ai-ide/v2"

    raise EnvironmentError(
        "请设置 BASE_URL，或同时设置 CNB_API_ENDPOINT 和 CNB_REPO_SLUG 环境变量"
    )


def get_api_key() -> str:
    """获取 API Key。优先读取 API_KEY，否则读取 CNB_TOKEN。"""
    api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN")
    if not api_key:
        raise EnvironmentError("请设置 API_KEY 或 CNB_TOKEN 环境变量")
    return api_key


MODEL_ID: str = os.environ.get("MODEL_ID", "glm-5.0")
