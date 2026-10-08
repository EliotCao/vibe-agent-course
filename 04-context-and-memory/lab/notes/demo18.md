# demo13 代码笔记



## >5d

这是 Python **格式化字符串迷你语言**（Format Spec Mini-Language）里的写法，专门用来控制数字/文本怎么”摆“在一段固定宽度里。拆开看：



### `>5d` 三段拆解

```text
 >    5    d
 │    │    │
 │    │    └─ 类型：d = decimal integer（十进制整数）
 │    └────── 宽度：至少占 5 个字符宽
 └─────────── 对齐：> 表示右对齐（左侧补空格）
```



### 举个具体例子

假设 `prompt_tk` 在不同轮次分别是 `87`、`1234`、`27893`：

```python
f"prompt={87:>5d} tokens"        # 输出：prompt=   87 tokens
f"prompt={1234:>5d} tokens"      # 输出：prompt= 1234 tokens
f"prompt={27893:>5d} tokens"     # 输出：prompt=27893 tokens
f"prompt={123456:>5d} tokens"    # 输出：prompt=123456 tokens   ← 超过 5 位就不截断
```

注意最后一行：**5 是"最小宽度"，不是"最大宽度"**。位数超了，原样输出，不会被砍掉。



### 为什么要这么写？

看 demo 里的实际输出：

```text
[第  1 轮] prompt=   87 tokens · total=  412 tokens · messages 字符数=63
[第  2 轮] prompt=  531 tokens · total=  889 tokens · messages 字符数=412
[第 10 轮] prompt= 4823 tokens · total= 5201 tokens · messages 字符数=3812
[第 20 轮] prompt=18472 tokens · total=18901 tokens · messages 字符数=14203
```

数字**右对齐 + 等宽**，每一行的小数点（其实是个位）都对齐在同一列，肉眼一扫就能看出“涨了几个数量级”。如果不加 `>5d`，会变成这样：

```text
[第 1 轮] prompt=87 tokens · ...
[第 2 轮] prompt=531 tokens · ...
[第 10 轮] prompt=4823 tokens · ...
```

参差不齐，对比起来眼睛要重新校准。



### 同一文件里另外两个例子

```python
        print(
            f"[第 {turn:2d} 轮] "
            f"prompt={prompt_tk:>5d} tokens · "
            f"total={total_tk:>5d} tokens · "
            f"messages 字符数={history_chars[-1]}"
        )
```

- `{turn:2d}` —— 没写对齐符号，**整数默认就是右对齐**，效果等同于 `>2d`。所以 `1` 会变成 `1`（前面补一个空格），`10` 就是 `10`，让"第 1 轮"和"第 10 轮"对齐。
- `{prompt_tk:>5d}` 和 `{total_tk:>5d}` —— 显式写了 `>`，是好习惯，不依赖默认行为。



### 顺带补充常用对齐符

| 符号 | 含义               | `f"{42:*<7d}"` | `f"{42:*>7d}"` | `f"{42:*^7d}"` |
| ---- | ------------------ | -------------- | -------------- | -------------- |
| `<`  | 左对齐             | `42*****`      | —              | —              |
| `>`  | 右对齐（数字默认） | —              | `*****42`      | —              |
| `^`  | 居中               | —              | —              | `**42***`      |

> [!NOTE]
>
> `*` 是填充字符，默认是空格；写成 `*` 只是为了让你看清楚补在哪。





## 为什么需要打开流式输出

### 1. 最直接的原因：超时

非流式（`stream=False`）的请求行为是：

```text
client ──请求──> 网关 ──> 模型推理 ────────(漫长等待)────────> 完整结果 ──> 客户端
```

整个 HTTP 连接要**一直挂着**直到模型把若干个 token 全部生成完。中间任何一个环节超时（默认很多反代是 30s/60s），连接就断了。

而流式是：

```text
client ──请求──> 网关 ──> 模型 ──chunk1──> ──chunk2──> ──chunk3──> ... ──[DONE]
```

每隔几十毫秒就有数据流回来，TCP 连接持续有活动，**任何中间层都不会判定为 idle 而 kill 连接**。

对于一个对外提供服务的网关来说，强制 stream 是最省心的做法——它不用为「某个用户问了个超长问题，模型要算 90 秒」这种场景去单独调长超时。



### 2. 资源占用模型不一样

非流式：网关需要在内存里**缓存完整响应**，然后一次性吐出。如果并发 1000 个请求，每个响应平均 2KB，那就是 2MB 常驻；如果是 long context 场景，单条响应几十 KB，内存压力指数上升。

流式：网关基本是**透明转发**，chunk 来了就转走，几乎不留内存。对网关运维来说成本低得多。



### 3. 用户体验考量（次要）

终端用户（ChatGPT/聊天产品）几乎都期望「打字机效果」，所以上游服务一开始就把 stream 作为一等公民来设计。非流式反而是个「兼容用法」，很多新接口干脆就不再实现了。



### 4. 为什么 `usage` 默认不给

