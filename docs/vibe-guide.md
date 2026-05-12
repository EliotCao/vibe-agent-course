# 用 CodeBuddy Vibe 出一个 AI Agent —— 逐步教学指南

> 本指南带你从零开始，通过与 CodeBuddy 对话，逐步 vibe 出一个基于 **Thought-Action-Observation** 循环的智能旅行助手。
>
> 每一步都会先解释**为什么要这样做**，再给出对应的提示词。

---

## 前置准备

- 一个 CNB 平台的代码仓库（已自动注入 `CNB_API_ENDPOINT`、`CNB_REPO_SLUG`、`CNB_TOKEN` 环境变量）
- 在仓库中打开 CodeBuddy

---

## Step 1：搭建项目骨架

### 你需要理解的

任何 Python 项目都需要一个清晰的结构。我们要构建一个智能体，它由以下几个部分组成：

- **配置管理**：API 地址、密钥等不能写死在代码里，应该从环境变量读取
- **LLM 客户端**：负责与大语言模型通信
- **工具（Tools）**：智能体可以调用的外部能力（如查天气）
- **提示词（Prompt）**：告诉 LLM 它是谁、能做什么、该怎么输出
- **主循环（Agent Loop）**：驱动整个 Thought-Action-Observation 循环
- **入口文件**：把以上所有部分串起来运行

在 CNB 平台上，LLM API 的地址和密钥通过环境变量注入：
- 地址：`${CNB_API_ENDPOINT}/${CNB_REPO_SLUG}/-/ai/`
- 密钥：`${CNB_TOKEN}`

### 提示词

```
帮我创建一个 Python 项目，实现一个智能旅行助手，要求：

1. 符合 Python 项目标准结构，使用 pyproject.toml 管理依赖
2. 项目分为以下模块：
   - config.py：配置管理，从环境变量读取
   - llm.py：LLM 客户端，兼容 OpenAI 接口
   - tools.py：工具模块，包含天气查询工具（使用 wttr.in 免费 API）
   - prompt.py：系统提示词
   - agent.py：智能体核心循环
   - main.py：入口文件
3. LLM 的 baseUrl 和 apiKey 需要做成可配置的，默认从环境变量拼接：
   baseUrl = "${CNB_API_ENDPOINT}/${CNB_REPO_SLUG}/-/ai/"
   apiKey = "${CNB_TOKEN}"
4. 模型使用 "hunyuan-turbos-latest"
```

### 这一步之后你会得到

一个完整的项目目录结构，所有模块各司其职，但智能体还只是个空壳——它能调用 LLM，但还不知道该怎么"思考"。

---

## Step 2：实现智能体的"大脑"—— System Prompt

### 你需要理解的

智能体的核心行为由 **System Prompt**（系统提示词）决定。它就像给智能体的一份"工作手册"，需要告诉它：

1. **你是谁**：你是一个智能旅行助手
2. **你有什么工具**：列出每个工具的名称、参数和用途
3. **你该怎么输出**：必须严格遵循 `Thought → Action` 的格式
4. **什么时候结束**：收集够信息后用 `Finish[答案]` 结束

这就是 **Prompt Engineering** 的核心——用自然语言"编程"LLM 的行为。

### 提示词

```
帮我完善 prompt.py 中的系统提示词。要求智能体：

1. 每次回复严格输出一对 Thought 和 Action
2. Action 格式为 function_name(arg_name="arg_value") 或 Finish[最终答案]
3. 可用工具包括：
   - get_weather(city: str)：查询城市实时天气
   - get_attraction(city: str, weather: str)：根据城市和天气推荐景点
4. 每次只输出一对 Thought-Action，不要多输出
```

### 这一步之后你会得到

智能体有了"工作手册"，它知道自己该怎么思考、怎么调用工具、怎么结束任务。

---

## Step 3：实现工具——智能体的"手脚"

### 你需要理解的

LLM 本身只能生成文本，它无法真正查天气、搜景点。**工具（Tools）** 就是智能体伸向真实世界的"手脚"。

智能体的工作方式是：
1. LLM 输出 `Action: get_weather(city="北京")` 这样的文本
2. 我们的代码解析这段文本，提取出工具名和参数
3. 调用对应的 Python 函数，拿到真实结果
4. 把结果作为 `Observation` 反馈给 LLM

所以每个工具本质上就是一个普通的 Python 函数，接收参数，返回字符串结果。

### 提示词

```
帮我完善 tools.py：

1. get_weather 工具：调用 wttr.in 的免费 API（https://wttr.in/{city}?format=j1），
   提取当前天气描述和气温，返回自然语言描述
2. get_attraction 工具：使用 Tavily Search API 搜索景点推荐，
   需要从环境变量读取 TAVILY_API_KEY，未配置时返回友好的错误提示
3. 把所有工具注册到一个字典 AVAILABLE_TOOLS 中，方便主循环调用
```

### 这一步之后你会得到

两个可以独立调用的工具函数。你可以直接在终端测试：`python3 -c "from hello_agent.tools import get_weather; print(get_weather('北京'))"`

---

## Step 4：实现核心循环——让智能体"动起来"

### 你需要理解的

这是整个智能体最关键的部分——**Agent Loop（智能体循环）**。它的工作流程是：

