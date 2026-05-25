"""Demo 共用：从环境变量读取 LLM 配置。

- 优先使用显式的 `BASE_URL` / `API_KEY`；
- 若在 CNB 平台运行（未显式配置），则自动从 `CNB_API_ENDPOINT` + `CNB_REPO_SLUG`
  拼接 Base URL，并使用 `CNB_TOKEN` 作为 API Key。
- `MODEL_ID` 未设置时默认 `hunyuan-turbos-latest`。
"""

from __future__ import annotations

import os

try:
    # 可选依赖：本地有 .env 时方便加载；没装也不影响 CNB 环境
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_base_url() -> str:
    """获取 LLM API 的 Base URL。

    优先读取 `BASE_URL`；未设置时从 `CNB_API_ENDPOINT` + `CNB_REPO_SLUG` 拼接。
    """
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
    """获取 API Key。优先读取 `API_KEY`，否则读取 `CNB_TOKEN`。"""
    api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN")
    if not api_key:
        raise EnvironmentError("请设置 API_KEY 或 CNB_TOKEN 环境变量")
    return api_key


def get_model_id() -> str:
    """获取模型 ID，默认 `hunyuan-turbos-latest`。"""
    return os.environ.get("MODEL_ID", "hunyuan-turbos-latest")


def make_client():
    """创建一个 OpenAI 兼容客户端（按上述规则解析配置）。"""
    from openai import OpenAI

    return OpenAI(base_url=get_base_url(), api_key=get_api_key())
