# Day 2 · 实操：从零搭出最小 Agent Loop

> 130 分钟 · 实操（第 10 节 + 第 11 节）

## 前提

已经跑过 4 个 demo**，分别看到：
- demo_06：Chatbot vs Agent 同一道题的差别
- demo_07：手写一次完整的 4 角色 function calling 消息流
- demo_08：ToolRegistry 自动从函数签名生成 schema
- demo_09：把上面两件事拼成 ~50 行的最小 Agent Loop

本节把这些能力**整合成自己的小工具**：

```
02-checkpoint/
├── tool_registry.py        # 自己重写一遍 ToolRegistry
├── tools.py                # 3 个示例工具
├── mini_agent.py           # 最小 Agent Loop
├── run_log.md              # 执行日志
└── reflection.md           # 100-200 字反思
```

## 时间分配

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 10min | 环境配置 + 验证 |
| B | 50min | Part 1：实现 ToolRegistry（自己写一遍，不许直接抄 demo） |
| C | 60min | Part 2：从 starter 骨架填空搭出 Agent Loop + 跑 4 个任务 |
| D | 10min | Q&A + Checkpoint 提交 |

---

## 阶段 A · 环境配置（10min）

### A.1 工作目录

```bash
mkdir 02-checkpoint
cd 02-checkpoint
```

### A.2 复用 Day1 已经装好的环境

```bash
# 在仓库根目录
uv sync --all-packages
# 或者用 01 那套独立 venv 也行
```

### A.3 准备 .env（同 Day1）

```bash
BASE_URL=<你的 API 地址>
API_KEY=<你的 API 地址>
MODEL_ID=<使用的模型 ID>
```

### A.4 验证 function calling 能跑

直接跑 demo_07 看完整消息流是否打印出来：

```bash
cd ../02-tools-and-agent-loop/lab/demos
python demo_07_function_calling_protocol.py
```

看到 `[1] system / [2] user / [3] assistant / [4] tool / [5] assistant` 5 条消息就算通了。

---

## 阶段 B · Part 1：实现 ToolRegistry（50min）<a id="part1"></a>

### 目标

写一个自己的 `tool_registry.py`，达到以下能力：

1. **装饰器注册**：`@registry.tool("...")` 一行搞定
2. **自动 schema**：从函数签名 + 类型注解自动生成 OpenAI tool schema
3. **统一调度**：`registry.invoke(name, args)` 按工具名分发
4. **异常兜底**：工具内部抛错不会让 Agent 崩，转成字符串返回

### 让你先 vibe（25min）

让他们打开 IDE，先**不要看 demo_08**，直接给 AI 这个 prompt：

```
帮我写一个 Python 类 ToolRegistry，要求：

1. 提供装饰器 .tool(description) 来注册函数为工具
2. 提供 .to_schemas() 方法，自动从函数签名生成 OpenAI function calling 的 schema 列表
   - str 类型 → "string"
   - int → "integer"
   - float → "number"
   - bool → "boolean"
   - 没有默认值的参数算 required
3. 提供 .invoke(name, args) 方法按工具名分发执行
   - 工具内部抛异常时，捕获并转成字符串返回（不上抛）
   - 找不到工具时，返回 "未知工具: xxx"
```

让他们先跑出来。**不完美没关系**——常见漏掉的点是异常兜底。

### 参考实现参考（10min）

给一份"参考代码"对照（**不要在课前发**）：详见 [`demos/demo_08_tool_registry.py`](./demos/demo_08_tool_registry.py)。

投屏时重点对比：
- 你写的 description 是从哪里读的？（docstring vs 装饰器参数）
- 你处理"参数没有类型注解"了吗？应该 fallback 成 `"string"`
- invoke 里有 try/except 吗？

### 当堂改造（15min）

让你在自己的 ToolRegistry 上加：

1. **支持默认值**：`def fn(x: int, y: int = 10)` → `y` 不在 required 里
2. **加一个 `list_tools()` 方法**返回工具名列表，便于调试

跑一遍下面这个**自测脚本**，打印输出对了就过：