```
用户提问 → LLM 思考(Thought) → 输出行动(Action)
                                      ↓
                              解析 Action 并执行
                                      ↓
                              获得观察结果(Observation)
                                      ↓
                           把 Observation 追加到历史 → 回到 LLM 思考
                                      ↓
                           直到 Action = Finish[答案]
```

关键设计点：
- **Prompt 累积**：每轮的 LLM 输出和 Observation 都追加到历史中，这样 LLM 能看到完整的上下文
- **正则解析**：用正则表达式从 LLM 输出中提取 Action，再解析出工具名和参数
- **最大轮次**：设置上限（如 5 轮），防止智能体陷入死循环
- **截断处理**：LLM 有时会一次输出多对 Thought-Action，需要只保留第一对

### 提示词

```
帮我完善 agent.py，实现智能体的主循环：

1. 维护一个 prompt_history 列表，记录完整的对话历史
2. 每轮循环：拼接历史 → 调 LLM → 解析 Action → 执行工具 → 记录 Observation
3. 用正则解析 Action，支持两种格式：
   - 工具调用：function_name(arg_name="arg_value")
   - 结束：Finish[最终答案]
4. 最大循环 5 次
5. 如果 LLM 输出了多对 Thought-Action，只保留第一对
```

### 这一步之后你会得到

一个完整的、可运行的智能体。它能接收用户问题，通过多轮循环调用工具，最终给出答案。

---

## Step 5：运行验证

### 你需要理解的

现在所有模块都就绪了，`main.py` 负责把它们串起来：读配置 → 创建 LLM 客户端 → 设定用户问题 → 启动智能体循环。

运行后你应该能看到类似这样的输出：

```
--- 循环 1 ---
Thought: 首先需要查询北京的天气...
Action: get_weather(city="北京")
Observation: 北京当前天气:Sunny，气温32摄氏度

--- 循环 2 ---
Thought: 天气是晴天，接下来推荐景点...
Action: get_attraction(city="北京", weather="Sunny")
Observation: ...

--- 循环 3 ---
Thought: 已经收集够信息了...
Action: Finish[今天北京天气晴朗...]
```

这就是一个完整的 **Thought-Action-Observation** 循环。

### 提示词

```
帮我安装依赖并运行一下项目，验证智能体是否能正常工作
```

---

## Step 6：添加新工具——扩展智能体能力

### 你需要理解的

智能体的能力边界由它拥有的**工具**决定。想让它做更多事？给它更多工具就行。

添加一个新工具只需要三步：
1. 写一个 Python 函数（工具实现）
2. 注册到 `AVAILABLE_TOOLS` 字典
3. 在 System Prompt 中告诉 LLM 有这个新工具

这就是 Agent 架构的优雅之处——**扩展能力不需要改核心逻辑，只需要"插入"新工具**。

### 提示词

```
我想给智能体新增一个美食推荐工具：
1. 在 tools.py 中添加 get_food(city: str, weather: str) 工具
2. 在 prompt.py 中更新系统提示词，加入这个新工具的描述
3. 修改 main.py 中的用户提问为："帮我查下北京天气，然后推荐景点和美食"
```

### 这一步之后你会得到

智能体学会了一个新技能。观察它的循环输出，你会看到它自主决定在什么时候调用新工具。

---

## Step 7：改造为交互式对话

### 你需要理解的

目前智能体只能处理一个写死的问题就退出了。真正有用的智能体应该能**持续对话**。

改造的核心是：
- 用 `while` 循环持续读取用户输入
- 每次输入启动一轮 Agent Loop
- 支持退出指令（如 `quit`）

### 提示词

```
把智能体改成交互式模式：
- 在终端持续等待用户输入
- 每次输入触发一轮完整的 Agent Loop
- 输入 quit 或 exit 时退出
- 每轮对话独立，不保留上一轮的工具调用历史
```

---

## Step 8：添加流式输出

### 你需要理解的

目前 LLM 的回答是等全部生成完才一次性返回。**流式输出**可以让文字像打字一样逐字显示，大幅提升用户体验。

OpenAI 兼容接口支持 `stream=True` 参数，返回的不再是完整响应，而是一个逐块（chunk）产生内容的迭代器。

### 提示词

```
帮我给 LLM 客户端添加流式输出支持：
- 在 llm.py 中新增 stream_generate 方法，使用 stream=True
- 智能体最终的 Finish 回答使用流式输出逐字显示
- 中间的 Thought 和工具调用过程保持原样
```

---

## 总结

通过以上 8 步，你从零构建了一个完整的 AI 智能体：

| 步骤 | 你做了什么 | 核心概念 |
|------|-----------|---------|
| Step 1 | 搭项目骨架 | Python 项目结构、配置管理 |
| Step 2 | 写 System Prompt | Prompt Engineering、角色设定 |
| Step 3 | 实现工具函数 | Tools = 智能体连接真实世界的桥梁 |
| Step 4 | 实现 Agent Loop | Thought-Action-Observation 循环 |
| Step 5 | 运行验证 | 端到端验证、问题排查 |
| Step 6 | 添加新工具 | 智能体的可扩展性 |
| Step 7 | 交互式对话 | 用户体验、循环控制 |
| Step 8 | 流式输出 | Stream API、实时响应 |

核心思路：**一个智能体 = LLM（大脑） + Tools（手脚） + Prompt（工作手册） + Loop（驱动循环）**。

理解了这四个要素，你就掌握了构建任何 AI Agent 的基本方法。
