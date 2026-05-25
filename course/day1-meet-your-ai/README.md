# Day 1 · 认识你的 AI

> 本章目标：理解 LLM 的工作原理、使用方式和局限性，为后续构建 Agent 打下基础。

## 你将学到

- LLM 为什么具备智能（next-token prediction + 涌现）
- 如何与 LLM 对话（messages 协议、三种角色）
- Token 与上下文窗口：成本和约束
- 大模型幻觉：成因、识别与缓解
- 为什么需要给 LLM 配工具与上下文（Agent 的雏形）

## 内容结构

| 章节 | 内容 | 讲义 | Demo |
|------|------|------|------|
| 1 | LLM 为什么具备智能 | [01-why-llm-is-smart.md](./lecture/01-why-llm-is-smart.md) | `demo_01_next_token.py` |
| 2 | 提示词与角色 | [02-prompts-and-roles.md](./lecture/02-prompts-and-roles.md) | `demo_02_roles.py` |
| 3 | Token 与上下文窗口 | [03-tokens-and-context.md](./lecture/03-tokens-and-context.md) | `demo_03_tokens.py` |
| 4 | 大模型幻觉 | [04-hallucination.md](./lecture/04-hallucination.md) | `demo_04_hallucinate.py` |
| 5 | LLM + 外部支持 | [05-llm-needs-augmentation.md](./lecture/05-llm-needs-augmentation.md) | `demo_05_with_tool.py` |

## 配套 Demo

所有 demo 在 `lab/demos/` 目录下，运行前确保环境变量已配置（参见 `_env.py`）：

```bash
cd lab/demos
python demo_00_chat.py           # 最简交互式对话
python demo_01_next_token.py     # 看模型怎么"猜下一个词"
python demo_02_roles.py          # system prompt 改变模型人格
python demo_03_tokens.py         # tokenization + 成本估算
python demo_04_hallucinate.py    # 主动诱发幻觉
python demo_05_with_tool.py      # 加工具前后对比
```

## 参考实现

- `ch02-hello-llm/main.py` —— 流式调用参考实现
- `ch04-my-agent/llm/llm.py` —— 工程级 LLM 客户端
