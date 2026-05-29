# 第 3 章 · 实操：实现并对比三种 Agent 范式

> 130 分钟 · 实操（第 15-17 节）

## 前提

已经在前 3 节看过 3 个 demo：
- `demo_12_react.py` —— ReAct（prompt + 正则）
- `demo_13_plan_and_solve.py` —— Plan-and-Solve（Planner + Executor + Aggregator）
- `demo_14_reflection.py` —— Reflection（包装在 Plan-and-Solve 外面）

并且**复用第2章的 ToolRegistry**（已经在 `toy_agent_base.py` 内置了一份）。

## 时间分配

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 5min | 看参考实现，理解 5 个测试任务 |
| B | 50min | Part 1：填空 `agent_react.py` |
| C | 50min | Part 2：填空 `agent_plan_solve.py` |
| D | 25min | Part 3：填空 `agent_reflection.py` + 跑横向对比，写 `comparison.md` |

## 当日产物

```
03-checkpoint/
├── agent_react.py          # 你填空补完的 ReAct
├── agent_plan_solve.py     # 你填空补完的 Plan-and-Solve
├── agent_reflection.py     # 你填空补完的 Reflection
├── comparison.md           # 5 个任务三种范式对比表
└── reflection.md           # 100-200 字反思
```

---

## 阶段 A · 看骨架（5min）

```bash
cd 03-agent-patterns/lab
ls -la
```

你会看到 3 个范式实现，在 `lab/` 里的 4 个完整版（demo_12/13/14 + toy_agent_base）。

**核心约定**：所有范式都从 `toy_agent_base` 里 import 同一套工具集和同一组 5 个任务，让横向对比是 apple-to-apple。

5 个测试任务（详见 `toy_agent_base.py`）：

| 编号 | 任务 | 测什么 |
|---|---|---|
| 1 | 北京天气 + 推荐景点 | 串联两个工具 |
| 2 | A001/A002/A003 总价 + 平均 | 多次调同一工具 + 计算 |
| 3 | 深圳天气 + 雨天改室内 | 条件判断 |
| 4 | 上海天气 + 景点 + 数汉字 | 工具结果做后处理 |
| 5 | "2099 年世界杯冠军" | 故意刁难 |

---

## 阶段 B · Part 1：ReAct 填空（50min）<a id="part1"></a>

打开 `demo_12_react.py`，里面三个 TODO：

| TODO | 难度 | 提示 |
|---|---|---|
| ① 写 `REACT_PROMPT_TEMPLATE` | 中 | 严格约束输出格式，每次一对 Thought/Action |
| ② 写 `parse_react_output` | 中 | 正则抠 Thought 和 Action |
| ③ 写 `parse_action` | 中 | 解析两种格式：`tool(...)` / `Finish[...]` |

### 动手 vibe（30min）

让你先**不要看 demo_12**，直接给 AI 这个 prompt：

```
帮我写一个 ReAct 风格的 prompt 模板和解析函数：

1. prompt 让模型严格输出格式：
   Thought: ...
   Action: tool_name(arg="value") 或 Finish[最终答案]
   每次只输出一对，不要多输出。

2. 写 parse_react_output(text) 用正则抠出 thought 和 action 字符串
   注意：模型可能多说一句话、可能输出多对、可能 Action 后面还有 Observation

3. 写 parse_action(action_str) 返回 (kind, name_or_answer, args_dict)
   kind ∈ {"finish", "tool", "error"}
   tool 调用解析 arg="value" 形式的 kwargs
```

让他们跑一遍 5 个任务，**故意先不做容错**——看哪个任务挂了，再回头加 fallback。

### 参考演示（10min）

参考实现 [`demo_12_react.py`](./demo_12_react.py) 的 `parse_react_output` 和 `parse_action`，重点对比：
- 你的 Thought 正则有没有处理 `Action:` 之后还有内容的情况
- 你的 Action 有没有截断（用 `(?=...)` 前瞻）
- `Finish[...]` 里的 `]` 转义了吗？

### 当堂改造（10min）

让你在自己的 ReAct 上加：

1. **截断兜底**：模型一次输出 2 对 Thought-Action 时，只保留第一对（参考 ch01 的做法）
2. **空 Action 兜底**：解析失败时不要崩，写一条 Observation 让模型下一轮看到错误并重试

---

## 阶段 C · Part 2：Plan-and-Solve 填空（50min）<a id="part2"></a>

打开 `demo_13_plan_and_solve.py`，4 个 TODO：

| TODO | 难度 | 提示 |
|---|---|---|
| ① 写 `PLANNER_PROMPT` | 中 | 强约束 JSON 数组输出 |
| ② 解析 Planner 输出 | 中 | 处理 ` ```json ``` ` 包裹 |
| ③ 写 `execute_step` | 高 | **复用第2章的最小 Agent Loop**（你的代码） |
| ④ 写 `aggregate` | 低 | 拼一段 prompt 让 LLM 汇总 |

