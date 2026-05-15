# Hello Agent

基于 **Thought-Action-Observation** 循环的智能旅行助手示例，参考 [Datawhale Hello-Agents 第一章](https://hello-agents.datawhale.cc/#/./chapter1/第一章%20初识智能体)。

## 项目结构

```
ch01-hello-agent/
├── pyproject.toml  # 依赖声明
├── config.py       # 配置管理（环境变量）
├── prompt.py       # 系统提示词模板
├── tools.py        # 外部工具（天气查询、景点推荐）
├── llm.py          # LLM 客户端
├── agent.py        # 智能体核心循环
└── main.py         # 入口
```

## 快速开始

本项目使用 [uv](https://docs.astral.sh/uv/) 管理依赖。如未安装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 1. 安装依赖

```bash
uv sync
```

`uv sync` 会读取 `pyproject.toml`，自动创建 `.venv` 并安装所有依赖。

### 2. 配置环境变量

在 CNB 平台上运行时，`CNB_API_ENDPOINT`、`CNB_REPO_SLUG`、`CNB_TOKEN` 会自动注入，无需额外配置。

如需本地运行，可复制 `.env.example` 为 `.env` 并填写：

```bash
cp .env.example .env
```

### 3. 运行

```bash
uv run python main.py
```

> `uv run` 会自动使用项目的虚拟环境，无需手动 `source .venv/bin/activate`。

## 配置项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `BASE_URL` | LLM API 地址（优先级最高） | - |
| `CNB_API_ENDPOINT` | CNB 平台 API 端点 | - |
| `CNB_REPO_SLUG` | CNB 仓库标识 | - |
| `API_KEY` | API 密钥（优先级最高） | - |
| `CNB_TOKEN` | CNB 平台 Token | - |
| `MODEL_ID` | 模型 ID | `hunyuan-turbos-latest` |
| `TAVILY_API_KEY` | Tavily 搜索 API 密钥 | - |
