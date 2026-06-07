# 第 4 章 · 练习题

> 每题都是一个 Python 文件，补全 `TODO` 部分使所有断言通过。
> 运行：`python ex_4_1.py`，看到 `✅ PASSED` 即为完成。

## 练习 4.1 · 上下文压缩器

补全 `compress_messages`：当消息列表太长时，用 LLM 摘要压缩早期对话。

## 练习 4.2 · 向量记忆存取

补全 `VectorMemory` 类：add 存入（文本→向量），search 检索（余弦相似度 top-k）。

## 练习 4.3 · 上下文管理决策器

补全 `should_compress`：判断当前 messages 是否需要压缩（基于 token 数阈值）。

---

文件在 `exercises/05-context-and-memory/` 目录下。
