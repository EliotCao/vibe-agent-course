# 第 6 章 · 整合：完整 Coding Agent

> 本章目标：把第1章-第5章的零件拼装成完整的 Coding Agent。
> 产出：`my-agent/main.py` — 一个能跑通真实任务的 Agent。

## 你将学到

- 整合架构：各模块怎么协作
- REPL 交互界面
- 端到端调试技巧

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 28 | 整合架构 | [28-integration-architecture.md](./lecture/28-integration-architecture.md) | `demo_30_integration_walkthrough.py` |
| 29 | UI 与交互 | [29-ui-and-modes.md](./lecture/29-ui-and-modes.md) | `demo_31_three_tasks.py` |

```

## 作业指引

本章作业在配套作业仓库中完成：

> 📦 **作业仓库**：<https://cnb.cool/xidian/vibe-coding-learning/vibe-agent-exercise>

**流程**：Fork 作业仓库 → 在 `my-agent/` 中完成本章整合任务 → 提交 PR，CI 流水线（`.cnb.yml`）自动测评，全绿即通过。

> 说明：作业仓库的 `exercises/` 第 7 章待更新，本章聚焦 `my-agent/main.py` 的整合与端到端运行。

## 本章产出

在作业仓库中打开 `my-agent/main.py`，把所有模块接好，跑通：

```bash
cd my-agent
python main.py
# 输入一个真实任务，如："在当前目录创建一个 hello.py，写一个 hello world，然后运行它"
```

## 验证标准

- [ ] `python main.py` 能启动 REPL
- [ ] 能通过对话让 Agent 创建文件、写代码、执行命令
- [ ] 至少完成 3 个端到端任务
