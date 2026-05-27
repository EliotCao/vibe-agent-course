# Day 1 · 实操：综合 LLM 客户端

> 80 分钟 · 实操（第 6 节，理论 5 节后的总实操）

## 前提

学生已经在前 5 节里**当堂跑过 5 个 demo**，分别看到：
- LLM 在猜下一个词（demo_01）
- 三种 system prompt 三种人格（demo_02）
- 不同语言的 tokenization + 撑爆窗口（demo_03）
- 主动诱发幻觉 + LLM 自查（demo_04）
- 加工具 / 加上下文 = 答对（demo_05）

本节把这些能力**整合成自己的小工具**：

```
01/
├── 01_llm.py          # 流式对话 REPL（包含 system prompt 切换）
├── count_tokens.py      # token 计数小工具
└── hallucination_log.md # 幻觉实验记录
```

## 时间分配

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 10min | 环境配置 + 验证连通 |
| B | 25min | Step 1：流式对话脚本 `01_llm.py` |
| C | 20min | Step 2：token 计数工具 `count_tokens.py` |
| D | 15min | Step 3：完成 `hallucination_log.md` |
| E | 10min | Q&A + Checkpoint 提交 |

---

## 阶段 A · 环境配置（10min）

### A.1 创建项目目录

```bash
mkdir 01-products
cd 01-products
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install openai python-dotenv tiktoken
```

### A.2 写 .env

```bash
# .env
BASE_URL=<老师下发>
API_KEY=<老师下发>
MODEL_ID=<老师指定>
```

> ⚠️ `.env` **绝对不能提交到 Git**。Day5 会展开讲。

### A.3 验证

```python
# ping.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
resp = client.chat.completions.create(
    model=os.getenv("MODEL_ID"),
    messages=[{"role": "user", "content": "回复一个字：好"}],
)
print(resp.choices[0].message.content)
```

跑通看到回复就算通了。

---

## 阶段 B · Step 1：流式对话 REPL（25min）

### 目标

写 `01_llm.py`，要求：

1. **多轮对话**：保留 messages 历史
2. **流式输出**：逐字打印，看到模型"思考"过程
3. **system prompt 可切换**：用 `/system <新prompt>` 命令更换
4. **看 token 消耗**：每次回答后打印本轮和累计 token
5. **退出**：`exit` / `quit` / Ctrl-C

### 让学生先 vibe（10min）

让他们打开 IDE，给 AI 这个 prompt：

```
帮我写一个 Python 脚本 01_llm.py：
- 从 .env 读取 BASE_URL / API_KEY / MODEL_ID
- 用 openai SDK 跟 LLM 对话，流式输出
- 多轮对话保留 messages
- 支持 /system <prompt> 切换 system
- 支持 /reset 清空对话（保留 system）
- 每轮回答后打印 token 消耗
- exit 退出
```

让他们先跑出来，**不完美没关系**。

### 老师投屏参考实现（10min）

老师给一份"参考代码"对照（**不要在课前发**）：

```python
# 01_llm.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))
MODEL = os.getenv("MODEL_ID")

messages = [{"role": "system", "content": "你是一个简洁的编程助手。"}]
total_tokens = 0


def stream_chat(messages):
    """流式调用并返回完整文本 + 用量"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )
    pieces = []
    usage = None
    for chunk in resp:
        if chunk.choices and chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            print(piece, end="", flush=True)
            pieces.append(piece)
        if chunk.usage:
            usage = chunk.usage
    print()
    return "".join(pieces), usage


def main():
    global total_tokens
    print(f"[Day1 LLM REPL] system: {messages[0]['content']}")
    print("命令：/system <prompt>  /reset  exit\n")

    while True:
        try:
            user = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit"):
            break

        if user.startswith("/system "):
            new_sys = user[len("/system "):]
            messages[0] = {"role": "system", "content": new_sys}
            print(f"[已切换 system] {new_sys}\n")
            continue

        if user == "/reset":
            sys_prompt = messages[0]
            messages.clear()
            messages.append(sys_prompt)
            print("[已清空历史]\n")
            continue

        messages.append({"role": "user", "content": user})
        print("AI: ", end="")
        text, usage = stream_chat(messages)
        messages.append({"role": "assistant", "content": text})

        if usage:
            total_tokens += usage.total_tokens
            print(f"[本轮 {usage.total_tokens} tokens · 累计 {total_tokens}]\n")


if __name__ == "__main__":
    main()
```

