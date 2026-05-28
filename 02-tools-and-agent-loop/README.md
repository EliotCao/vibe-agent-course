# Day 2 · Function Calling 与最小 Agent

> 今天结束时，每个人亲手实现一个工具注册系统，搭出 ~50 行的最小 Agent Loop，理解 Function Calling 协议。

## 你将学到

- Agent 与 Chatbot 的本质区别：**循环**
- Tool Schema 的 JSON 结构：name / description / parameters / required
- 4 角色消息流（system / user / assistant / **tool**）和 `tool_calls` 字段
- 用装饰器 + 反射写一个极简 `ToolRegistry`：从函数签名自动生成 schema
- 最小 Agent Loop 的 5 个核心点 + 必须配的"刹车"

## 内容结构

| 节 | 类型 | 内容 | 讲义 | Demo |
|----|------|------|------|------|
| 6 | 理论 · 20min | Agent vs Chatbot：为什么需要循环 | [06-agent-vs-chatbot.md](./lecture/06-agent-vs-chatbot.md) | `demo_06_chatbot_vs_agent.py` |
| 7 | 理论 · 40min | Function Calling 协议：Tool Schema 与 4 角色消息流 | [07-function-calling.md](./lecture/07-function-calling.md) | `demo_07_function_calling_protocol.py` |
| 8 | 理论 · 20min | ToolRegistry：从函数到 Schema 的自动化 | [08-tool-registry.md](./lecture/08-tool-registry.md) | `demo_08_tool_registry.py` |
| 9 | 理论 · 20min | 最小 Agent Loop 的 5 个核心点 | [09-agent-loop.md](./lecture/09-agent-loop.md) | `demo_09_mini_agent.py` |
| 10-11 | 实操 · 130min | 亲手搭出 ToolRegistry + Agent Loop + 跑 4 个任务 | [lab/README.md](./lab/README.md) | 参考 `lab/demo_09_mini_agent.py` |

## 配套 Demo

所有 demo 在 `lab/` 目录下，运行前确保环境变量已配置（参见 `_env.py`）：

```bash
cd lab/demos
python demo_06_chatbot_vs_agent.py        # 同一道题，循环不循环差别有多大
python demo_07_function_calling_protocol.py  # 手写完整 4 角色消息流
python demo_08_tool_registry.py           # 装饰器 + 反射自动生成 schema
python demo_09_mini_agent.py              # 完整 Agent Loop，跑 4 个任务
```

## 当日产物

lab 提交的目录结构：

```
02-checkpoint/
├── tool_registry.py        # 自己写的 ToolRegistry（装饰器 + inspect + 异常兜底）
├── mini_agent.py           # 最小 Agent Loop
├── run_log.md              # 4 个任务的执行日志
└── reflection.md           # 100-200 字反思
```

3 个示例工具：
- `calculator(expr)` — 算术表达式
- `current_time()` — 当前时间
- `fetch_url(url)` — 抓网页前 500 字

## Checkpoint

1. **完整代码**：`tool_registry.py` + `mini_agent.py`，4 个 TODO 都填好
2. **执行日志**：让 Agent 跑通 "抓 https://example.com 内容长度并除以 7"，记录每一轮调了什么工具
3. **失败 case 观察**：让 Agent 做"无法用现有工具完成的任务"（如"2099 年世界杯冠军是谁"），记录它的反应——理想是承认做不到；常见错误是硬调工具
4. **100-200 字反思**：看 [lab/README.md → 反思要求](./lab/README.md#反思要求reflectionmd)

## 跟 Day1 / Day3 的衔接

| 来自 Day1 | 今天怎么用 |
|---|---|
| 流式调用 LLM 的客户端 | 今天调用 LLM 的方式不变，**多传一个 `tools=` 参数** |
| messages 协议（system / user / assistant） | 今天**多了第 4 种角色 `tool`** |
| RAG（手动塞资料） | 今天升级成"模型自己决定调什么工具"，是 RAG 的自动化版 |

| 今天产出 | Day3 / Day4 / Day5 怎么用 |
|---|---|
| `ToolRegistry` | Day5 给它接 9 个真正的 Coding 工具（read/write/edit/bash...） |
| 最小 Agent Loop | Day3 在循环里玩 ReAct / Plan-and-Solve / Reflection 三种范式 |
| `messages` 列表 | Day4 给它加上下文管理（截断 / 摘要 / 分层）防止爆窗 |

## 参考实现

- [`examples/04-my-agent/tools/tools.py`](../examples/04-my-agent/tools/tools.py) —— 工程级 ToolRegistry（含 `Tool` 基类 + 装饰器双注册路径）
- [`examples/04-my-agent/agent/agent.py`](../examples/04-my-agent/agent/agent.py) —— `SimpleAgent` / `ReActAgent` 主循环（Day3 还会再深入对比）

> 这两份"工程级"实现不是今天要抄的——今天先掌握极简版（80 行 ToolRegistry + 50 行 Loop），后面几天再迭代到工程级。

## 课后练习题

详见 [exercises/README.md](../exercises/02-tools-and-agent-loop/README.md)：

- 必做 3 题：Schema 反向工程 / 并行工具调用 / 错误处理压测
- 选做 2 题：enum 支持 / "先想再做" 范式预热

## 参考资产

卡住时参考：

| 情况 | 投屏什么 |
|---|---|
| ToolRegistry 卡住 | `demo_08_tool_registry.py` |
| messages 拼错（漏了 assistant.tool_calls） | `demo_07_function_calling_protocol.py` 最后那段完整 messages 历史 |
| Agent Loop 跑飞了 | `demo_09_mini_agent.py` 主循环 |
| 想看工程级长什么样 | `examples/04-my-agent/agent/agent.py` 的 `SimpleAgent` |
