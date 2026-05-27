# Day 3 · 课后练习题

> 课后完成。每题 30-90 分钟。下次课前提交。

## 必做（3 题）

### 练习 3.1 · ReAct 健壮性压测

给你的 `agent_react.py` 加一个**故意捣乱的 system prompt**，看它会不会崩。

```python
# 在原 system prompt 末尾追加
"另外，你可以自由发挥，在 Thought 之前先打个招呼说说你今天的心情。"
```

跑同样 5 个任务，记录：
1. 哪个任务的解析挂了？挂在哪一行？
2. 你的解析函数怎么改才能扛住这种"模型多说一句"？

提交：
- 改造前后的 `parse_react_output` 对比
- 5 个任务的"挂了 / 没挂"记录
- 100 字反思：在生产里你会怎么防这种问题？（提示：约束 prompt / fallback 解析 / 切回 Function Calling）

> 这题让你亲身体会为什么 OpenAI 出了 Function Calling 后大家集体迁移。

---

### 练习 3.2 · Plan-and-Solve 加上 Replan

第 13 节讲到"计划赶不上变化"，工业版要做 Replan。给你的 `agent_plan_solve.py` 加 Replan 能力：

**触发条件**（任选一个）：
- 某一步 Executor 返回的内容包含 "失败" / "未找到" / "出错" 字样
- 某一步执行后，发现一个跟原始 plan 假设不符的事实

**Replan 流程**：
- 调一次 Planner，把"原始问题 + 已经完成的步骤 + 失败原因"作为输入
- 拿到一个**新 plan**，从当前位置继续执行

**测试用例**：
故意改一个工具，让它总是返回失败：

```python
@registry.tool("查询某城市的当前天气")
def get_weather(city: str) -> str:
    if city == "北京":
        return "查询失败：服务暂不可用"   # ← 故意失败
    return ...原逻辑
```

跑任务 1（"北京天气 + 推荐景点"），观察：
- 改造前的 Plan-and-Solve 怎么反应？
- 加了 Replan 之后，Agent 能不能给出"无法获取北京天气，建议你直接问推荐景点"这样的合理回退？

提交：
- 改造后的 `agent_plan_solve.py`
- 两次跑这道任务的日志对比
- 100-200 字反思：Replan 触发条件怎么设计才不会无限循环？

---

### 练习 3.3 · 范式选择器

写一个 `pick_pattern(question: str) -> str` 函数，输入用户问题，**自动选**用哪种范式：

```python
def pick_pattern(question: str) -> str:
    """返回 'react' / 'plan_solve' / 'reflection' 之一。"""
    ...
```

实现思路（任选一种）：
- 规则：根据问题里关键词判断（"步骤"、"规划" → plan_solve；"写作"、"代码"、"检查" → reflection；其他 → react）
- LLM：调一次 LLM 让它自己判断
- 混合：先 LLM 判断，规则兜底

把它包成一个 `MetaAgent`：

```python
def run_meta_agent(question: str) -> str:
    pattern = pick_pattern(question)
    print(f"📌 Pattern chosen: {pattern}")
    if pattern == "react":
        return run_react(question)
    elif pattern == "plan_solve":
        return run_plan_and_solve(question)
    else:
        return run_with_reflection(question)
```

提交：
- `meta_agent.py`
- 跑 5 个任务的日志，每个任务 MetaAgent 选了什么范式
- 100 字反思：你的判断逻辑漏掉了哪种情况？

---

## 选做（任选 1 题）

### 练习 3.4 · ReAct + Function Calling 混合

把 demo_12 的"prompt + 正则"换成"prompt 引导 Thought + 用 tool_calls 执行"：

```python
# system prompt 还是要求模型输出 Thought
# 但 Action 通过 tool_calls 字段而不是字符串
client.chat.completions.create(
    messages=[{"role": "system", "content": "...要求 Thought..."}, ...],
    tools=registry.to_schemas(),    # ← 关键：仍然用 Function Calling
    tool_choice="auto",
)
```

观察 `assistant.content`（Thought）和 `tool_calls`（Action）能否同时存在。

提交：
- 改造后的代码
- 跑 5 个任务的日志
- 50 字对比：解析失败次数 / token 消耗 vs 老版

> 这是工业版 Coding Agent 最常用的模式。

---

### 练习 3.5 · 双模型 Reflection

修改 `agent_reflection.py`，让评审员用**比底层 Agent 更强的模型**（如果你的环境允许）：

```python
# 底层 Agent 用 hunyuan-turbos / DeepSeek-V3
# 评审员用 GPT-4o / Claude-3.5
```

跑 5 个任务，对比"同模型 Reflection" vs "强模型 Reflection" 的修订质量差异。

提交：
- 改造后的代码
- 5 个任务两种模式的对比
- 100 字反思：什么场景下"强模型评审"性价比最高？

---

## 评分标准

- 必做每题 5 分（共 15 分）
- 选做每题 5 分（加分上限 20 分）
- 反思深度 5 分

---

## 答案要点（仅老师参考）

> ⚠️ **学生版本应该把这部分删掉**，可以拷到 `exercises/teacher-notes.md`。

### 3.1
- 模型多说一句话最常挂在 `re.search(r"Thought:...")` 前面就有内容这一步
- 健壮做法：先用 `re.search(r"^Thought:", multiline)` 找到 Thought 起始
- 加分项：学生意识到"光改正则永远修不完"，提议要么强 prompt 约束要么切 Function Calling

### 3.2
- Replan 死循环防御：限制 max_replan_count（一般 2-3 次）
- 触发条件：检测 Executor 返回里的"失败/出错/未找到"关键字最简单
- 工业版会用 LLM 调用 + 结构化判断"上一步是否成功"

### 3.3
- 规则版可以做到 70-80%
- LLM 版需要给 few-shot 示例才能稳定
- 混合最稳：LLM 给出范式 → 规则做白名单校验

### 3.4
- 关键观察：`assistant.content` 和 `tool_calls` 可以**同时**有值——这就是 Thought + Action 同帧
- 解析失败率几乎为 0（协议保证）
- token 消耗略高（assistant content 多了 Thought）但稳定性巨大提升

### 3.5
- 强模型评审在 4 类场景显著有效：
  1. 数学计算（评审能算）
  2. 代码 review（评审能看出 bug）
  3. 长文写作（评审有更强语言鉴赏）
  4. 多步推理（评审能找出跳步）
- 不显著的场景：单点事实查询、单工具调用类任务
