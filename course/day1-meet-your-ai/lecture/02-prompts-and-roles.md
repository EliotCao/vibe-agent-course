# 第 2 节 · 提示词与角色：System / User / Assistant

> 30 分钟 · 理论 + 当堂 demo

## 教学节奏

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 5min | 抛问题：为什么同一个模型有时候像 ChatGPT，有时候像猫娘？ |
| B | 15min | 讲三种角色 + messages 协议 |
| C | 10min | 学生跑 [`demo_02_roles.py`](../lab/demos/demo_02_roles.py)，体感 system prompt 的威力 |

---

## 阶段 A · 抛问题（5min）

老师投屏现场敲：

```python
# 第一次
client.chat.completions.create(
    messages=[{"role": "user", "content": "你是谁？"}]
)
# 输出：我是 ChatGPT，由 OpenAI 训练...
```

```python
# 第二次
client.chat.completions.create(
    messages=[
        {"role": "system", "content": "你是一只猫娘，每句话以喵结尾"},
        {"role": "user", "content": "你是谁？"}
    ]
)
# 输出：我是一只可爱的猫娘喵～
```

> **同一个模型，加一行 system 就成了完全不同的"人"。这是怎么做到的？**

## 阶段 B · 讲三种角色（15min）

### messages 协议

OpenAI 兼容接口都用统一的 messages 协议：

```python
messages = [
    {"role": "system",    "content": "你是一个简洁的助手。"},
    {"role": "user",      "content": "什么是递归？"},
    {"role": "assistant", "content": "函数调用自身解决子问题。"},
    {"role": "user",      "content": "举个例子。"},
]
```

每条消息有 `role` 和 `content` 两个字段。模型每次都看完**整个列表**再生成下一条。

### 三种角色的作用

| 角色 | 作用 | 谁来写 | 类比 |
|------|------|--------|------|
| `system` | 定义 AI 的人设、规则、约束 | 开发者 | 给员工写岗位说明书 |
| `user` | 用户的输入 | 用户 | 客户提问 |
| `assistant` | AI 的历史回复 | AI 自己（也可由开发者伪造作为示例）| 员工的过往答复记录 |

> Day2 还会引入第 4 个角色 `tool`（工具结果），先不讲。

### 关键认知 1：模型本身**没有记忆**

每次调用都是一次"零开始"，整个 messages 列表必须**全量传**。

```
第 1 轮:                     第 2 轮:
[system, user₁]              [system, user₁, assistant₁, user₂]
       ↓                            ↓
   assistant₁                   assistant₂
```

**所谓"AI 记得我们刚才聊过什么" = 你把历史 messages 传回去了。**

这是个朴素但震撼的认知。学生听到这里通常会"啊？"

### 关键认知 2：system prompt 是"最便宜的人格定制"

为什么 system prompt 能改变行为？

因为模型在训练时见过的"对话数据"里，**system prompt 一直被作为"主导信号"对待**。模型学会了"看到 system 就把它当成自己的角色定义"。

这是**训练阶段的约定**，不是模型自带的魔法。

### 关键认知 3：assistant 角色可以伪造（few-shot）

```python
messages = [
    {"role": "system", "content": "把每个英文单词翻译成中文，只输出中文。"},
    {"role": "user",      "content": "apple"},
    {"role": "assistant", "content": "苹果"},   # ← 伪造的"历史"
    {"role": "user",      "content": "banana"},
    {"role": "assistant", "content": "香蕉"},   # ← 伪造的"历史"
    {"role": "user",      "content": "cherry"},
]
```

模型会照葫芦画瓢，输出"樱桃"。**这就是 few-shot prompting**。

> 模型不知道 assistant 是真历史还是你伪造的，只看模式。

## 阶段 C · 当堂 demo（10min）

让学生跑：

```bash
python demo_02_roles.py
```

这个 demo 同一个 user 问题（"什么是递归？"），挂三种 system：

1. 严谨学者
2. 5 岁小朋友的语言
3. 只能用 emoji

**学生看到一样的问题给出完全不同的输出**——直观感受 system prompt 的威力。

### 当堂改造练习（5min）

让学生在 demo 文件里**自己加一个 system prompt**，比如：

- "你是鲁迅，回答带有鲁迅风格"
- "你是一个总是反问的人，从不直接回答"
- "你是一个程序员，只能用代码块回答"

跑一下看效果。

---

## 小结

| 关键词 | 一句话理解 |
|--------|-----------|
| messages 协议 | LLM 的"输入格式"，3 种角色 |
| system | 定义人格 / 规则 |
| user | 用户输入 |
| assistant | AI 历史回复（可伪造做 few-shot）|
| 模型无状态 | 每次都全量传历史 |

## 下节预告

下一节：聊了这么久，**这堆消息到底要花多少钱**？token 怎么算？
