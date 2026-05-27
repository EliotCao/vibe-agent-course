# 第 3 节 · Token、上下文窗口与成本

## 什么是 Token

![Token 不是字也不是词，而是介于两者之间的子词单位](./images/03-tokenization.png)

**Token 不是字、不是词，是介于两者之间的"子词单位"（subword）。**

LLM 不直接处理字符串——它先把文本切成 token 序列，再对每个 token 做概率预测。你可以把 token 理解为模型世界里的"原子"。

### 不同语言的 Token 差异

| 文本 | 字符数 | Token 数 | 规律 |
|------|--------|---------|------|
| `"Hello, world!"` | 13 | 4 | 英文 1 词 ≈ 1 token |
| `"你好，世界！"` | 6 | 5-7 | 中文 1 字 ≈ 1-1.5 token |
| `"def foo(): return 1"` | 19 | 7-9 | 代码的标点缩进各算 token |
| `"🤖 AI"` | 4 | 3 | emoji 通常是 1-2 token |

**经验法则**：
- 英文：1 token ≈ 4 个字符 ≈ 0.75 个单词
- 中文：1 token ≈ 0.5-1 个汉字
- 代码：标点和缩进单独成 token，所以代码相对"贵"

### 如何查看 Token 切分

可以用 OpenAI 的 `tiktoken` 库来查看任意文本被切成了什么 token：

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
text = "你好，世界！"

tokens = enc.encode(text)
pieces = [enc.decode([t]) for t in tokens]

print(f"Token 数: {len(tokens)}")
print(f"切分结果: {pieces}")
# → ['你', '好', '，', '世界', '！']
```

运行 `demo_03_tokens.py` 可以看到更多语言的切分对比。

## 为什么要在乎 Token

三个原因：

### 1. 计费按 Token

LLM API 的定价单位是 token，不是字符。典型价格（2025 年水平）：

| 模型 | 输入 ¥/1M token | 输出 ¥/1M token |
|------|-----------------|-----------------|
| GPT-4o | ¥18 | ¥72 |
| Claude 3.5 Sonnet | ¥22 | ¥108 |
| DeepSeek-V3 | ¥1 | ¥8 |
| 混元 Turbo S | 免费/极低 | 免费/极低 |

**算一笔账**：一次典型的 Coding Agent 调用（输入 5K + 输出 1K token），用 GPT-4o 大约 ¥0.16。一天跑 100 次 = ¥16，一个月 = ¥480。

这就是为什么做 Agent 必须关注**上下文管理**——不是什么都往里塞。

### 2. 上下文窗口按 Token 算

### 3. 生成延迟跟 Token 数线性相关

输出越多 token，等待时间越长（每个 token 都要算一次前向传播）。

## 上下文窗口：LLM 的"工作内存"

![输入和输出共享同一个上下文窗口，加起来不能超出容量](./images/03-context-window.png)

模型一次推理能"看"到的最大 token 数，叫**上下文窗口（context window）**。

| 模型 | 上下文窗口 |
|------|-----------|
| GPT-3.5 | 16K |
| GPT-4o | 128K |
| Claude 3.5 Sonnet | 200K |
| Gemini 2.0 Pro | 2M |
| DeepSeek-V3 | 128K |

### 三个容易搞错的点

#### 1. 输入 + 输出共享窗口

128K 上下文 ≠ 输入 128K 还能再写。是 **输入 + 输出 ≤ 128K**。

如果你给模型 127K 的输入，它最多只能生成 1K 的回复。

#### 2. 超出窗口 = 直接报错

API 不会"自动截断"，而是返回错误：

```
context_length_exceeded: This model's maximum context length is 128000 tokens.
However, your messages resulted in 134567 tokens.
```

ChatGPT 之所以聊久了会"忘事"，是因为前端**主动裁掉了早期消息**来避免超限——模型本身不会自动处理。

#### 3. 越长越笨（Lost in the Middle）

![长上下文里中间最容易被忽略，注意力呈 U 形曲线](./images/03-lost-in-middle.png)

研究表明，大部分模型在上下文超过 50% 容量后，对**中间位置**的内容关注度显著下降。

也就是说，把关键信息放在一长段文本的正中间，模型很可能会忽略它。这被称为 **"Lost in the Middle"** 现象。

> 这意味着上下文管理不只是"塞得下"的问题，还要考虑"放在哪里模型能注意到"。

## 成本估算实例

```python
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

# 假设你要让 LLM 审查一个 500 行的 Python 文件
with open("my_code.py") as f:
    code = f.read()

n_tokens = len(enc.encode(code))
cost_per_call = n_tokens / 1_000_000 * 18  # GPT-4o 输入价格

print(f"文件: {len(code)} 字符 → {n_tokens} token")
print(f"单次审查输入成本: ¥{cost_per_call:.4f}")
print(f"每天审查 50 个文件: ¥{cost_per_call * 50:.2f}")
```

## 动手试试

运行 `demo_03_tokens.py` 会演示三件事：

1. **不同语言的 tokenization 对比**：英文、中文、日文、代码、emoji
2. **成本估算**：一份文档跑多少次要多少钱
3. **故意撑爆上下文窗口**：构造超长输入，看 API 怎么报错

## 小结

| 概念 | 一句话理解 |
|------|-----------|
| Token | LLM 的最小处理单位（子词） |
| 上下文窗口 | 一次推理能看多少 token，输入+输出共享 |
| Lost in the Middle | 长上下文的中间位置容易被忽略 |
| 计费单位 | 按 token 计费，不是按字符 |
| 经验法则 | 中文 1 字 ≈ 1-1.5 token，英文 1 词 ≈ 1 token |

---

下一节：模型挺能聊的，但**它有时候会编**——这就是幻觉。为什么会发生？怎么防？
