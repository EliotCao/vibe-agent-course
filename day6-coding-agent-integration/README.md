# Day 6 · 整合：完整 Coding Agent

> 今天是组装日。把 Day2-Day5 的零件拼成一个能干真活的 Coding Agent。

## 学习目标

- [ ] 能画出完整 Agent 的模块边界与数据流
- [ ] 区分 Agent 的 3 种交互模式：REPL / 单次任务 / 流式输出
- [ ] 能把 ToolRegistry / ContextManager / Memory / 工具集 / Agent Loop 全部装到一起
- [ ] 能让自己的 Agent 完成 3 个真实任务
- [ ] 能识别并修复整合期常见的接口对不上问题

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 28 | 25min | 理论 | 整合架构：模块边界与数据流 | [28-integration-architecture.md](./lecture/28-integration-architecture.md) |
| 29 | 20min | 理论 | UI 与交互模式：REPL / 单次任务 / 流式输出 | [29-ui-and-modes.md](./lecture/29-ui-and-modes.md) |
| 30 | 80min | 实操 | 把所有零件装到一个 Agent 类 | [lab/part1](./lab/README.md#part1) |
| 31 | 70min | 实操 | 让你的 Agent 完成 3 个真实任务 | [lab/part2](./lab/README.md#part2) |
| 32 | 15min | 实操 | 故障排查与调优 + 答疑 | — |

## 当日产物

```
my_coding_agent/
├── llm/                    # 来自 Day1
├── tools/                  # ToolRegistry 来自 Day2，工具实现来自 Day5
├── context/                # 来自 Day4
├── memory/                 # 来自 Day4
├── agent/
│   └── agent.py            # 整合主类
├── ui/
│   └── repl.py             # REPL 交互
└── main.py                 # 入口（支持 REPL / 单次任务两种模式）
```

## 3 个真实任务（学生 vibe 自己的 Agent 完成）

### 任务 1：让 Agent 给 Day5 的工具集生成 README
> "请阅读 coding_tools/ 目录，给每个工具生成一段说明，最后整合成 coding_tools/README.md"

考察：list_dir / read_file / write_file 协同。

### 任务 2：补单测
> "给 coding_tools/edit.py 补单测，确保测试通过且 coverage ≥ 80%"

考察：read / write / bash（跑测试）/ 多轮迭代。

### 任务 3：找 bug
> （老师在某个工具里**故意埋一个 bug**，比如 `read.py` 偏移量算错）
> "我代码有问题：调 read_file(path, offset=10) 拿到的不是第 10 行开始。帮我找出来并修。"

考察：read / grep / edit / 调试推理。

## Checkpoint

1. `my_coding_agent/` 完整可跑
2. 3 个任务的执行录屏（每个 ≤ 1 分钟）
3. 一段"我的 Agent 跟 Cursor / Claude Code 比，差距在哪"（≥ 5 条具体差距）
4. 100-200 字反思

## 教师演示备用

- `ch04-my-agent/` 整体目录，特别是 `agent/agent.py` 和 `main.py`
- 整合期间老师**当场带做**：每 15 分钟一个 checkpoint
  1. （0:00）确认所有零件代码到位
  2. （0:15）`Agent.__init__` 跑通
  3. （0:30）单工具调用跑通
  4. （0:45）多轮工具调用 + Context 接入
  5. （1:00）Memory 持久化跑通
  6. （1:20）任务 1 完成
