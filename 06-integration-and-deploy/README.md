# 第 6 章 · 整合与部署：完整 Coding Agent + Skills + NPC

> 本章目标：把第 1 章-第 5 章的零件拼装成完整的 Coding Agent，再给它装上「按需加载的领域知识」（Skills），最后作为 NPC 挂到仓库里干活。
> 产出：`my-agent/main.py` — 一个能跑通真实任务的 Agent；以及自定义 Skills + 仓库 NPC。

## 你将学到

- 整体串联流程：各模块按单向数据流怎么协作组装
- Coding Agent 的几个形态：REPL / Solo / WebUI，一个内核多种壳
- **Skills**：为什么需要 Skills、Skills 与 Tool Call 的区别，以及 Agent 实现 Skills 机制的原理（伪代码）
- **NPC**：把 Agent 挂到仓库里，@ 它就自动干活的完整流程（伪代码）

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 20 | 整合与形态 | [20-integration-and-modes.md](./lecture/20-integration-and-modes.md) | - |
| 21 | Skills 机制与原理 | [21-skills.md](./lecture/21-skills.md) | - |
| 22 | NPC 上线流程 | [22-npc.md](./lecture/22-npc.md) | - |

## 作业指引

本章作业在配套作业仓库中完成：

> 📦 **作业仓库**：<https://cnb.cool/opencamp/learning-agent/vibe-agent-exercise>

**流程**：Fork 作业仓库 → 在 `my-agent/` 中完成本章整合任务 → 提交 PR，CI 流水线（`.cnb.yml`）自动测评，全绿即通过。

> 说明：本章聚焦 `my-agent/main.py` 的整合与端到端运行，并在此基础上扩展 Skills、部署为仓库 NPC。

## 本章产出

在作业仓库中打开 `my-agent/main.py`，把所有模块接好，跑通：

```bash
cd my-agent
python main.py
# 输入一个真实任务，如："在当前目录创建一个 hello.py，写一个 hello world，然后运行它"
```