这是流式协议本身的限制：流式是「边算边发」，**算到一半时根本不知道总 token 数**。所以协议设计上，`usage` 只能在「全部生成完」的最后一个特殊 chunk 里给出。这也是为什么 OpenAI 兼容 API 要专门加一个 `stream_options.include_usage=True` 开关——不是默认行为，而是显式索取。

这也解释了为什么那个 chunk 的 `choices` 是空列表：

```python
if chunk.choices:           # 内容 chunk：有 delta.content
    ...
if getattr(chunk, "usage", None):   # 收尾 chunk：只带 usage，没有 choices
    usage = chunk.usage
```

两类 chunk 是分开发的，必须两个 `if` 分开判断（不是 `elif`）。



### 5. 在 vibe-coding 场景下的启示

对你做 agent 来说，这意味着：

- **永远默认用 stream**：哪怕你不需要逐 token 渲染，也比非流式更稳。
- **统计 token 要主动开 `include_usage`**：否则你拿不到 prompt_tokens / completion_tokens，做不了上下文预算管理。
- **解析时区分两种 chunk**：内容 chunk 看 `choices[0].delta.content`，收尾 chunk 看 `usage`。





## Usage

`usage` 是模型这一次调用的「**计费/额度账单**」对象，由服务端在响应里塞回来，不是我们本地算出来的。

它有三个核心字段：

1. `usage.prompt_tokens`：这次发出去的“输入”消耗了多少 token（messages 全量）
2. `usage.completion_tokens`：这次模型"输出"消耗了多少 token（assistant 的回复）
3. `usage.total_tokens`：= prompt_tokens + completion_tokens



### 在 demo 里我们用了哪两个？

```python
        prompt_tk = usage.prompt_tokens
        total_tk = usage.total_tokens
        history_tokens.append(prompt_tk)
        history_chars.append(sum(len(m["content"]) for m in messages))
```

- **`prompt_tokens`** —— 这是 demo 18 真正想看的东西。每一轮我们都把“上一轮的 assistant 回复 + 新一句 user 追问”全量塞回 `messages` 再发一次，所以 `prompt_tokens` 会**单调上涨**。最后画的那张 ASCII 折线图，就是它在每轮的值。
- **`total_tokens`** —— 只是顺手打印出来给你直观感受“这一次调用的全开销”。



### 在流式下为什么要特别处理

非流式时 `resp.usage` 在响应对象上一拿就有：

```python
resp = client.chat.completions.create(..., stream=False)
usage = resp.usage   # 直接拿
```

但我们改成流式后，`usage` 变成"最后一个特殊 chunk"才送来：

```python
            reply_parts: list[str] = []
            usage = None
            for chunk in stream:
                # 注意：带 usage 的最后一个 chunk，choices 通常是空列表
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if getattr(delta, "content", None):
                        reply_parts.append(delta.content)
                if getattr(chunk, "usage", None):
                    usage = chunk.usage
```

所以代码里 `usage` 初始化成 `None`，遍历完所有 chunk 后才会被赋值——它代表「**这次完整请求结束后，服务器告诉我们的最终账单**」。



### 在 Agent 工程里它的用途

`usage` 不是装饰品，是后面几章会反复用到的核心信号：

| 用途           | 怎么用 `usage`                                               |
| -------------- | ------------------------------------------------------------ |
| **成本核算**   | `prompt_tokens` × 输入单价 + `completion_tokens` × 输出单价 = 这次调用花了多少钱 |
| **上下文预算** | 当 `prompt_tokens` 接近窗口的 70% 时，触发摘要/裁剪策略      |
| **观测告警**   | 单轮 `total_tokens` 异常飙升 → 多半是 history 失控、要排查   |
| **回归测试**   | 对比新旧 prompt 设计的 `prompt_tokens` 差异，看优化是否真的省了钱 |

所以 demo 18 这里把 `prompt_tokens` 攒成一个 list 画出来，本质就是在让你**提前感受"上下文预算"这个概念**——下一节开始要做的摘要、滑窗、外部记忆，都是为了把这条曲线压平。



## chunk

`chunk` 是**服务器通过 SSE（Server-Sent Events）协议陆陆续续推回来的“一小块响应”**，每一块都是一个结构和非流式 response 几乎一样的对象，只是里面的内容是“增量”，不是“全量”。



### 直观对比：非流式 vs 流式

**非流式**：服务器算完了，一次性给你一个**完整对象**：

```python
resp = client.chat.completions.create(..., stream=False)
# resp 长这样（一个对象）：
# ChatCompletion(
#     id="chatcmpl-xxx",
#     choices=[Choice(message=ChatCompletionMessage(content="北京 7 日游建议如下：第一天..."))],
#     usage=CompletionUsage(prompt_tokens=87, completion_tokens=325, total_tokens=412)
# )
```



**流式**：服务器算一点发一点，你拿到的是一**串**对象：

