# Hello LLM

第 2 章：用最少的代码封装一个**兼容 OpenAI 接口**的 LLM 客户端 `HelloAgentsLLM`，默认使用**流式响应**，便于直观感受大模型逐 token 输出的过程。

## 项目结构

```
02-hello-llm/
├── pyproject.toml   # 依赖声明
├── .env.example     # 环境变量示例
├── config.py        # 配置管理（环境变量）
└── main.py          # HelloAgentsLLM 客户端 + 使用示例
```

## 快速开始

本项目整体使用 [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) 组织，所有章节共享仓库根目录的 `.venv`。

### 1. 安装依赖（在仓库根目录执行一次）

```bash
cd ..                     # 回到仓库根目录
uv sync --all-packages    # 安装所有章节的依赖到共享 .venv
```

### 2. 配置环境变量

在 CNB 平台上运行时，`CNB_API_ENDPOINT`、`CNB_REPO_SLUG`、`CNB_TOKEN` 会自动注入，无需额外配置。

如需本地运行，可复制 `.env.example` 为 `.env` 并填写：

```bash
cp .env.example .env
```

### 3. 运行

CNB 云端 IDE 的终端已预激活根 `.venv`，直接：

```bash
python main.py
```

运行后将看到模型以流式方式逐 token 输出快速排序的实现。

> 在本地或 CI 环境不确定是否激活时，推荐用 `uv run python main.py`，
> 它会自动使用根 `.venv` 并在依赖缺失时先 `uv sync`。

## 配置项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `BASE_URL` | LLM API 地址（优先级最高） | - |
| `CNB_API_ENDPOINT` | CNB 平台 API 端点 | - |
| `CNB_REPO_SLUG` | CNB 仓库标识 | - |
| `API_KEY` | API 密钥（优先级最高） | - |
| `CNB_TOKEN` | CNB 平台 Token | - |
| `MODEL_ID` | 模型 ID | `hunyuan-turbos-latest` |
| `LLM_TIMEOUT` | 请求超时（秒） | `60` |

## 核心代码一览

```python
from main import HelloAgentsLLM

llm = HelloAgentsLLM()
text = llm.think([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "用一句话解释什么是大语言模型"},
])
print(text)
```

`HelloAgentsLLM.think()` 接收标准的 `messages` 列表，内部以 `stream=True` 调用 Chat Completions 接口，边输出边收集 token，最终返回完整文本。
