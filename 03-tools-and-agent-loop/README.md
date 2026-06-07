# 第 2 章 · Function Calling 与最小 Agent

> 本章目标：理解工具调用协议，实现 ToolRegistry，搭出最小 Agent Loop。
> 产出：`my-agent/tools.py` — 你的 ToolRegistry 类。

## 你将学到

- Chatbot vs Agent：为什么需要循环
- Function Calling 协议：4 条消息的完整流转
- ToolRegistry：从函数签名自动生成 schema
- 最小 Agent Loop：LLM + Tools + While 循环

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 6 | Agent vs Chatbot | [06-agent-vs-chatbot.md](./lecture/06-agent-vs-chatbot.md) | `demo_06_chatbot_vs_agent.py` |
| 7 | Function Calling 协议 | [07-function-calling.md](./lecture/07-function-calling.md) | `demo_07_function_calling_protocol.py` |
| 8 | ToolRegistry | [08-tool-registry.md](./lecture/08-tool-registry.md) | `demo_08_tool_registry.py` |
| 9 | 最小 Agent Loop | [09-agent-loop.md](./lecture/09-agent-loop.md) | `demo_09_mini_agent.py` |

## 运行 Demo

```bash
cd 03-tools-and-agent-loop/lab
python demo_06_chatbot_vs_agent.py
python demo_07_function_calling_protocol.py
python demo_08_tool_registry.py
python demo_09_mini_agent.py
```

## 本章产出

补全 [`my-agent/tools.py`](../my-agent/tools.py) 中的 `ToolRegistry` 类，让测试通过：

```bash
cd my-agent
python tests/test_tools.py
```

## 配套练习

[`exercises/03-tools-and-agent-loop/`](../exercises/03-tools-and-agent-loop/) — 3 道代码填空题
