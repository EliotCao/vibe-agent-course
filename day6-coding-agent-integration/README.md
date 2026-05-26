# Day6 · 整合：完整 Coding Agent

> **今天是组装日。** 把 Day1-Day5 的 6 个零件拼成一个能干真活的 Coding Agent——不到 120 行主逻辑，因为重活全在零件里。

---

## 学习目标

- [ ] 能画出完整 Agent 的模块边界与数据流
- [ ] 区分 Agent 的 3 种交互模式：REPL / 单次任务 / 流式输出
- [ ] 能把 LLM / ToolRegistry / ContextManager / Memory / 工具集 / UI 全部装到一起
- [ ] 能让自己的 Agent 完成 3 个真实任务（建项目跑测试 / 修 bug / 刁难题）
- [ ] 能识别并修复整合期常见的接口对不上问题

---

## 内容结构

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 28 | 25min | 理论 | 整合架构：6 个零件的模块边界与数据流 | [28-integration-architecture.md](./lecture/28-integration-architecture.md) |
| 29 | 20min | 理论 | UI 与交互模式：REPL / 单次任务 / 流式输出 | [29-ui-and-modes.md](./lecture/29-ui-and-modes.md) |
| — | 130min | 实操 | 组装 + 跑任务 + 对比反思 | [lab/README.md](./lab/README.md) |

---

## Demo 索引

| Demo | 功能 | 文件 |
|------|------|------|
| `demo_30` | 6 零件手动组装 walkthrough | `lab/demos/demo_30_integration_walkthrough.py` |
| `demo_31` | 3 个真实任务端到端 | `lab/demos/demo_31_three_tasks.py` |
| `my_coding_agent/` | 完整参考实现 | `lab/demos/my_coding_agent/main.py` |

---

## 当日产物

```
my_coding_agent/
├── llm/                    # Day1 LLM 客户端
├── tools/                  # Day2 ToolRegistry + Day5 工具实现
├── context/                # Day4 ContextManager
├── memory/                 # Day4 Memory（embedding + cosine）
├── agent/
│   └── agent.py            # ★ 整合主类（学生填 4 个 TODO）
├── ui/
│   └── repl.py             # REPL 交互
└── main.py                 # 入口
```

---

## 3 个真实任务

### 任务 1：建项目 + 跑测试
> "请创建 calculator.py（含 add/subtract 函数），再创建 test_calculator.py（用 assert 写测试），最后跑 pytest -v"

考察：write + bash 协同。

### 任务 2：修 bug
> 给 Agent 一个有 bug 的 `buggy.py`，让它找 bug 并修复。

考察：read + edit + bash 多轮迭代。

### 任务 3：刁难题
> "帮我访问 https://example.com 并把网页保存到 page.html"

考察：Agent 在没有网络工具时如何回应——诚实拒绝 or 用 bash + curl 变通？

---

## Checkpoint

1. `starter/my_coding_agent/` 4 个 TODO 全部填完、REPL 可运行
2. 任务 1 建项目 + 测试通过
3. `comparison.md` 有真实内容：你的实现 vs 参考实现的差异 + 一个意外发现
4. 100-200 字反思

---

## 课后练习

见 [exercises/README.md](./exercises/README.md)（3 必做 + 2 选做）

---

## 衔接关系

| 来自哪天 | 今天用哪个零件 |
|----------|----------------|
| Day1 | LLM 客户端（chat / chat_stream） |
| Day2 | ToolRegistry（装饰器 + invoke + to_schemas） |
| Day3 | Agent Loop 设计理念（循环到不再要工具为止） |
| Day4 | ContextManager（keep_last + summarize） + Memory（embedding + cosine） |
| Day5 | 5 个必做工具实现（read / list_dir / write / edit / bash） |
| → Day7 | Skills + Docker 沙箱 + CNB NPC 部署 |

---

## 教师演示备用

- `examples/ch04-my-agent/` 完整目录作为"终极参考"
- 整合期间老师**当场带做**：每 15 分钟一个 checkpoint
  1. （0:00）确认所有零件代码到位
  2. （0:15）`Agent.__init__` 跑通
  3. （0:30）单工具调用跑通
  4. （0:45）多轮工具调用 + Context 接入
  5. （1:00）Memory 持久化跑通
  6. （1:20）任务 1 完成
