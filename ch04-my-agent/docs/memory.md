# 记忆系统设计文档

## 概述

`memory.py` 实现了一个极简的三层记忆系统，使用本地 JSON 文件持久化，无外部依赖。

## 设计理念

借鉴认知科学的记忆分层模型，简化为三层：

```
┌────────────────────────────────────────┐
│  工作记忆 (working)                      │  ← 会话级，退出即清
│  "刚才用户问了 X"                        │
├────────────────────────────────────────┤
│  情景记忆 (episodic)                     │  ← 持久化，记录事件
│  "修改了 main.py"、"安装了 requests"     │
├────────────────────────────────────────┤
│  语义记忆 (semantic)                     │  ← 持久化，抽象知识
│  "用户偏好函数式风格"、"项目用 FastAPI"    │
└────────────────────────────────────────┘
```

## 三种记忆类型

| 类型 | 生命周期 | 自动记录 | 用途 |
|------|----------|----------|------|
| `working` | 会话级（reset 即清） | 用户每次提问 | 短期上下文 |
| `episodic` | 持久化 | 文件写入/编辑、安装命令 | 操作历史 |
| `semantic` | 持久化 | 手动或 LLM 提取 | 项目知识、用户偏好 |

## 核心接口

```python
mem = Memory(storage_dir=".memory")

# 添加
mem.add("内容", memory_type="semantic", importance=0.8, tags=["python"])

# 搜索
results = mem.search("main.py", limit=5)

# 获取格式化上下文（注入 prompt）
context_text = mem.get_context(query="当前问题", limit=5)

# 遗忘
mem.forget(strategy="importance", threshold=0.2)

# 统计
mem.stats()  # {'working': 3, 'episodic': 5, 'semantic': 2, 'total': 10}
```

## 检索评分公式

```
分数 = 关键词匹配 × 时间衰减 × (0.8 + importance × 0.4)
```

| 因子 | 说明 |
|------|------|
| 关键词匹配 | query 中的词在记忆内容中出现的比例 |
| 时间衰减 | `e^(-age_hours/24)`，24h 半衰期；working 用 4h 半衰期 |
| importance 权重 | 重要性 0.0~1.0 映射为 [0.8, 1.2] 的乘数 |

## 与 CodingAgent 的集成

### 启动时

```
加载 .memory/memory.json
    ↓
memory.get_context() 提取相关记忆
    ↓
注入 system prompt 末尾的 [记忆] 区块
```

### 每轮任务完成后

自动记录：
- 用户意图 → working 记忆
- 文件写入/编辑 → episodic 记忆（持久化）
- 安装命令 → episodic 记忆（持久化）

### reset 时

- 清空 working 记忆
- 保留 episodic/semantic 记忆
- 重建 system prompt（重新注入记忆）

## 存储格式

```
.memory/
└── memory.json
```

```json
{
  "episodic": [
    {"id": "a1b2c3d4", "content": "修改了文件 main.py", "memory_type": "episodic", "importance": 0.7, "timestamp": "2026-05-19T16:00:00", "tags": ["main.py", "edit"]}
  ],
  "semantic": [
    {"id": "e5f6g7h8", "content": "项目使用 Python + FastAPI", "memory_type": "semantic", "importance": 0.9, "timestamp": "2026-05-19T15:00:00", "tags": ["tech-stack"]}
  ]
}
```

## 后续扩展

| 方向 | 说明 |
|------|------|
| 向量检索 | 用 embedding 替代关键词匹配，提升语义理解 |
| LLM 自动提取 | 让 LLM 从对话中自动提取 semantic 记忆 |
| 记忆整合 | working → episodic → semantic 自动晋升 |
| 遗忘曲线 | 基于访问频率的动态遗忘 |
| 记忆工具 | 让 LLM 可主动调用 memory 工具读写记忆 |
