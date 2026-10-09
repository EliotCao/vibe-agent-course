# 第 6 章 · Skills 扩展 + NPC 上线

> 本章目标：给第 5 章整合好的 Coding Agent 装上「按需加载的领域知识」（Skills），再把它作为 NPC 挂到仓库里干活。
> 本章只讲原理，讲义中所有代码均以伪代码表述。

## 你将学到

- **Skills**：为什么需要 Skills、Skills 与 Tool Call 的区别，以及 Agent 实现 Skills 机制的原理（伪代码）
- **NPC**：CNB 上 NPC 怎么用、自定义一个 NPC 大致要配什么（Docker 打包与 Pipeline 留作课后实验）

## 内容结构

| 节 | 内容 | 讲义 |
|----|------|------|
| 20 | Skills 机制与原理 | [20-skills.md](./lecture/20-skills.md) |
| 21 | NPC 上线流程 | [21-npc.md](./lecture/21-npc.md) |

## 作业指引

本章作业在配套作业仓库中完成：

> 📦 **作业仓库**：<https://cnb.cool/opencamp/learning-agent/vibe-agent-exercise>

**流程**：Fork 作业仓库 → 在 `my-agent/` 中为你的 Coding Agent 扩展自定义 Skills → 提交 PR，CI 流水线（`.cnb.yml`）自动测评，全绿即通过。

## 本章产出

- 为第 5 章的 Coding Agent 编写至少一个自定义 **Skill**（`SKILL.md`），让它面对特定场景自动加载对应规范
- （课后实验）把 Agent 打包成 Docker 镜像，在 CNB 仓库里配置并上线一个 **NPC**，@ 它就能自动干活
