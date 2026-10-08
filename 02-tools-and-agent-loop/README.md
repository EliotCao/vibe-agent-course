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
| 5 | Agent vs Chatbot | [05-agent-vs-chatbot.md](./lecture/05-agent-vs-chatbot.md) | `demo_05_chatbot_vs_agent.py` |
| 6 | Function Calling 协议 | [06-function-calling.md](./lecture/06-function-calling.md) | `demo_06_function_calling_protocol.py` |
| 7 | ToolRegistry | [07-tool-registry.md](./lecture/07-tool-registry.md) | `demo_07_tool_registry.py` |
| 8 | 最小 Agent Loop | [08-agent-loop.md](./lecture/08-agent-loop.md) | `demo_08_mini_agent.py` |
| 9 | Tool Calling 扩展面（MCP / Skill / RAG 预告） | [09-tool-calling-extensions.md](./lecture/09-tool-calling-extensions.md) | — |

## 运行 Demo

```bash
cd 02-tools-and-agent-loop/lab
python demo_05_chatbot_vs_agent.py
python demo_06_function_calling_protocol.py
python demo_07_tool_registry.py
python demo_08_mini_agent.py
```

## 作业指引

本章作业在配套作业仓库中完成：

> 📦 **作业仓库**：<https://cnb.cool/xidian/vibe-coding-learning/vibe-agent-exercise>

**流程**：Fork 作业仓库 → 在 `my-agent/`（核心产出）与 `exercises/`（配套填空）中完成本章任务 → 提交 PR，CI 流水线（`.cnb.yml`）自动测评，全绿即通过。

## 本章产出

在作业仓库中补全 `my-agent/tools.py` 的 `ToolRegistry` 类，让测试通过：

```bash
cd my-agent
python tests/test_tools.py
```

## 配套练习

作业仓库的 `exercises/02-tools-and-agent-loop/` — 3 道代码填空题（运行 `python exercises/02-tools-and-agent-loop/ex_*.py` 看到 ✅ PASSED 即通过）。
