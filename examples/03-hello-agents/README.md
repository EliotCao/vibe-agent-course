# Hello Agents 框架快速上手

第 1 章我们**手写**了一个 ReAct 循环，第 2 章手写了 LLM 客户端。本章换个角度——
直接用社区开源的 [`hello-agents`](https://github.com/jjyaoao/HelloAgents) 框架（v0.1.1），
看看同样的能力**用框架来写**是什么样子，对照之下能更直观地理解 Agent 框架到底封装了什么。

## 你将看到什么

| Demo | 用到的类 | 对应前两章的概念 |
|------|---------|----------------|
| 1. 最小对话 agent | `SimpleAgent` + `HelloAgentsLLM` | ch02 手写的 `HelloAgentsLLM` |
| 2. 带工具的 ReAct agent | `ReActAgent` + `ToolRegistry` + `CalculatorTool` | ch01 手写的 Thought-Action-Observation 循环 |

## 项目结构

```
03-hello-agents/
├── pyproject.toml   # 依赖：hello-agents==0.1.1
├── config.py        # 复用 ch01/ch02 的环境变量约定
├── .env.example     # 环境变量模板
└── main.py          # 两个 demo 的入口
```

## 快速开始

### 1. 安装依赖（在仓库根目录执行一次）

```bash
cd ..                     # 回到仓库根目录
uv sync --all-packages    # 把 hello-agents 装入共享 .venv
```

### 2. 配置环境变量

在 CNB 平台上，`CNB_API_ENDPOINT` / `CNB_REPO_SLUG` / `CNB_TOKEN` 会自动注入。
本地运行时复制模板填写：

```bash
cp .env.example .env
```

### 3. 运行

```bash
python main.py
```

或者跨环境更稳：

```bash
uv run python main.py
```

## 为什么要再造一个 `config.py`？

`hello-agents` 框架自身约定的环境变量是 `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL_ID`，
与前两章用的 `BASE_URL` / `API_KEY` / `MODEL_ID` 不一致。本章 `config.py` 仍按
项目约定解析变量，再**显式**作为参数传给 `HelloAgentsLLM(...)`，这样读者不用再
维护第二份 `.env`。

```python
HelloAgentsLLM(
    model=get_model_id(),
    api_key=get_api_key(),
    base_url=get_base_url(),
    timeout=get_timeout(),
)
```

## 与前两章的对照

- **ch01** 里我们自己写了 `agent.py` ~100 行，手工解析模型输出里的 `Action: ...` 字符串、
  执行工具、把 Observation 拼回 messages。本章 `ReActAgent` 把这一整套都封装好了，
  你只负责"注册工具 + 提问"。
- **ch02** 里我们自己写了 `HelloAgentsLLM`，用 `OpenAI(...)` 做流式调用。本章直接用框架
  同名的 `HelloAgentsLLM`——接口几乎一样，但额外支持多 provider 自动检测、
  `Message` 抽象、`temperature` / `max_tokens` 等参数。

> 框架并不"魔法"，它只是把 ch01/ch02 我们已经手写过的代码做了产品化封装。
> **理解 ch01/ch02 的内部机制后再看 ch03，就能很快读懂任何 Agent 框架的源码。**

## 配置项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `BASE_URL` | LLM API 地址（优先级最高） | - |
| `CNB_API_ENDPOINT` + `CNB_REPO_SLUG` | CNB 平台自动拼接的 Base URL | - |
| `API_KEY` / `CNB_TOKEN` | API 密钥 | - |
| `MODEL_ID` | 模型 ID | `hunyuan-turbos-latest` |
| `LLM_TIMEOUT` | 请求超时（秒） | `60` |
