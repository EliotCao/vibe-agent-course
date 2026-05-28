# CodingAgent 设计文档

## 概述

`coding_agent.py` 实现了一个极简版 Claude Code —— 基于 **Function Calling + 对话循环 + 多工具** 的交互式编程助手。

## 与简化版 Agent 的区别

| 维度 | SimpleAgent / ReActAgent | CodingAgent |
|------|--------------------------|-------------|
| 工具调用 | 文本标记解析 | OpenAI Function Calling |
| 参数传递 | 单字符串 | 结构化 JSON（多参数） |
| 交互方式 | 一问一答 | 持续对话循环（REPL） |
| 工具数量 | 1-2 个演示工具 | 9 个实用工具 |
| 上下文 | 手动管理 | 自动累积 messages |

## 核心架构

```
┌─────────────────────────────────┐
│          用户 (REPL)             │
└──────────────┬──────────────────┘
               │ input
┌──────────────▼──────────────────┐
│         CodingAgent              │
│                                  │
│  messages[]  ←── 完整对话历史    │
│  registry    ←── 9 个工具       │
│  llm         ←── LLM 客户端    │
└──────────────┬──────────────────┘
               │ chat(tools=schema)
┌──────────────▼──────────────────┐
│           LLM                    │
│  Function Calling 模式           │
│  返回 tool_calls 或 文本回答    │
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       │               │
  tool_calls?      直接回答
       │               │
       ▼               ▼
  执行工具          输出给用户
  结果注入
  再次调用 LLM
```

## 核心循环

```python
while True:
    user_input = input("> ")
    messages.append(user_input)
    
    while True:
        response = llm.chat(messages, tools=schema)
        
        if response.tool_calls:
            执行每个工具
            结果注入 messages
            continue
        else:
            输出 response.content
            break
```

## 工具集

| 工具 | 用途 |
|------|------|
| `read` | 读文件（带行号） |
| `write` | 写文件 |
| `edit` | 精确替换内容 |
| `list` | 列目录 |
| `glob` | 匹配文件名 |
| `grep` | 搜索文件内容 |
| `bash` | 执行 shell 命令 |
| `todo` | 管理任务列表 |
| `webfetch` | 抓取网页 |

## Messages 结构

完整对话历史保持在 `self.messages` 中：

```
[system]      系统提示（角色 + 能力 + 原则）
[user]        用户第一次输入
[assistant]   LLM 回复（可能含 tool_calls）
[tool]        工具执行结果（tool_call_id 关联）
[assistant]   LLM 最终回答
[user]        用户第二次输入
...
```

## 运行方式

```bash
cd 04-my-agent
python coding_agent.py             # 当前目录
python coding_agent.py /path/to   # 指定工作目录
```

## 命令

| 命令 | 说明 |
|------|------|
| `/quit` | 退出 |
| `/reset` | 重置对话历史 |

## 后续扩展

| 方向 | 说明 |
|------|------|
| 流式输出 | LLM 文本回答流式打印 |
| 确认机制 | 写文件/执行命令前征求用户确认 |
| Token 预算 | 对话过长时自动压缩历史 |
| 多模型 | 支持切换不同 LLM |
| 项目感知 | 启动时自动扫描项目结构注入 context |
