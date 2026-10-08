<p align="center">
    <img src="../assets/banner-04-context-memory.svg" alt="Context & Memory">
</p>

# 第 4 章 · 上下文与记忆

本章目标：解决 Agent 的两个关键问题 —— 对话过长导致上下文爆炸（token 超限）、会话结束后遗忘用户偏好（无长期记忆）。
产出：`my-agent/context.py`（上下文管理器）和 `my-agent/memory.py`（向量记忆系统）。



## 本章要点

- 上下文爆炸的根源：每轮对话追加 user + assistant 消息，token 数线性增长，迟早超出模型上限
- 三层上下文管理策略：system prompt 常驻、`keep_last` 保留最近原文、中间段用 LLM 摘要压缩
- 向量记忆系统：用 embedding 将事实转为向量，通过余弦相似度检索相关长期记忆
- Agent v2 实战整合：将 `ContextManager` 和 `Memory` 接入 Agent Loop，实现跨会话记忆



## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 13 | 为什么要管上下文 | [13-why-context-matters.md](./lecture/13-why-context-matters.md) | `demo_13_context_explosion.py` |
| 14 | 上下文管理策略 | [14-context-strategies.md](./lecture/14-context-strategies.md) | `demo_14_context_strategies.py` |
| 15 | Memory 系统 | [15-memory-types.md](./lecture/15-memory-types.md) | `demo_15_memory.py` |
| 16 | Agent v2（整合） | — | `demo_16_agent_v2.py` |



## 运行示例

在云原生开发环境中执行：

```bash
cd 04-context-and-memory/lab
python demo_13_context_explosion.py
python demo_14_context_strategies.py
python demo_15_memory.py
python demo_16_agent_v2.py
```



## 作业指引

本章作业需要在配套仓库中完成，按以下步骤操作：

> [!TIP]
>
> 📦 **作业仓库**：<https://cnb.cool/opencamp/learning-agent/vibe-agent-exercise>

**操作流程**：

1. **Fork** 作业仓库到自己的账号下
2. 在 `my-agent/` 目录中完成核心代码产出，在 `exercises/` 目录中完成配套填空题
3. **提交 PR**，CI 流水线（`.cnb.yml`）会自动运行测评
4. 全部测试通过（全绿）即视为作业通过检测 ✅，作业完成



## 本章产出

在作业仓库中补全 `my-agent/context.py` 和 `my-agent/memory.py`，执行以下命令让测试通过：

```bash
cd my-agent
python tests/test_context.py
python tests/test_memory.py
```



## 配套练习

作业仓库的 `exercises/04-context-and-memory/` — 3 道代码填空题（运行 `python exercises/04-context-and-memory/ex_*.py` 看到 ✅ PASSED 即通过）。
