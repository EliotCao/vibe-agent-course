# Day 7 · Skills 扩展 + NPC 上线

> 今天结束时，每个学生的 Agent 学会"领域规范"（Skills），并且作为 NPC 挂在自己仓库里，能在 Issue 评论里 @ 它得到回复。

## 学习目标

- [ ] 能解释 Skills 解决什么问题（团队规范 / 跨项目复用）
- [ ] 能写 `SKILL.md`（含 frontmatter + 何时调用 + 示例）
- [ ] 能给 Agent 加 `list_skills` 和 `load_skill` 两个工具
- [ ] 能用 Docker 把 Agent 打包成镜像
- [ ] 能配置 `.cnb.yml` 和 `.cnb/settings.yml` 让 NPC 工作
- [ ] 在自己 Issue 里 @ NPC 得到真实回复

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 33 | 25min | 理论 | Skills 系统：为什么需要、SKILL.md 标准、加载机制 | [33-skills.md](./lecture/33-skills.md) |
| 34 | 25min | 理论 | NPC 是什么：仓库里的 AI 角色 | [34-what-is-npc.md](./lecture/34-what-is-npc.md) |
| 35 | 30min | 理论+实操 | Docker 速通：运行容器 + 写 Dockerfile | [35-docker-quick.md](./lecture/35-docker-quick.md) |
| 36 | 30min | 理论+实操 | CNB Pipeline + NPC 配置 | [36-cnb-pipeline-and-npc.md](./lecture/36-cnb-pipeline-and-npc.md) |
| 37 | 50min | 实操 | 给 Agent 实现 Skills 扩展系统 | [lab/part1](./lab/README.md#part1) |
| 38 | 50min | 实操 | 把 Agent 打包成镜像 → 挂仓库做 NPC | [lab/part2](./lab/README.md#part2) |

## 当日产物

```
my_coding_agent/                        # 沿用 Day6
├── skills/
│   └── add-docstring/
│       └── SKILL.md                    # 至少 1 个自定义 Skill
├── tools/
│   └── skills_tool.py                  # 新增 list_skills / load_skill
├── Dockerfile                          # 容器化打包
├── npc-entrypoint.sh                   # NPC 入口脚本
├── .cnb.yml                            # CNB Pipeline + NPC 事件配置
└── .cnb/
    └── settings.yml                    # NPC 角色定义
```

## Checkpoint

1. 完整代码，所有上述文件齐全
2. 在自己仓库新建一个 Issue，评论 `@<owner>/<repo>(<NPC名>) 介绍下这个仓库`，**截图看到 NPC 回复**
3. 至少 3 次成功的 NPC 触发记录
4. 一段"加 Skill 前 vs 后"的对比（用同一任务跑两次，输出差异）
5. 100-200 字反思

## 教师演示备用

- `ch04-my-agent/skills/` —— Skill 加载机制
- `ch04-my-agent/Dockerfile` —— **直接发给学生当模板**
- `ch04-my-agent/npc-entrypoint.sh` —— **直接发给学生当模板**
- `docs/cnb-npc-setup.md` —— **直接发给学生当操作手册**

## 教师准备（关键）

> 今天链路最长，老师**必须提前发 4 份模板**给学生：

1. `Dockerfile` 模板（基于 ch04-my-agent 的版本）
2. `npc-entrypoint.sh` 模板
3. `.cnb.yml` 模板（含 NPC 事件流水线）
4. `.cnb/settings.yml` 模板

学生只需要：
- 改 NPC 名字（`.cnb/settings.yml`）
- 改 Dockerfile 里 `COPY` 的路径（如果项目结构不同）
- 自己仓库 push 一次触发构建
- 在 Issue 里 @ 试一下

**不要让学生从零写 Dockerfile**，时间不够，也不是今天的重点。

---

## Demo 索引

| Demo | 功能 | 文件 |
|------|------|------|
| `demo_33` | Skills 扫描/匹配/加载演示 | `lab/demos/demo_33_skills.py` |
| 示例 Skills | add-docstring / commit-convention | `lab/demos/skills/` |

---

## 模板文件

| 文件 | 作用 | 位置 |
|------|------|------|
| Dockerfile | 两阶段构建 NPC 镜像 | `lab/templates/Dockerfile` |
| npc-entrypoint.sh | 容器入口脚本 | `lab/templates/npc-entrypoint.sh` |
| cnb.yml | NPC 事件流水线定义 | `lab/templates/cnb.yml` |
| settings.yml | NPC 角色定义 | `lab/templates/settings.yml` |

---

## 课后练习

见 [exercises/README.md](./exercises/README.md)（3 必做 + 2 选做）

---

## 衔接关系

| 来自哪天 | 今天用什么 |
|----------|------------|
| Day6 | my_coding_agent 完整 Agent（被打包进 Docker） |
| Day5 | 5 个工具（Agent 在 NPC 模式下用它们干活） |
| Day4 | Memory（NPC 跨次对话不保留，单次清空） |
| → Day8 | 复盘 + 大作业（用完整 NPC 完成一个端到端项目）|