```python
stream = client.chat.completions.create(..., stream=True)
# stream 是个迭代器，迭代出来一连串 ChatCompletionChunk：
# 
# chunk 1: ChatCompletionChunk(choices=[Choice(delta=ChoiceDelta(role="assistant"))])         # 开场白
# chunk 2: ChatCompletionChunk(choices=[Choice(delta=ChoiceDelta(content="北京"))])           
# chunk 3: ChatCompletionChunk(choices=[Choice(delta=ChoiceDelta(content=" 7 日"))])          
# chunk 4: ChatCompletionChunk(choices=[Choice(delta=ChoiceDelta(content="游"))])             
# ...                                                                                          
# chunk N: ChatCompletionChunk(choices=[Choice(delta=ChoiceDelta(), finish_reason="stop")])   # 收尾
# chunk N+1: ChatCompletionChunk(choices=[], usage=CompletionUsage(...))                       # 账单
```

把它们的 `delta.content` 拼起来，就还原出了完整回复。



### 关键差异：`message` vs `delta`

这是流式最容易让人迷糊的地方：

| 非流式                             | 流式                             |
| ---------------------------------- | -------------------------------- |
| `chunk.choices[0].message.content` | `chunk.choices[0].delta.content` |
| 整段完整内容                       | 只是这一片增量                   |

字段名都不一样，`message` → `delta`，**delta 就是“差量”的意思**——这一 chunk 比上一 chunk 多出了哪些字符。

所以 demo 里这一段的本质是「**把所有增量拼回成完整字符串**」：

```python
            reply_parts: list[str] = []
            usage = None
            for chunk in stream:
                # 注意：带 usage 的最后一个 chunk，choices 通常是空列表
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if getattr(delta, "content", None):
                        reply_parts.append(delta.content)
```

`reply_parts` 收集每一片 `delta.content`，最后 `"".join(reply_parts)` 还原全文，效果等同于非流式的 `resp.choices[0].message.content`。



### chunk 的几种“形态”

实际跑下来，一次完整流大概会出现这 4 种 chunk：

#### 1. 角色 chunk（开场，1 个）

```bash
ChatCompletionChunk(
    choices=[Choice(
        index=0,
        delta=ChoiceDelta(role="assistant", content=None),  # 只是宣告"接下来轮到 assistant 说话"
        finish_reason=None
    )],
    usage=None
)
```

#### 2. 内容 chunk（中间一大堆）

```python
ChatCompletionChunk(
    choices=[Choice(
        index=0,
        delta=ChoiceDelta(content="北京"),  # ← 这就是我们要的增量
        finish_reason=None
    )],
    usage=None
)
```

#### 3. 结束信号 chunk（1 个）

```python
ChatCompletionChunk(
    choices=[Choice(
        index=0,
        delta=ChoiceDelta(),  # 空 delta
        finish_reason="stop"  # ← 告诉你"模型说完了"，原因可能是 stop / length / tool_calls
    )],
    usage=None
)
```

#### 4. 账单 chunk（仅当 `include_usage=True` 时，1 个）

```python
ChatCompletionChunk(
    choices=[],  # ← 空列表！这就是为什么我们必须 if chunk.choices: 守卫
    usage=CompletionUsage(prompt_tokens=87, completion_tokens=325, total_tokens=412)
)
```



### 你可以做的常见处理

| 需求               | 怎么写                                                       |
| ------------------ | ------------------------------------------------------------ |
| 打字机效果实时输出 | `print(delta.content, end="", flush=True)`                   |
| 拼成完整字符串     | demo 里这样：`reply_parts.append(delta.content); "".join(reply_parts)` |
| 拿 token 用量      | 必须 `stream_options={"include_usage": True}`，再读最后一 chunk 的 `usage` |
| 检测模型为啥停了   | 看哪个 chunk 的 `finish_reason`（stop=正常 / length=被 max_tokens 截断 / tool_calls=要调工具） |
| 处理 tool calls    | `delta.tool_calls`（增量也是分块的，要自己拼 function name + arguments） |

> [!TIP]
>
> 后面 05/06 章做 coding agent 时，**`finish_reason` 和 `tool_calls` 的增量拼接**会是必修课——那时候 chunk 处理就不只是拼字符串这么简单了，是要边读流边决定"模型现在是要继续写文字、还是要调工具"。



# enumerate

Python 内置函数 `enumerate`，用来在遍历可迭代对象时**同时拿到「索引」和「元素」**。函数签名如下：

```python
enumerate(iterable, start=0)
```

- `iterable`：要遍历的对象（list、tuple、生成器等）
- `start`：控制的是 `enumerate` 返回的**计数器（counter）从几开始**，跟列表自己的「索引（index）」没有关系。

> [!NOTE]
>
> 「索引」在 Python 里有特定含义 —— 就是 `list[0]`、`list[1]` 这个 `0`、`1`，由列表自己决定，永远从 0 开始，**任何外部函数都改不了它**。`enumerate` 只是顺序遍历列表，顺手给你发一个编号而已，这个编号叫**计数器**更合适。