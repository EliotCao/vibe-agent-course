# 第 3 节 · Token、上下文窗口、token 怎么算

> 30 分钟 · 理论 + 当堂 demo

## 教学节奏

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 5min | 抛问题：为什么 ChatGPT 跟我聊久了会"忘"早些时候说过的话？ |
| B | 15min | 讲 token / 上下文窗口 / 跨语言差异 / 计费 |
| C | 10min | 学生跑 [`demo_03_tokens.py`](../lab/demos/demo_03_tokens.py)，亲眼看 tokenization + 触发上下文超限 |

---

## 阶段 A · 抛问题（5min）

讲两个真实场景：

> **场景 1**：你跟 ChatGPT 聊了 100 轮，问它"我第一句话说了什么"，它说"对不起我不记得了"。

> **场景 2**：你看到 OpenAI 的账单上写"$0.05 / 1K tokens"——这个 token 到底是个啥？

把这两个问题钉在屏幕上。这一节回答它们。

## 阶段 B · 讲原理（15min）

### Token：LLM 的"原子"

**Token 不是字、不是词，是子词单位**（subword）。

中英文规则差异巨大：

| 文本 | 字符数 | Token 数 | 比例 |
|------|--------|---------|------|
| `"Hello, world!"` | 13 | 4 | 1 词 ≈ 1 token |
| `"你好，世界！"` | 6 | 5-7 | 1 字 ≈ 1-1.5 token |
| `"def foo(): return 1"` | 19 | 7-9 | 标点缩进各算 |

**经验法则**：
- 英文：1 token ≈ 0.75 个单词 ≈ 4 个字符
- 中文：1 token ≈ 0.5-1 个汉字
- 代码：标点和缩进单独成 token，相对"贵"

### 为什么要在乎 token？

3 个原因：

1. **计费按 token**（不是按字符）
2. **上下文窗口按 token 算**
3. **延迟跟 token 数线性相关**

### 上下文窗口：LLM 的"工作内存"

模型一次推理能"看"到的最多 token 数，叫**上下文窗口**。

| 模型 | 上下文窗口 |
|------|-----------|
| GPT-3.5 | 16K |
| GPT-4 / GPT-4o | 128K |
| Claude 3.5 Sonnet | 200K |
| Gemini 2.0 Pro | 2M |
| Qwen2.5-Max | 128K |
| DeepSeek-V3 | 128K |

### 三个反常识

#### 反常识 1：输入 + 输出**共享**窗口

128K 上下文 ≠ 输入 128K 还能再生成几 K。是**输入 + 输出 ≤ 128K**。
所以你给模型 127K 输入，它最多生成 1K。

#### 反常识 2：超出窗口会**直接报错**

不是"自动截断老消息"。API 会返回 400 错误：

```
context_length_exceeded: This model's maximum context length is 128000 tokens.
However, your messages resulted in 134567 tokens.
```

这就是为什么你聊久了 ChatGPT "忘事"——前端**主动**帮你裁掉早期消息了，否则 API 会报错。

#### 反常识 3：越长越笨

实验表明，大部分模型在 ≥ 50% 容量后准确率断崖下降，叫 "**Lost in the Middle**" 现象——
模型对中间位置的内容关注度明显低于头尾。

> 这是 Day4 上下文工程的伏笔：**上下文管理不只是"塞得下"，还要"管得好"**。

### 钱：怎么估成本

价格（2025 年大致水平，会变）：

| 模型 | 输入 ¥/1M token | 输出 ¥/1M token |
|------|-----------------|-----------------|
| GPT-4o | ¥18 | ¥72 |
| Claude 3.5 Sonnet | ¥22 | ¥108 |
| Qwen3-Coder-Plus | ¥6 | ¥18 |
| DeepSeek-V3 | ¥1 | ¥8 |

**算一笔账**：

- 一次 Coding Agent 调用，输入 5K token + 输出 1K token
- GPT-4o：(5×0.018 + 1×0.072) = **¥0.16 一次**
- 一天 100 次：**¥16**
- 一个月：**¥480**

> 这就是为什么 Coding Agent 必须做**上下文管理**——一不小心月花费就上千。

## 阶段 C · 当堂 demo（10min）

让学生跑：

```bash
pip install tiktoken          # 第一次需要装
python demo_03_tokens.py
```

这个 demo 演示三件事：

1. **不同语言的 tokenization**：英文 / 中文 / 日文 / 代码 / emoji 各被切成什么样
2. **成本估算**：一份 README 跑 1000 次要多少钱
3. **故意撑爆窗口**：构造 100K+ token 输入看 API 怎么报错

学生看到第 3 个的时候会"哦——"地一声，因为他们终于"看见"了那个抽象的"上下文窗口"。

### 当堂练习（3min）

让每个学生跑一下：

```python
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

# 拿出你昨天写的某个 .py 文件
with open("your_file.py") as f:
    code = f.read()

print(f"字符数: {len(code)}")
print(f"Token 数: {len(enc.encode(code))}")
print(f"按 ¥10/1M 输入算，单次调用: ¥{len(enc.encode(code))/1_000_000 * 10:.4f}")
```

让他们意识到——**自己每天读的代码值多少钱**。

---

## 小结

| 关键词 | 一句话理解 |
|--------|-----------|
| Token | LLM 的最小单位，子词 |
| 上下文窗口 | 一次能"看"多少 token，输入+输出共享 |
| Lost in the Middle | 越长越笨 |
| 计费单位 | token（不是字数）|

## 下节预告

下一节：模型挺会聊的，但**它有时候会编**——这就是幻觉。怎么识别、怎么防？
