# Day 2 · 课后练习题

> 课后完成。每题 20-60 分钟。下次课前提交。

## 必做（3 题）

### 练习 2.1 · Schema 反向工程

下面这个 schema 是某个工具的对外接口：

```json
{
  "type": "function",
  "function": {
    "name": "search_repo",
    "description": "在当前 git 仓库里搜索包含某个关键字的文件",
    "parameters": {
      "type": "object",
      "properties": {
        "keyword": {
          "type": "string",
          "description": "要搜索的关键字"
        },
        "case_sensitive": {
          "type": "boolean",
          "description": "是否区分大小写"
        },
        "limit": {
          "type": "integer",
          "description": "最多返回多少个结果"
        }
      },
      "required": ["keyword"]
    }
  }
}
```

**要求：**

1. 写一个 Python 函数 `search_repo(...)`，能让你的 ToolRegistry **生成的 schema 跟上面这份一模一样**（包括 required 列表）
2. 把它注册到你 Day2 的 ToolRegistry，调一下 `to_schemas()` 打印出来对比
3. 可以**不真去搜文件**——返回一个 mock 字符串就行

提交：
- `search_repo` 的源码
- `to_schemas()` 输出的 JSON
- 一段 50 字以内的反思：哪些字段必须靠你"主动设计"，靠 inspect 自动推不出来

> 这题考你对 Tool Schema 字段的理解。是 Day5 设计 Coding 工具的预热。

---

### 练习 2.2 · 并行工具调用

让你的 Agent 完成这个任务：

> "请同时帮我查北京、上海、深圳今天的天气，告诉我哪个城市最热。"

要求：
1. **观察**模型一次返回了几个 `tool_call`（应该是 3 个并行的 `get_weather`）
2. 把 3 个工具调用**真正并行执行**——不能 for 循环串行
3. 拿到 3 个结果后，模型应该第二轮直接给最终答案

实现提示：
```python
# 串行写法（容易，但慢）
for tc in msg.tool_calls:
    result = registry.invoke(tc.function.name, args)
    ...

# 并行写法（用 ThreadPoolExecutor 即可，工具是 IO bound）
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(registry.invoke, tc.function.name, ...) for tc in msg.tool_calls]
    results = [f.result() for f in futures]
```

提交：
- 改造后的 `mini_agent.py`
- 一段执行日志，看到"模型一次返回 3 个 tool_call，3 个并行执行"
- 100 字反思：如果 3 个工具中有 1 个失败了，你的并行版本是怎么处理的

---

### 练习 2.3 · 错误处理压力测试

故意给你的 Agent 一些"会出错"的工具调用，看它怎么反应。

**步骤 1**：在 `mini_agent.py` 里再加一个**故意失败**的工具：

```python
@registry.tool("查询某个用户的余额（未实现）")
def get_balance(user_id: str) -> str:
    raise RuntimeError("数据库连接失败：服务暂不可用")
```

**步骤 2**：让 Agent 跑这个问题：
> "查一下用户 alice 的余额，再换算成美元（1 美元 ≈ 7 元）。"

**观察并记录：**
1. Agent 第一轮调用 `get_balance` → 拿到 "工具 get_balance 执行出错: ..."
2. Agent 第二轮会怎么做？
   - 理想：承认 "余额查询失败，无法换算"
   - 不理想 1：再调一次 `get_balance`（重试不修参数 = 死循环）
   - 不理想 2：自己编一个余额数字接着算下去（**这是幻觉的工程版**）

**步骤 3**：根据观察结果，给你的 Agent 加一道额外的"刹车"：**同一个工具同样参数被连续调用 ≥ 2 次时，强制返回错误终止循环。**

提交：
- 改造后的 `mini_agent.py`
- 4 段日志：
  - 改造前：跑这个任务，看 Agent 怎么反应
  - 改造后：跑这个任务，看 Agent 怎么反应
- 100-200 字反思：你觉得这种"工具失败 → 模型硬调"的现象，在生产环境里更值得重视的是哪类工具？（提示：写文件 / 删文件 / 调用收费 API ……）

> 这题是 Day5 / Day6 健壮性的预热。

---

## 选做（任选 1 题）

### 练习 2.4 · 给 ToolRegistry 加 enum 支持

让你的 ToolRegistry 能自动识别 `Literal` 类型，把它转成 OpenAI schema 的 `enum`：

```python
from typing import Literal

@registry.tool("查询某城市的天气")
def get_weather(city: Literal["北京", "上海", "深圳"]) -> str:
    ...

# to_schemas() 应该输出：
# "city": {"type": "string", "enum": ["北京", "上海", "深圳"]}
```

提交：
- 改造后的 `tool_registry.py`
- `to_schemas()` 输出对比
- 一段 50 字反思：加了 enum 之后，模型调错参数（比如传 "纽约"）的概率有变化吗？

---

### 练习 2.5 · 让 Agent 学会"先想再做"

观察今天的 Agent：每一轮模型都直接发 tool_call，没有"思考"的环节。改造一下 system prompt，让它在调工具前**先输出一段思考**（assistant.content 不再是 None）：

```
任务：现在几点了？

模型应该输出：
content: "用户问当前时间，我需要调 current_time。"
tool_calls: [current_time()]
```

提交：
- 改造后的 system prompt
- 跑同样 4 个任务的日志
- 50 字对比：加了 thought 之后输出更可读了吗？token 消耗变了多少？

> 这是 Day3 ReAct 范式的预热。

---

## 评分标准

- 必做每题 5 分（共 15 分）
- 选做每题 5 分（加分上限 20 分）
- 反思深度 5 分

---

## 答案要点（参考）

> ⚠️ **先独立完成再看此部分**，可以拷一份到 `exercises/teacher-notes.md`。

### 2.1
- `keyword: str` 必填 / `case_sensitive: bool` 可选 / `limit: int` 可选
- 通常会忘了：description 字段必须**主动写**，inspect 推不出来
- 加分项：identifier 描述能"面向调用决策"，例如 "搜索包含某个 keyword 的文件，返回路径列表"

### 2.2
- 模型对"同类型批量任务"会自然返回多个并行 tool_call
- ThreadPoolExecutor 是最简单的并行方案；asyncio + httpx 更工业级
- 最容易翻车：**并行执行后追加 tool 消息时顺序错了**——必须按 tc.id 对应，不能按 future 完成顺序

### 2.3
- 改造前：模型常见反应是"再调一次"或"编一个数字"，几乎不会主动承认失败
- 改造后："连续 2 次同参调用"判定可以用一个 set/dict 记录 (name, json.dumps(args, sort_keys=True))
- 反思要点：**写类工具失败 = 部分写入 → 状态不一致**；**收费 API = 真金白银**；这两类必须有刹车

### 2.4
- 用 `typing.get_args(Literal["a", "b"])` 拿到取值列表
- enum 加上后，模型调错参数概率显著下降，因为 OpenAI 后端会**直接拒绝**不在 enum 里的值

### 2.5
- 改造点：system prompt 要求"先输出 1-2 句思考再调工具"
- token 消耗一般增加 20-30%
- 可读性显著上升，但**多步任务时模型容易'话痨'**——这是 Day3 ReAct 范式要专门解决的问题
