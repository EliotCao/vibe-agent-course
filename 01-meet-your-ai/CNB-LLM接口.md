# CNB LLM 大模型接口的使用方法

CNB 平台内置了 **OpenAI 兼容**的大模型接口，可以在仓库的云原生环境里**零密钥、开箱即用**地调用大模型。本章介绍接口规范、环境变量约定，以及在 Python、curl 中的调用方法。

---

## 4.1 接口规范（核心）

CNB 的大模型接口遵循 **OpenAI 兼容协议**，关键约定如下：

| 项目 | 取值 |
| --- | --- |
| **Base URL** | `{CNB_API_ENDPOINT}/{CNB_REPO_SLUG}/-/ai-ide/v2` |
| `CNB_API_ENDPOINT` | API 端点，默认 `https://api.cnb.cool` |
| `CNB_REPO_SLUG` | 仓库标识，如 `your-org/your-repo` |
| **API Key** | CNB 访问令牌（`CNB_TOKEN`） |
| **模型（model）** | 例如 `deepseek-v4.1-flash` |
| **调用方式** | OpenAI SDK / 任意 OpenAI 兼容客户端 |
| **流式要求** | ⚠️ **必须 `stream=True`**——该平台只支持流式请求 |

拼出来的完整 Base URL 形如：

```
https://api.cnb.cool/your-org/your-repo/-/ai-ide/v2
```

> 💡 **最大亮点**：在 **CNB 云原生环境**中，`CNB_API_ENDPOINT`、`CNB_REPO_SLUG`、`CNB_TOKEN` 这三个环境变量会被**自动注入**，代码里无需任何硬编码密钥即可直接调用大模型。

### 可用模型

调用时 `model` 字段可选用以下模型 ID：

| 模型 | 模型 ID（`model` 字段） | credits 倍率 |
| --- | --- | --- |
| Hy4（免费档） | `hy4free` | ×0.00 |
| Hy4（标准档） | `hy4std` | ×0.29 |
| DeepSeek-V4.1-Flash | `deepseek-v4.1-flash` | ×0.11 |
| GLM-5.3-Flash | `glm-5.3-flash` | ×0.08 |
| Space-Bunny | `space-bunny` | ×0.08 |
| MiniMax-M3.1-Flash | `minimax-m3.1-flash` | ×0.08 |
| Step-5-Preview | `step-5-preview` | ×0.33 |
| Xiaomi MiMo-V2.6-Pro | `mimo-v2.6-pro` | ×0.13 |

> ℹ️ 推荐入门用 `deepseek-v4.1-flash`：价格便宜、能力足够跑通全部 Demo；`hy4free` 完全免费，适合先验证链路是否打通。可用模型与 credits 倍率会随平台版本变动，请以 CNB 平台当前实际支持的列表为准。

---

## 4.2 环境变量约定

下面给出一份 `.env.example` 模板：

```bash
# CNB 平台环境（云端自动注入，无需手动配置）
# CNB_API_ENDPOINT=https://api.cnb.cool
# CNB_REPO_SLUG=your-org/your-repo
# CNB_TOKEN=auto_injected

# 本地开发环境配置（本地跑时才需要手动填）
BASE_URL=https://api.cnb.cool/your-org/your-repo/-/ai-ide/v2
API_KEY=your_cnb_access_token
MODEL_ID=deepseek-v4.1-flash
```

约定优先级：

- **云端运行**：直接用自动注入的 `CNB_API_ENDPOINT` + `CNB_REPO_SLUG` + `CNB_TOKEN` 拼 Base URL。
- **本地运行**：手动设置 `BASE_URL`、`API_KEY`（填你的 CNB 访问令牌）、`MODEL_ID`。

> 🔐 安全红线：本地的 `API_KEY` 是你的 CNB 访问令牌，等同账号凭证。**只放在 `.env` 且 `.env` 必须加入 `.gitignore`**，仓库里只提交 `.env.example` 模板，绝不提交真实令牌。访问令牌在 <https://cnb.cool/profile/token/create> 创建。

---

## 4.3 用 Python SDK 调用

下面是一份可直接复用的封装范本，核心逻辑拆解如下：

### 第 1 步：构造客户端（自动适配云端/本地）

```python
import os
from openai import OpenAI

def get_client() -> OpenAI:
    # 本地优先用 .env 的 BASE_URL
    base_url = os.environ.get("BASE_URL")
    if not base_url:
        # 云端：用自动注入的环境变量拼接
        endpoint = os.environ.get("CNB_API_ENDPOINT", "https://api.cnb.cool")
        repo_slug = os.environ.get("CNB_REPO_SLUG", "")
        base_url = f"{endpoint}/{repo_slug}/-/ai-ide/v2"

    api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN", "sk-placeholder")
    return OpenAI(base_url=base_url, api_key=api_key, timeout=60.0)

def get_model() -> str:
    return os.environ.get("MODEL_ID", "deepseek-v4.1-flash")
```

### 第 2 步：发起**流式**请求并收集结果

由于平台**只支持流式**，需要把所有 chunk 拼接成完整内容：

```python
def call_llm(system_prompt: str, user_prompt: str) -> str:
    client, model = get_client(), get_model()

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.8,
        max_tokens=1024,
        stream=True,          # ⚠️ 必须为 True
    )

    parts = []
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            parts.append(chunk.choices[0].delta.content)
    return "".join(parts).strip()
```

依赖（`requirements.txt`）：

```
openai>=1.60.0     # httpx>=0.28 移除了 proxies 参数，需要较新版本的 openai
python-dotenv
```

---

## 4.4 用 curl 调用（OpenAI 兼容）

```bash
curl -X POST "${CNB_API_ENDPOINT}/${CNB_REPO_SLUG}/-/ai-ide/v2/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${CNB_TOKEN}" \
  -d '{
    "model": "deepseek-v4.1-flash",
    "stream": true,
    "messages": [
      {"role": "system", "content": "你是一个修仙游戏的旁白"},
      {"role": "user",   "content": "为第一轮生成一段修仙境遇和两个选择，用 JSON 输出"}
    ]
  }'
```

> 注意 `"stream": true`。返回为 SSE 流（`data: {...}` 多行），需逐条解析拼接 `delta.content`。

---

## 本章小结

- CNB LLM 接口 = **OpenAI 兼容** + Base URL `…/{repo_slug}/-/ai-ide/v2`。
- 云端三件套（`CNB_API_ENDPOINT` / `CNB_REPO_SLUG` / `CNB_TOKEN`）**自动注入**，无需硬编码密钥；本地开发则通过 `.env` 配置 `BASE_URL` / `API_KEY` / `MODEL_ID`。
- 该平台**只支持流式**，调用时**必须 `stream=True`**，并把各 chunk 的 `delta.content` 拼接成完整内容。
- 用 OpenAI SDK 或任意 OpenAI 兼容客户端（如 curl）均可调用，迁移成本极低。

下一篇：[完整项目演示 →](完整项目演示.md)
