"""Demo 共用：从环境变量读取 LLM 配置。

跟 第1章-第5章 完全一致——确保整合后行为不变。
"""

from __future__ import annotations

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_base_url() -> str:
    base_url = os.environ.get("BASE_URL")
    if base_url:
        return base_url
    endpoint = os.environ.get("CNB_API_ENDPOINT", "")
    repo_slug = os.environ.get("CNB_REPO_SLUG", "")
    if endpoint and repo_slug:
        return f"{endpoint}/{repo_slug}/-/ai/"
    raise EnvironmentError(
        "请设置 BASE_URL，或同时设置 CNB_API_ENDPOINT 和 CNB_REPO_SLUG 环境变量"
    )


def get_api_key() -> str:
    api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN")
    if not api_key:
        raise EnvironmentError("请设置 API_KEY 或 CNB_TOKEN 环境变量")
    return api_key


def get_model_id() -> str:
    return os.environ.get("MODEL_ID", "hunyuan-turbos-latest")


def make_client():
    from openai import OpenAI

    return OpenAI(base_url=get_base_url(), api_key=get_api_key())
