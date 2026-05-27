# Agent 范式设计文档

## 概述

`agent.py` 实现了两种经典的 Agent 范式：

| 范式 | 核心思想 | 适用场景 |
|------|----------|----------|
| **SimpleAgent** | 对话 + 可选工具调用 | 通用对话、简单工具辅助 |
| **ReActAgent** | Thought → Action → Observation 循环 | 需要多步推理的复杂问题 |

## 类继承结构

```
Agent (ABC)           抽象基类
├── name              Agent 名称
├── llm               LLM 实例
├── system_prompt     系统提示
├── tools             ToolRegistry 实例
├── history           对话历史
└── run(input) → str  核心方法（子类实现）
     │
     ├── SimpleAgent       单轮/多轮 + 工具
     └── ReActAgent        推理-行动循环
```

## SimpleAgent

### 工作流程

```
用户输入
   ↓
构建 messages（system + history + user）
   ↓
LLM 推理
   ↓
┌─ 无 [TOOL_CALL] 标记 → 直接返回回答
│
└─ 有 [TOOL_CALL] 标记 → 解析并执行工具
                            ↓
                   结果注入 messages
                            ↓
                   再次调用 LLM → 生成最终回答
                   （循环最多 max_iterations 次）
```

### 工具调用协议

LLM 通过特殊标记触发工具：

```
[TOOL_CALL:工具名:参数名=值]
```

示例：`[TOOL_CALL:get_weather:city=北京]`

### 使用示例

```python
agent = SimpleAgent(
    name="助手",
    llm=LLM(),
    system_prompt="你是一个天气助手",
    tools=registry,
)
answer = agent.run("北京天气怎么样？")
```

## ReActAgent

### 工作流程

```
Question 输入
   ↓
┌────────────────────────────────────┐
│  Step Loop (最多 max_steps 次)      │
│                                     │
│  1. 构建 prompt (tools + Q + history)│
│  2. LLM → Thought + Action          │
│     ├─ Finish[答案] → 返回          │
│     └─ tool[input] → 执行工具       │
│  3. 获取 Observation                 │
│  4. 追加到 history → 回到 1          │
└────────────────────────────────────┘
```

### LLM 输出格式

```
Thought: 我需要计算这个表达式的值
Action: calculate[15 + 27]
```

终止信号：
```
Thought: 我已经得到了答案
Action: Finish[126]
```

### 使用示例

```python
agent = ReActAgent(
    name="推理助手",
    llm=LLM(),
    tools=registry,
    max_steps=5,
)
answer = agent.run("计算 (15 + 27) * 3 等于多少？")
```

## 两种范式对比

| 维度 | SimpleAgent | ReActAgent |
|------|-------------|------------|
| 推理方式 | 隐式（LLM 内部决策） | 显式（Thought 输出推理过程） |
| 工具调用 | 嵌入回复中 `[TOOL_CALL:...]` | 独立 `Action: tool[input]` |
| 终止条件 | 回复中无工具标记 | 输出 `Finish[答案]` |
| 可观测性 | 低（只看到最终回答） | 高（每步思考过程可见） |
| 复杂度 | 简单 | 中等 |
| 适用场景 | 直接问答、单工具辅助 | 多步计算、信息聚合、复杂推理 |

## 架构位置

```
04-my-agent/
├── llm.py              # LLM 客户端
├── context_builder.py  # 上下文构建器
├── tools.py            # 工具系统
├── agent.py            # ← Agent 范式（本模块）
├── main.py             # 入口 & 示例
└── docs/
    ├── llm.md
    ├── context_builder.md
    ├── tools.md
    └── agent.md        # ← 本文档
```

## 后续扩展方向

| 方向 | 说明 |
|------|------|
| PlanAgent | 先规划步骤再逐步执行，适合长任务 |
| 多 Agent 协作 | 主 Agent 分派子任务给专用 Agent |
| 流式 ReAct | 每步 Thought/Action 流式输出，提升交互体验 |
| 记忆集成 | 与 ContextBuilder 结合，自动管理长对话记忆 |
| Function Calling | 替代文本标记解析，使用 OpenAI 原生 tool_calls |
