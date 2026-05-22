# VibeCoding 课程·完整教学大纲（Agent 主线版）

> 8 天 × 3.5 小时 = 28 小时。每节标注 **分钟数**、**类型**（理论/实操）、**对应已有章节**。

---

## Day 1 · 认识你的 AI

> 主题：搞清楚 LLM 为什么具备"智能"、它的边界在哪、我们怎么跟它对话。今天结束时学生能流式对话 + 估算 token + 体感幻觉。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 1 | LLM 为什么具备智能：从概率预测到涌现 | 理论 | 30min | — |
| 2 | 提示词与角色：System / User / Assistant | 理论 | 30min | — |
| 3 | Token、上下文窗口、token 怎么算 | 理论 | 30min | — |
| 4 | 大模型幻觉：从哪来、怎么识别、怎么缓解 | 理论 | 20min | — |
| 5 | LLM 智能 + 外部支持：为什么需要工具与上下文 | 理论 | 20min | — |
| 6 | 实操：调用 LLM API + 流式输出 + token 计数 | 实操 | 80min | `ch02-hello-llm/` |

**当日产物**：`day1-llm.py`（流式对话）+ `count_tokens.py`（token 估算工具）
**当日 Checkpoint**：用同一 prompt 测两个不同模型 + 主动设计一次"诱发幻觉"的对话

---

## Day 2 · Function Calling 与最小 Agent

> 主题：从对话升级到行动。理解工具协议，亲手实现一个工具注册系统和最小 Agent 循环。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 7 | Agent vs Chatbot：为什么需要循环 | 理论 | 20min | — |
| 8 | Function Calling 协议：Tool Schema 与消息流 | 理论 | 40min | `ch04-my-agent/tools/` |
| 9 | 最小 Agent Loop 的 5 个核心点 | 理论 | 20min | `ch04-my-agent/agent/agent.py` |
| 10 | 实操：实现 ToolRegistry（工具注册类） | 实操 | 60min | `ch04-my-agent/tools/tools.py` |
| 11 | 实操：搭最小 Agent Loop + 接 3 个简单工具 | 实操 | 70min | `ch04-my-agent/agent/agent.py` |

**当日产物**：`tool_registry.py` + `mini_agent.py`（带 calculator / current_time / fetch_url 三个工具）
**当日 Checkpoint**：执行日志 + 一段"模型选错工具"的失败 case 分析

---

## Day 3 · Agent 范式

> 主题：Agent 的"思考方式"不止一种。今天讲三种主流范式，每种都跑一遍。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 12 | ReAct：Thought-Action-Observation 循环 | 理论 | 30min | `ch01-hello-react/` |
| 13 | Plan-and-Solve：先规划再执行 | 理论 | 25min | — |
| 14 | Reflection：让 Agent 自我反思与修正 | 理论 | 25min | — |
| 15 | 实操：把 Day2 的 Agent 改成 ReAct 版 | 实操 | 50min | `ch01-hello-react/agent.py` |
| 16 | 实操：实现 Plan-and-Solve 版（Planner + Executor）| 实操 | 50min | — |
| 17 | 实操：给 Agent 加 Reflection 步骤 + 三种范式横向对比 | 实操 | 30min | — |

**当日产物**：`agent_react.py` + `agent_plan_solve.py` + `agent_reflection.py` + `comparison.md`
**当日 Checkpoint**：三种范式跑同一组 5 个任务的对照表

---

## Day 4 · 上下文与记忆

> 主题：Agent 跑久了上下文会爆、跑完就忘。今天解决这两个工程问题。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 18 | 上下文工程：为什么要管、什么时候爆 | 理论 | 25min | — |
| 19 | 上下文管理策略：截断 / 摘要 / 分层 / GSSC | 理论 | 30min | `ch04-my-agent/context/` |
| 20 | 记忆系统：短期 / 长期 / 工作记忆 | 理论 | 25min | `ch04-my-agent/memory/` |
| 21 | 实操：实现 ContextManager 类 | 实操 | 60min | `ch04-my-agent/context/context_builder.py` |
| 22 | 实操：实现 Memory 类（含简单向量检索） | 实操 | 50min | `ch04-my-agent/memory/memory.py` |
| 23 | 实操：把 Day3 的 Agent 接上 ContextManager + Memory | 实操 | 20min | — |

**当日产物**：`context_manager.py` + `memory.py` + 升级后的 Agent
**当日 Checkpoint**：一段超长任务的"加上下文管理前 vs 后"对比，含 token 消耗曲线

---

## Day 5 · Coding Agent 工具集

