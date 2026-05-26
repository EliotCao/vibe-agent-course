# Day 8 · 总结 + 大作业

> 课程最后一天。复盘 7 天链路、对比行业图景、学生分享、布置大作业。

## 学习目标

- [ ] 能完整画出"从 token 到 NPC"的全链路图
- [ ] 知道当前业界主流 Coding Agent 的差异（Cursor / Claude Code / Devin / 国产产品）
- [ ] 能讲清自己 7 天的产物，并指出可改进点
- [ ] 知道结课大作业的要求和评分标准
- [ ] 有清晰的"课后路线图"

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 39 | 40min | 理论 | 课程总复盘：从 token 到 NPC 的全链路 | [39-recap.md](./lecture/39-recap.md) |
| — | 30min | 互动 | 课堂提问（30 题随机抽） | [quiz-questions.md](./lecture/quiz-questions.md) |
| 41 | 60min | 互动 | 学生分享：每人 3 分钟讲自己的 Agent | — |
| 42 | 20min | 理论 | 大作业布置 + 评分标准说明 | [final-assignment.md](./exercises/final-assignment.md) |
| 43 | 60min | 自由 | Q&A + 个人后续路线建议 | — |

## 课程总复盘要点

把 7 天串成一根线，让学生**自己**说出每天学的是什么：

```
Day1: LLM 是什么 + token + 提示词 + 幻觉
       ↓
Day2: Tools + 最小 Agent Loop（让 LLM 行动）
       ↓
Day3: 三种范式（让 Agent 不同思考方式）
       ↓
Day4: Context + Memory（让 Agent 不忘事不爆炸）
       ↓
Day5: 9 个 Coding 工具（让 Agent 能读写代码）
       ↓
Day6: 整合（让所有零件协作）
       ↓
Day7: Skills + NPC（让 Agent 学规范 + 上云端）
       ↓
Day8: 你下一步要做什么？（结课作业）
```

## 行业图景对比表（投屏用）

| 产品 | 形态 | 主要范式 | 上下文管理 | Skills | 商用模式 |
|------|------|---------|-----------|--------|---------|
| Cursor | IDE 插件 | ReAct + Function Calling | 大模型长上下文 + 索引 | Rules | 订阅 |
| Claude Code | CLI | Function Calling + Reflection | 多 Agent + 摘要 | SKILL.md | API Key |
| Devin | 自主 Agent | Plan-and-Solve + 多 Agent | 强 Memory | 内置 | 订阅 |
| GitHub Copilot Workspace | 网页 | Plan-and-Solve | 仓库索引 | — | 订阅 |
| 通义灵码 / 文心快码 | IDE 插件 | ReAct | 大模型 | — | 订阅 |
| 你今天的 Agent | CLI + NPC | 你选的范式 | ContextManager | SKILL.md | 你的 token |

> **关键讲点**：你今天做的 Agent，已经具备 80% 的核心能力。剩下的 20% 是工程细节、模型质量、生态集成。

## 学生分享要求（41 节）

每人 3 分钟，必须包含：
1. 我的 Agent 名字与定位
2. 我用了什么范式（Day3 选哪种）
3. 我自己最满意的一个工具或 Skill
4. 我最大的卡点是什么
5. 我之后想加什么功能

老师做点评，不打分（已经在 Day1-7 Checkpoint 打过）。

## 大作业布置

详见 [`exercises/final-assignment.md`](./exercises/final-assignment.md)。

**核心要求**：
- 选一个**真实场景**：自己仓库 / 同学项目 / 开源项目
- 让你的 NPC 在 Issue 评论里被 @ 后能完成一类有用任务
- 至少 5 次成功触发记录
- 提交时间：课后 1 周

**禁止**：
- 直接复用 ch04-my-agent 的代码（必须是自己 Day1-7 写的版本）
- 让 NPC 只回复"你好"这种水任务

**评分**：30 分，详见 [`exercises/final-assignment.md`](./exercises/final-assignment.md)。

## 课后路线建议（43 节抛出）

按学生兴趣分类推荐：

**想往工程方向**：
- 读 LangGraph / DSPy 源码
- 做一个"团队级"Agent（多人共用 Skills）
- 学 vector DB（pgvector / qdrant）

**想往算法方向**：
- 读 ReAct / Reflexion / Voyager / Tree of Thoughts 论文
- 跟一个 ICLR/NeurIPS 的 Agent 工作做复现
- 学 RLHF 和模型微调

**想做产品**：
- 选一个真实领域（运维 / 客服 / 数据分析）做垂直 Agent
- 接入企业内部数据
- 做 Eval / 可观测性

**想做开源**：
- 给主流 Agent 框架（hello-agents / LangChain / Autogen）提 PR
- 把自己课程作业开源