```python
from tool_registry import ToolRegistry

reg = ToolRegistry()

@reg.tool("加法")
def add(a: int, b: int = 10) -> int:
    return a + b

@reg.tool("故意抛错")
def boom() -> str:
    raise ValueError("故意失败")

print(reg.list_tools())                          # ['add', 'boom']
print(reg.to_schemas()[0]["function"]["parameters"]["required"])  # ['a']  注意 b 不在
print(reg.invoke("add", {"a": 1, "b": 2}))       # '3'
print(reg.invoke("add", {"a": 1}))               # '11' (用了默认值)
print(reg.invoke("boom", {}))                    # '工具 boom 执行出错: 故意失败'
print(reg.invoke("nope", {}))                    # '未知工具: nope'
```

---

## 阶段 C · Part 2：搭最小 Agent Loop + 接 3 个工具（60min）<a id="part2"></a>

### 目标

打开 [`starter/mini_agent.py`](./starter/mini_agent.py)（已经准备好的填空骨架），把里面 4 个 `TODO` 填上，让 4 个测试任务都能跑通。

### Step 1：填空骨架（30min）

骨架已经做了的事：
- 帮你内联了一份 ToolRegistry
- 注册了 3 个工具：`calculator` / `current_time` / `fetch_url`
- 准备好了 4 个测试任务

你要填的事：
- TODO ① 调 LLM
- TODO ② 检查 tool_calls
- TODO ③ 追加 assistant 消息
- TODO ④ 执行工具 + 追加 tool 消息

每个 TODO 旁边都标了"对应第 9 节哪个核心点"。**对照讲义填，不要直接抄 demo_09**——抄了你不会真懂。

### Step 2：跑 4 个任务，记录日志（20min）

```bash
python mini_agent.py > run_log.txt 2>&1
```

把 `run_log.txt` 整理成 **`run_log.md`**，每个任务一段，至少包含：
- 任务问题
- 跑了几轮才结束
- 模型在每一轮调了什么工具
- 最终答案

### Step 3：观察 4 号任务"故意刁难"的反应（10min）

任务 4 是"2099 年世界杯冠军是谁？"——没有合适的工具能回答。

理想情况：模型应该承认不知道。
常见错误情况：
- 模型硬调 `fetch_url("https://wikipedia.org/world-cup-2099")` → 抓到的内容里没有
- 模型连续调好几轮，每次都失败
- 模型最后被 max_iters 截断

**记录你的 Agent 在这个任务上的反应**，这是 Day2 Checkpoint 必交的内容。

---

## 阶段 D · Q&A + Checkpoint（10min）

### 提交清单

```
02-checkpoint/
├── tool_registry.py            # 你自己写的注册表（含异常兜底）
├── mini_agent.py               # 填空版的 Agent Loop（4 个 TODO 都填了）
├── run_log.md                  # 4 个任务的执行日志
└── reflection.md               # 100-200 字反思
```

### 反思要求（reflection.md）

必须包含：
- 你在写 ToolRegistry 时**最容易忘**的细节是什么？
- 在 mini_agent.py 的 4 个 TODO 里，你**写错过的**是哪个？错在哪？
- 任务 4 你的 Agent 是怎么反应的？合理吗？怎么让它更好？
- 一个明天 Day3 你想看到的东西

---

## 助教检查重点

- [ ] tool_registry.py 是自己写的，不是 demo_08 直接拷贝（看变量命名 / 注释）
- [ ] tool_registry 里 invoke 有异常兜底
- [ ] mini_agent.py 真的在 messages 里追加了 assistant 消息（带 tool_calls 字段）
- [ ] 跑 4 个任务，前 3 个都能跑通；第 4 个能看到"承认不知道 / 硬调失败"两种反应之一
- [ ] reflection.md 不是水文，至少有一个具体观察

## 参考资产（仅卡住时参考）

- [`demos/demo_08_tool_registry.py`](./demos/demo_08_tool_registry.py) —— ToolRegistry 参考实现
- [`demos/demo_09_mini_agent.py`](./demos/demo_09_mini_agent.py) —— 完整 Agent Loop
- [`examples/04-my-agent/tools/tools.py`](../../examples/04-my-agent/tools/tools.py) —— 工程级 ToolRegistry（含 Tool 基类、装饰器/类双注册）
- [`examples/04-my-agent/agent/agent.py`](../../examples/04-my-agent/agent/agent.py) —— SimpleAgent / ReActAgent 主循环

> 注意：ch04 的 ToolRegistry 比今天教的复杂得多（Tool 基类 / 双注册路径 / 工具描述自动注入 prompt）。**今天先掌握极简版，Day5 / Day6 会逐步迭代到 ch04 的复杂度。**
