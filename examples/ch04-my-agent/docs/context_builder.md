# ContextBuilder 设计文档

## 概述

`ContextBuilder` 是一个极简的上下文构建器，实现了 **GSSC 四阶段流水线**（Gather → Select → Structure → Compress），用于在每次调用 LLM 前拼装最优上下文。

## 设计理念

上下文工程的核心问题：**在 LLM 有限的上下文窗口内，以最少的 token 传递最高价值的信息。**

本设计遵循三个原则：
1. **信息充分但紧凑** —— 只保留高信号密度的内容
2. **可控可度量** —— 通过评分公式量化信息价值
3. **渐进式披露** —— 按需加载，而非一次性灌入所有信息

## 核心数据结构

### ContextPacket（信息包）

上下文的最小构建单元：

```python
@dataclass
class ContextPacket:
    content: str            # 信息内容
    source: str             # 来源: user / system / memory / tool / assistant
    relevance: float        # 预设相关性 0.0~1.0
    timestamp: datetime     # 时间戳（用于新近性衰减）
```

### ContextConfig（配置）

```python
@dataclass
class ContextConfig:
    max_tokens: int = 3000       # 总 token 预算
    reserve_ratio: float = 0.2   # 系统指令预留比例（20%）
    recency_weight: float = 0.3  # 新近性权重
    relevance_weight: float = 0.7 # 相关性权重
    min_relevance: float = 0.1   # 最低相关性阈值
```

## GSSC 流水线

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Gather  │ →  │  Select  │ →  │Structure │ →  │ Compress │
│  汇集    │    │  选择    │    │  结构化  │    │  压缩    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### 1. Gather（汇集）

通过 `builder.add()` 从多个来源汇集候选信息：

| 来源 | 说明 | 示例 |
|------|------|------|
| `memory` | 历史记忆/摘要 | 之前对话的关键结论 |
| `tool` | 工具检索结果 | RAG 返回的文档片段 |
| `user` | 用户历史输入 | 多轮对话中的旧消息 |
| `assistant` | 助手历史回复 | 上一轮的回答 |

### 2. Select（选择）

使用综合评分公式，贪心填充至 token 预算：

```
综合分数 = relevance_weight × 相关性 + recency_weight × 新近性
```

- **相关性**：取 Jaccard 关键词重叠与预设 relevance 的较大值
- **新近性**：指数衰减模型 `e^(-age_hours/24)`，24h 内保持高分

### 3. Structure（结构化）

输出标准 OpenAI messages 格式（保证 user/assistant 严格交替）：

```
[system]     系统提示 + [参考信息]（来自 tool/memory 的内容）
[user]       历史用户消息
[assistant]  历史助手回复
...          （user/assistant 按时间交替）
[user]       当前用户输入
```

注意：如果连续出现同角色消息，会自动合并，确保不违反 OpenAI 接口的交替约定。

### 4. Compress（压缩）

如果总 token 超过预算，从中间逐条删除历史消息，保留首条 system 和末条 user。

## 使用示例

```python
from context_builder import ContextBuilder

builder = ContextBuilder(system_prompt="你是一个助手")

# 添加背景信息
builder.add("之前讨论过 X 的实现方案", source="memory", relevance=0.8)
builder.add("文档中关于 Y 的说明...", source="tool", relevance=0.9)

# 构建并调用
messages = builder.build(user_input="如何优化 X？")
result = llm.chat(messages)
```

## 架构位置

```
ch04-my-agent/
├── llm.py              # LLM 客户端
├── context_builder.py  # 上下文构建器（本模块）
└── main.py             # 入口 & 示例
```

## 后续扩展方向

| 方向 | 说明 |
|------|------|
| 动态相关性计算 | 当前 relevance 完全由调用方静态指定，未来可结合 query 动态计算（如 Jaccard 关键词重叠或向量相似度），实现 `静态预设 × 0.6 + 动态匹配 × 0.4` 的混合评分 |
| 向量相似度 | 用 embedding 替代关键词匹配，提升语义级别的相关性判断 |
| 对话历史管理 | 自动维护多轮对话的滑动窗口 |
| 分区压缩 | 超限时先摘要再截断，而非直接丢弃 |
| NoteTool 集成 | 持久化笔记作为 memory 来源 |
| Token 精确计算 | 接入 tiktoken 替代粗略估算 |
