# LLM 类设计文档

## 概述

`LLM` 是一个独立的大语言模型客户端，兼容 OpenAI API 接口，不依赖任何外部 Agent 框架。设计目标是：**极简、自包含、调用方可控**。

## 设计原则

1. **零框架依赖** —— 仅依赖 `openai` SDK 和 `python-dotenv`
2. **配置自包含** —— 环境变量读取内聚在类内部
3. **输出控制权归调用方** —— 流式模式返回生成器，不在内部打印
4. **兼容性优先** —— 任何兼容 OpenAI 接口的服务均可接入

## 类结构

```
LLM
├── __init__(model, api_key, base_url, timeout)  # 初始化
├── chat(messages, temperature, stream)           # 核心调用方法
├── stream_print(stream)                          # 便捷方法：消费流并打印
├── _iter_stream(response)                        # 内部：流式响应转生成器
├── _get_base_url()                               # 内部：获取 API 地址
├── _get_api_key()                                # 内部：获取密钥
├── _get_model_id()                               # 内部：获取模型 ID
└── _get_timeout()                                # 内部：获取超时时间
```

## 核心方法

### `chat(messages, temperature=0, stream=True)`

唯一的对外调用入口，两种返回模式：

| 参数 | 返回类型 | 说明 |
|------|----------|------|
| `stream=False` | `str \| None` | 阻塞等待，返回完整响应文本 |
| `stream=True` | `Generator[str] \| None` | 返回生成器，调用方逐块消费 |

调用示例：

```python
llm = LLM()

# 非流式
result = llm.chat(messages, stream=False)
print(result)

# 流式
stream = llm.chat(messages, stream=True)
for chunk in stream:
    print(chunk, end="", flush=True)

# 流式（便捷方式）
stream = llm.chat(messages, stream=True)
result = LLM.stream_print(stream)
```

### `stream_print(stream)` （静态方法）

便捷工具方法，消费生成器并逐块打印到终端，最终返回拼接后的完整文本。

## 配置管理

所有配置通过环境变量加载（支持 `.env` 文件），优先级：

```
构造函数参数 > 环境变量 > 默认值
```

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `BASE_URL` | API 地址 | 无（必填） |
| `API_KEY` | API 密钥 | 无（必填） |
| `CNB_API_ENDPOINT` | CNB 平台端点（备选） | - |
| `CNB_REPO_SLUG` | CNB 仓库标识（备选） | - |
| `CNB_TOKEN` | CNB 平台 Token（备选） | - |
| `MODEL_ID` | 模型 ID | `hunyuan-turbos-latest` |
| `LLM_TIMEOUT` | 请求超时（秒） | `60` |

## 错误处理

- API 调用异常时打印错误信息并返回 `None`
- 环境变量缺失时抛出 `EnvironmentError`，快速失败

## 架构位置

```
04-my-agent/
├── llm.py              # ← 本模块
├── context_builder.py  # 上下文构建器（消费 LLM）
├── main.py             # 入口（组合 LLM + ContextBuilder）
└── docs/
    ├── llm.md          # ← 本文档
    └── context_builder.md
```

## 后续扩展方向

| 方向 | 说明 |
|------|------|
| Tool Calling | 支持 `tools` 参数，返回结构化函数调用 |
| 重试机制 | 指数退避重试，应对限流/超时 |
| Token 计数 | 接入 tiktoken，精确统计用量 |
| 多模型切换 | 运行时动态切换不同模型 |
| 异步支持 | 提供 `async chat()` 版本 |
