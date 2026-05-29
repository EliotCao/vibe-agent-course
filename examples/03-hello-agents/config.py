"""第 3 章配置：复用前两章的 BASE_URL / API_KEY / MODEL_ID 约定。

`hello-agents` 框架内部约定的环境变量是 `LLM_BASE_URL` / `LLM_API_KEY` /
`LLM_MODEL_ID`，与项目其他章节使用的 `BASE_URL` / `API_KEY` / `MODEL_ID`
不一致。为避免读者重新维护一份 `.env`，这里把项目惯用变量解析出来后，
显式作为参数传给 `HelloAgentsLLM(...)`，框架就不会再去读它自己的环境变量。
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_base_url() -> str:
    """获取 LLM API 的 Base URL。

    优先读取 `BASE_URL`；若在 CNB 平台运行，则从
    `CNB_API_ENDPOINT` + `CNB_REPO_SLUG` 拼接。
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
    """获取 API Key。优先 `API_KEY`，否则 `CNB_TOKEN`。"""
    api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN")
    if not api_key:
        raise EnvironmentError("请设置 API_KEY 或 CNB_TOKEN 环境变量")
    return api_key


def get_model_id() -> str:
    """获取模型 ID，默认 `glm-5.0`。"""
    return os.environ.get("MODEL_ID", "glm-5.0")


def get_timeout() -> int:
    """获取 LLM 请求超时时间（秒），默认 60。"""
    return int(os.environ.get("LLM_TIMEOUT", "60"))