> 主题：Coding Agent 的工具是有讲究的。今天搞清楚为什么是这 9 个工具，亲手实现它们。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 24 | Coding Agent 的工作模式：浏览-定位-理解-修改-验证 | 理论 | 25min | `ch04-my-agent/main.py` |
| 25 | 9 个工具的设计哲学：read / write / edit / list / glob / grep / bash / todo / webfetch | 理论 | 35min | `ch04-my-agent/tools/impl/` |
| 25.5 | Git 速通：push / branch / PR / 解决冲突（5 个命令）| 理论+实操 | 30min | — |
| 26 | 实操：实现"读类"工具（read / list / glob / grep）| 实操 | 60min | `ch04-my-agent/tools/impl/` |
| 27 | 实操：实现"写类"工具（write / edit / bash），重点讲 edit 的 old_str/new_str 设计 | 实操 | 60min | `ch04-my-agent/tools/impl/edit.py` |

**当日产物**：`coding_tools/` 目录，9 个独立工具实现 + 单元测试
**当日 Checkpoint**：把工具集 push 到 CNB 仓库

---

## Day 6 · 整合：完整 Coding Agent

> 主题：今天是"组装日"。把 Day2-5 的零件拼成一个能干真活的完整 Agent。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 28 | 整合架构：模块边界与数据流 | 理论 | 25min | `ch04-my-agent/` 总体 |
| 29 | UI 与交互模式：REPL / 单次任务 / 流式输出 | 理论 | 20min | `ch04-my-agent/ui/`, `ch04-my-agent/main.py` |
| 30 | 实操：把 ToolRegistry + Context + Memory + 工具集装到一个 Agent 类 | 实操 | 80min | `ch04-my-agent/agent/agent.py` |
| 31 | 实操：让你的 Agent 完成 3 个真实任务 | 实操 | 70min | — |
| 32 | 实操：故障排查与调优 + 答疑 | 实操 | 15min | — |

**3 个真实任务**（学生 vibe 自己的 Agent 完成）：
1. "为我自己 Day5 写的工具集生成 README"
2. "给某个工具补单测，确保 coverage ≥ 80%"
3. "我代码里有个 bug：xxx，帮我找出来并修"

**当日产物**：`my_coding_agent/`（完整可跑） + 3 个任务的执行录屏
**当日 Checkpoint**：录屏 + 一段"我的 Agent 跟 Cursor / Claude Code 比，差距在哪"反思

---

## Day 7 · Skills 扩展 + NPC 上线

> 主题：让 Agent 学会团队规范，并把它送上云端，挂在仓库里干活。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 33 | Skills 系统：为什么需要、SKILL.md 标准、加载机制 | 理论 | 25min | `ch04-my-agent/skills/` |
| 34 | NPC 是什么：仓库里的 AI 角色 | 理论 | 25min | `docs/cnb-npc-setup.md` |
| 35 | Docker 速通：运行容器 + 写 Dockerfile（最小子集）| 理论+实操 | 30min | `ch04-my-agent/Dockerfile` |
| 36 | CNB Pipeline + NPC 配置（最小子集） | 理论+实操 | 30min | `docs/cnb-npc-setup.md` |
| 37 | 实操：给你的 Agent 实现 Skills 扩展系统 | 实操 | 50min | `ch04-my-agent/skills/` |
| 38 | 实操：把 Agent 打包成镜像 → 挂到仓库做成 NPC | 实操 | 50min | `ch04-my-agent/npc-entrypoint.sh` |

**当日产物**：含 Skills 的 Agent + 仓库 `.cnb.yml` + `.cnb/settings.yml` + NPC 触发记录
**当日 Checkpoint**：在自己 Issue 里 @ NPC，看到回复

---

## Day 8 · 总结 + 大作业

> 主题：把 7 天串起来，每个学生说自己学到了什么。布置结课大作业。

| 节 | 主题 | 类型 | 时长 | 对应资产 |
|----|------|------|------|---------|
| 39 | 课程总复盘：从 token 到 NPC 的全链路 | 理论 | 40min | — |
| 40 | 行业图景：Cursor / Claude Code / Devin / 国产产品对比 | 理论 | 30min | — |
| 41 | 学生分享：每人 3 分钟讲自己的 Agent | 实操 | 60min | — |
| 42 | 大作业布置 + 评分标准说明 | 理论 | 20min | — |
| 43 | 自由 Q&A + 个人后续路线建议 | 实操 | 60min | — |

**结课大作业**（课后 1 周提交）：
- 选一个**真实场景**（自己仓库 / 同学项目 / 开源项目）
- 让你的 NPC 在 Issue 评论里被 @ 后能完成一类有用任务
- 提交：录屏 demo + 总结文档（含技术选型、踩坑、迭代历史）

---

## 教学节奏建议

- 每节理论后留 5 分钟"白板提问时间"，强制学生说出一个疑问
- 每个实操**先让学生自己 vibe 5 分钟**，再老师演示
- 每天最后留 15 分钟做 Checkpoint 提交 + 第二天预告
- 卡壳的学生可以参考 `ch01`-`ch04` 已有实现，但要求**自己抄一遍**

详见 [`teaching-notes.md`](./teaching-notes.md)。