### 学生当堂改造（5min）

让学生加一个 `/save <文件名>` 命令，把当前对话存为 JSON。

---

## 阶段 C · Step 2：Token 计数工具（20min）

### 目标

写 `count_tokens.py`，能：

1. 命令行接收文件路径或字符串：`python count_tokens.py file.py` 或 `python count_tokens.py "你好"`
2. 输出：字符数、token 数、按 ¥10/1M 估算成本
3. 支持 `--show` 标志，展示前 30 个 token 切分情况

### 参考实现

```python
# count_tokens.py
import argparse
import sys
from pathlib import Path
import tiktoken

ENC = tiktoken.get_encoding("cl100k_base")
PRICE_PER_1M = 10  # ¥


def count(text: str, show_pieces: bool = False) -> None:
    n_chars = len(text)
    ids = ENC.encode(text)
    n_tokens = len(ids)
    cost = n_tokens / 1_000_000 * PRICE_PER_1M

    print(f"字符数: {n_chars:,}")
    print(f"Token 数: {n_tokens:,}")
    print(f"按 ¥{PRICE_PER_1M}/1M 估算: ¥{cost:.4f}")
    print(f"  跑 1000 次: ¥{cost*1000:.2f}")

    if show_pieces:
        print("\n前 30 个 token：")
        sample = ids[:30]
        pieces = [ENC.decode([i]) for i in sample]
        print("  " + " | ".join(repr(p) for p in pieces))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="文件路径或文本字符串")
    p.add_argument("--show", action="store_true", help="展示前 30 个 token 切分")
    args = p.parse_args()

    path = Path(args.input)
    text = path.read_text() if path.exists() else args.input
    count(text, args.show)


if __name__ == "__main__":
    main()
```

### 当堂练习

让学生统计一下**自己昨天写的某个文件**的 token 数和成本，**跟同桌对比**。

---

## 阶段 D · Step 3：幻觉实验日志（15min）

回到 `demo_04_hallucinate.py`，让学生：

1. 跑一遍 4 个内置案例
2. **自己设计 2 个新案例**：
   - 一个你认为模型一定不知道的事
   - 一个故意诱导越狱的 prompt
3. 把所有 6 个案例的回答 + 你的判断 + LLM 自查结果整理成 `hallucination_log.md`

### `hallucination_log.md` 模板

```markdown
# 幻觉实验日志

## 案例 1：（标题）

**问题**：
```
（你输入的 prompt）
```

**模型回答**：
```
（模型输出）
```

**你的判断**：
- 幻觉等级：□ 高 □ 中 □ 低 □ 无
- 编造点：（具体哪些）

**LLM 自查结果**：
（demo 跑出来的）

**反思**：
（为什么这个案例触发了幻觉，对应第 4 节哪种"触发器"）

---

## 案例 2 ...
```

---

## 阶段 E · Q&A + Checkpoint（10min）

### 提交清单

```
01-checkpoint/
├── 01_llm.py             # 流式对话 REPL
├── count_tokens.py         # token 计数工具
├── hallucination_log.md    # 6 个幻觉案例日志
└── reflection.md           # 100-200 字反思
```

### 反思要求

`reflection.md` 必须包含：
- Day1 五节里你觉得最反常识的一点
- 你跑 demo_04 时哪个案例最离谱
- 你最有把握/最没把握的概念
- 一个明天 Day2 你想看到的东西

---

## 助教检查重点

- [ ] `01_llm.py` 真的流式（逐字出现，不是整段才出）
- [ ] `count_tokens.py` 既能接文件也能接字符串
- [ ] `hallucination_log.md` 有自己设计的案例（不是只跑内置 4 个）
- [ ] reflection 不是水文，至少有一个具体观察

## 参考资产（仅老师卡住时投屏）

- `02-hello-llm/main.py` —— 流式调用最简版
- `04-my-agent/llm/llm.py` —— 工程级 LLM 客户端
