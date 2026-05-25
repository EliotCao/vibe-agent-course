# Day 2 · Function Calling 与最小 Agent

> 今天结束时，每个学生亲手实现一个工具注册系统，搭出最小 Agent 循环，理解 Function Calling 协议。

## 学习目标

- [ ] 解释 Agent 与 Chatbot 的本质区别：循环
- [ ] 看懂 Tool Schema 的 JSON 结构
- [ ] 看懂带 `tool_calls` 的消息流（4 种角色：system / user / assistant / tool）
- [ ] 能从零实现一个 `ToolRegistry` 类（自动从函数生成 Schema）
- [ ] 能搭出一个 30 行以内的最小 Agent Loop，跑通 3 个工具

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 7 | 20min | 理论 | Agent vs Chatbot：为什么需要循环 | [07-agent-vs-chatbot.md](./lecture/07-agent-vs-chatbot.md) |
| 8 | 40min | 理论 | Function Calling 协议：Tool Schema 与消息流 | [08-function-calling.md](./lecture/08-function-calling.md) |
| 9 | 20min | 理论 | 最小 Agent Loop 的 5 个核心点 | [09-agent-loop.md](./lecture/09-agent-loop.md) |
| 10 | 60min | 实操 | 实现 ToolRegistry（工具注册类）| [lab/part1](./lab/README.md#part1) |
| 11 | 70min | 实操 | 搭最小 Agent Loop + 接 3 个简单工具 | [lab/part2](./lab/README.md#part2) |

## 当日产物

```
day2/
├── tool_registry.py     # 工具注册类
├── tools.py             # 3 个示例工具
└── mini_agent.py        # 最小 Agent Loop（< 50 行核心代码）
```

3 个示例工具：
- `calculator(expr)` — 计算数学表达式
- `current_time(tz)` — 获取当前时间
- `fetch_url(url)` — 抓网页前 500 字

## Checkpoint

1. 完整代码
2. 一段执行日志：让 Agent 完成"查 https://example.com 的内容长度并把它除以 7"，全过程
3. **一段失败 case**：让 Agent 做一个"无法用现有工具完成的任务"，记录它怎么处理（理想情况是承认做不到；常见错误是硬调工具）
4. 100-200 字反思

## 教师演示备用

- `ch04-my-agent/tools/tools.py` —— ToolRegistry 工程级实现
- `ch04-my-agent/agent/agent.py` —— Agent 主循环
