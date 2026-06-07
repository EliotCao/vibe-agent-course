# 第 2 章 · 练习题

> 每题都是一个 Python 文件，补全 `TODO` 部分使所有断言通过。
> 运行：`python ex_2_1.py`，看到 `✅ PASSED` 即为完成。

## 练习 2.1 · 手搓 Function Calling 消息流

补全完整的 4 步消息流：user → assistant(tool_calls) → tool(result) → assistant(final)

## 练习 2.2 · ToolRegistry 注册与调用

补全一个最小 ToolRegistry：装饰器注册 + 生成 schema + 按名字分发执行

## 练习 2.3 · 最小 Agent Loop

补全一个 while 循环：模型有 tool_calls 就执行并回传，没有就结束

---

文件在 `exercises/03-tools-and-agent-loop/` 目录下。
