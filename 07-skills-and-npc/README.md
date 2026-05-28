# Day 7 · Skills 扩展 + NPC 上线

> 本章目标：让你的 Agent 学会领域规范（Skills），并作为 NPC 部署到仓库。
> 产出：自定义 Skill + 仓库 NPC 能回复。

## 你将学到

- Skills 系统：为什么需要、SKILL.md 标准
- NPC 是什么：仓库里的 AI 角色
- Docker 速通：打包 Agent 为镜像
- CNB Pipeline + NPC 配置

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 33 | Skills 系统 | [33-skills.md](./lecture/33-skills.md) | `demo_33_skills.py` |
| 34 | NPC 是什么 | [34-what-is-npc.md](./lecture/34-what-is-npc.md) | — |
| 35 | Docker 速通 | [35-docker-quick.md](./lecture/35-docker-quick.md) | — |
| 36 | CNB Pipeline + NPC | [36-cnb-pipeline-and-npc.md](./lecture/36-cnb-pipeline-and-npc.md) | — |

## 运行 Demo

```bash
cd 07-skills-and-npc/lab
python demo_33_skills.py
```

## 今日产出

1. 给你的 Agent 写至少 1 个自定义 Skill（`SKILL.md`）
2. 用 Docker 打包
3. 配置 `.cnb.yml` + `.cnb/settings.yml`
4. 在仓库 Issue 里 @ 你的 NPC，看到回复

## 模板文件

在 `lab/templates/` 下提供了 Dockerfile / cnb.yml / settings.yml 模板。

## 配套练习

[`exercises/07-skills-and-npc/`](../exercises/07-skills-and-npc/)
