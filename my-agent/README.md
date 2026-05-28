# my-agent：从零搭建你的 Coding Agent

> 这是你 Day1-Day6 的核心产出目录。每天实现一个模块，最终 Day6 拼装成完整 Agent。

## 目录结构

```
my-agent/
├── llm.py              # Day1：LLM 客户端
├── tools.py            # Day2：ToolRegistry
├── agent.py            # Day3：Agent 主循环
├── context.py          # Day4：ContextManager
├── memory.py           # Day4：Memory
├── coding_tools/       # Day5：具体工具实现
│   ├── __init__.py
│   ├── read.py
│   ├── write.py
│   ├── edit.py
│   ├── list_dir.py
│   └── bash.py
├── main.py             # Day6：组装入口
└── tests/              # 每天的测试用例
    ├── test_llm.py
    ├── test_tools.py
    ├── test_agent.py
    ├── test_context.py
    ├── test_memory.py
    └── test_coding_tools.py
```

## 搭建路线

| Day | 产出文件 | 核心接口 |
|-----|---------|---------|
| 1 | `llm.py` | `LLMClient.chat()` / `.chat_stream()` / `.count_tokens()` |
| 2 | `tools.py` | `ToolRegistry.register()` / `.to_schemas()` / `.invoke()` |
| 3 | `agent.py` | `Agent.run()` — LLM + Tools + Loop |
| 4 | `context.py` + `memory.py` | `ContextManager.compress()` + `Memory.add/search()` |
| 5 | `coding_tools/*.py` | 5 个工具函数注册到 ToolRegistry |
| 6 | `main.py` | 把所有零件拼起来，跑通一个真任务 |

## 验证方式

```bash
cd my-agent
python -m pytest tests/ -v
```

每天只需要让当天的测试通过即可。