### 关键提示

**TODO ③ 是今天最大的"零件复用"点**：

`execute_step()` 内部就是第2章你写的 `mini_agent.py` 的核心循环。把第2章那部分代码**搬过来**，加一个 system prompt 说"你正在执行子任务"，user prompt 把"前序结果 + 本步任务"拼上即可。

如果第2章的代码丢了，参考 [`demo_13_plan_and_solve.py`](./demo_13_plan_and_solve.py) 的 `execute_step` 函数（30 行内）。

### 跑通 5 个任务后观察

把 5 个任务都跑一遍，记录每个任务**Planner 拆出了几步**：

| 任务 | Planner 拆出几步 | 你觉得合理吗？ |
|---|---|---|
| 1 | ? | |
| 2 | ? | |
| 3 | ? | |
| 4 | ? | |
| 5 | ? | |

任务 5 是个观察重点——Planner 会怎么拆这个"无解"任务？

---

## 阶段 D · Part 3：Reflection + 横向对比（25min）<a id="part3"></a>

### 25min 安排

| 时间 | 干什么 |
|---|---|
| 0-10min | 填空 `agent_reflection.py` 三个 TODO |
| 10-20min | 把 5 个任务跑三遍（react / plan_solve / reflection），记录数据 |
| 20-25min | 写 `comparison.md` |

### Reflection 填空

打开 `demo_14_reflection.py`：
| TODO | 提示 |
|---|---|
| ① `REVIEW_PROMPT` | 检查清单 + VERDICT/ISSUES 结构化输出 |
| ② 解析 VERDICT | 正则取 `VERDICT:\s*(\w+)` |
| ③ `refine` 函数 | 拼"基于评审重写"的 prompt 调一次 LLM |

### comparison.md 模板

```markdown
# 三种范式横向对比

| 任务 | ReAct（步数 / token / 答对？） | Plan-Solve（步数 / token / 答对？） | Reflection（轮数 / token / 答对？） |
|---|---|---|---|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |
| 4 | ... | ... | ... |
| 5 | ... | ... | ... |

## 我的判断指南

- 当任务是 XX 类型时，应该选 ReAct，因为 ___
- 当任务是 YY 类型时，应该选 Plan-and-Solve，因为 ___
- 当任务是 ZZ 类型时，应该套 Reflection，因为 ___

## 一个意外发现

（你跑出来的，最让你意外的一件事）
```

> token 消耗可以从 `client.chat.completions.create()` 返回的 `resp.usage.total_tokens` 拿到。
> 在 demo 里加一个全局 `_total_tokens += usage.total_tokens` 计数即可。

---

## 阶段 E · Q&A + Checkpoint

### 提交清单

```
03-checkpoint/
├── agent_react.py
├── agent_plan_solve.py
├── agent_reflection.py
├── comparison.md
└── reflection.md
```

### 反思要求（reflection.md）

必须包含：
- 你跑 5 个任务时，**哪个范式让你最意外**？为什么？
- ReAct 的正则解析在哪个任务上崩了？怎么修的？
- 如果让你重新设计第3章的"5 个测试任务"，你会换掉哪个，加什么？
- 一个下一章（第4章）你想看到的东西

---

## 助教检查重点

- [ ] `agent_react.py` 的 prompt 有 Thought + Action 的明确格式约束
- [ ] `agent_react.py` 的解析有处理 `Action:` 后面还有 Observation 的情况
- [ ] `agent_plan_solve.py` 的 Planner 输出是真的 JSON 数组（不是字符串拼凑）
- [ ] `agent_plan_solve.py` 的 Executor 真的复用了第2章那套 tool_calls 循环（不是 ReAct 字符串解析）
- [ ] `agent_reflection.py` 至少跑一次 review 给出过 NEEDS_REVISION
- [ ] `comparison.md` 含 5 个任务的三栏对比，**且写出了"一个意外发现"**

---

## 参考资产（仅卡住时参考）

| 情况 | 投屏什么 |
|---|---|
| ReAct 解析卡住 | `demo_12_react.py` 的 `parse_react_output` |
| Plan 输出 JSON 失败 | `demo_13_plan_and_solve.py` 的 `make_plan` 容错 |
| Reflection 评审员从不挑刺 | `demo_14_reflection.py` 的 `REVIEW_PROMPT` 检查清单 |
| 想看工程级 ReAct | [`examples/01-hello-react/agent.py`](../../examples/01-hello-react/agent.py) 的 truncate 逻辑 |
| 想看 hello-agents 框架对照 | [`examples/03-hello-agents/main.py`](../../examples/03-hello-agents/main.py) |

> tip：[`examples/03-hello-agents/main.py`](../../examples/03-hello-agents/main.py) 里有一段 `patch_react_agent_logging_and_parser` ——这就是工业框架为了应对"模型不规矩"打的补丁。投屏看一下，**让他们感受工业版做了多少 fallback**。
