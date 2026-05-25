# Hello ReAct

基于 **ReAct（Thought-Action-Observation）** 循环的智能旅行助手示例，参考 [Datawhale Hello-Agents 第一章](https://hello-agents.datawhale.cc/#/./chapter1/第一章%20初识智能体)。

## 项目结构

```
ch01-hello-react/
├── pyproject.toml  # 依赖声明
├── config.py       # 配置管理（环境变量）
├── prompt.py       # 系统提示词模板
├── tools.py        # 外部工具（天气查询、景点推荐）
├── llm.py          # LLM 客户端
├── agent.py        # 智能体核心循环
└── main.py         # 入口
```

## 快速开始

本课程整体使用 [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) 组织，所有章节共享仓库根目录的 `.venv`。

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
| `TAVILY_API_KEY` | Tavily 搜索 API 密钥 | - |
