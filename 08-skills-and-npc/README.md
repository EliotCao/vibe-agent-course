# 第 7 章 · Skills 扩展 + NPC 上线 + 结课大作业

> 本章目标：让你的 Agent 学会领域规范（Skills），并作为 NPC 部署到仓库；布置结课大作业。
> 产出：自定义 Skill + 仓库 NPC 能回复 + 选定大作业方向。

## 你将学到

- Skills 系统：为什么需要、SKILL.md 标准
- NPC 是什么：仓库里的 AI 角色
- Docker 速通：打包 Agent 为镜像
- CNB Pipeline + NPC 配置
- 结课大作业：三个方向自由选择

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 33 | Skills 系统 | [33-skills.md](./lecture/33-skills.md) | `demo_33_skills.py` |
| 34 | NPC 是什么 | [34-what-is-npc.md](./lecture/34-what-is-npc.md) | — |
| 35 | Docker 速通 | [35-docker-quick.md](./lecture/35-docker-quick.md) | — |
| 36 | CNB Pipeline + NPC | [36-cnb-pipeline-and-npc.md](./lecture/36-cnb-pipeline-and-npc.md) | — |
| 37 | 结课大作业 | [37-final-assignment.md](./lecture/37-final-assignment.md) | — |

## 运行 Demo

```bash
cd 08-skills-and-npc/lab
python demo_33_skills.py
```

## 作业指引

本章 Skills / NPC / 大作业在你**自己的 Agent 仓库**中完成（作业仓库的 `exercises/` 第 8 章待更新）。

> 📦 作业仓库（参考与后续更新）：<https://cnb.cool/xidian/vibe-coding-learning/vibe-agent-exercise>

## 本章产出

1. 给你的 Agent 写至少 1 个自定义 Skill（`SKILL.md`）
2. 用 Docker 打包
3. 配置 `.cnb.yml` + `.cnb/settings.yml`
4. 在仓库 Issue 里 @ 你的 NPC，看到回复
5. 选定大作业方向，开始规划

## 大作业

详见 [37-final-assignment.md](./lecture/37-final-assignment.md)

三个方向任选其一：
1. **Coding Agent 优化** — 在你的 Agent 基础上添加特色功能（并行调用、代码索引、沙箱等）
2. **Agent 应用开发** — 用所学知识开发一个解决真实问题的 Agent（运维助手、代码审查 Bot 等）
3. **自由 VibeCoding** — 题材不限，用 AI 辅助编程做出任何你想做的东西

## 模板文件

在 `lab/templates/` 下提供了 Dockerfile / cnb.yml / settings.yml 模板。

## 配套练习

作业仓库的 `exercises/08-skills-and-npc/`（待更新）。
