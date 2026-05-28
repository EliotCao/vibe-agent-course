# Day 5 · Coding Agent 工具集

> 今天结束时，你写完 5 个 Coding Agent 必备工具，理解它们背后的设计哲学，能把代码 push 到 CNB。

## 你将学到

- Coding Agent 的 5 阶段工作流：浏览 → 定位 → 理解 → 修改 → 验证
- 5 个核心工具的设计哲学：read / write / edit / list_dir / bash
- 为什么 edit 用 `old_content / new_content` 而不是行号
- bash 工具的 4 道安全闸门
- 读类工具 vs 写类工具的设计心态差异
- Git push / branch / PR 的 5 个命令

## 内容结构

| 节 | 类型 | 内容 | 讲义 | Demo |
|----|------|------|------|------|
| 24 | 理论 · 25min | Coding Agent 五阶段工作流 | [24-coding-agent-workflow.md](./lecture/24-coding-agent-workflow.md) | `demo_24_five_stages.py` |
| 25 | 理论 · 35min | 工具的设计哲学（4 个关键选择）| [25-tool-design.md](./lecture/25-tool-design.md) | `demo_25_design_philosophy.py` |
| 26-27 | 实操 · 130min | 写 5 个工具 + Git 推送 | [lab/README.md](./lab/README.md) | `demo_26_end_to_end.py` |

## 配套 Demo

```bash
cd lab/demos
python demo_24_five_stages.py        # 手动按 5 阶段调一遍工具
python demo_25_design_philosophy.py  # 3 个对比演示（唯一性 / 行号 / bash 安全）
python demo_26_end_to_end.py         # 让 LLM 用 5 个工具完成"建项目+跑测试"
```

> `lab/coding_tools/` 是完整的参考实现（5 个必做 + 选做 grep）。
> 参考 `lab/coding_tools/` 是填空骨架。

## 当日产物

```
05-checkpoint/
├── coding_tools/
│   ├── __init__.py     # self_test 跑通
│   ├── read.py         # ★ 必做
│   ├── list_dir.py     # ★ 必做
│   ├── write.py        # ★ 必做
│   ├── edit.py         # ★ 必做
│   └── bash.py         # ★ 必做
└── reflection.md
```

## 工具清单

**必做（5 个）：**
- `read(path, offset, limit, max_bytes)` — 读文件，带行号，自动截断
- `list_dir(path, show_hidden, max_items)` — 列目录，区分文件 / 目录
- `write(path, content, overwrite)` — 写新文件，**默认拒绝覆盖**
- `edit(path, old_content, new_content)` — 精确替换，**old_content 必须唯一**
- `bash(command, workdir, timeout, max_output)` — 跑 shell，**4 道安全闸门**

**选做（4 个，详见 exercises）：**
- `grep(pattern, path, file_glob, max_matches)` — 递归正则搜
- `glob(pattern, path)` — 通配符列文件
- `todo` — 任务记录
- `webfetch(url)` — 抓 URL

## Checkpoint

1. **5 个必做工具齐全**，跑 `python -m coding_tools.self_test` 全过
2. **代码 push 到 CNB 仓库**（详见 [lab/README.md → 阶段 D](./lab/README.md#阶段-d--git-速通-5-个命令5min)）
3. **反思**：必做"如果只能保留 3 个工具，你会选哪 3 个 + 理由"
4. **不要求每个工具单测** —— Day6 任务 2 会让你"让自己写的 Agent 给这些工具补单测"

## 跟 Day1-4 / Day6-7 的衔接

| 来自前几天 | 今天怎么用 |
|---|---|
| Day2 ToolRegistry + tool_calls 协议 | 今天用同一个 ToolRegistry 注册 5 个工具，schema 自动生成 |
| Day2 工具异常兜底原则 | **5 个工具一律遵守**：失败转字符串返回，不抛异常 |
| Day4 ContextManager | 工具返回的字符串是 messages 的主要 token 来源——必须自己控制大小 |

| 今天产出 | Day6 / Day7 怎么用 |
|---|---|
| 5 个工具 | Day6 整合到 `my_coding_agent/tools/` —— 直接搬过去 |
| `coding_tools/__init__.py.build_registry()` | Day6 整合时 Agent 一行 import |
| 工具的"设计哲学" | Day7 写 Skills 时，Skill 描述就是给 LLM 的"工具说明书"，同套设计原则 |

## 课后练习题

详见 [exercises/README.md](../exercises/05-coding-agent-tools/README.md)：
- 必做 3 题：实现 grep / bash 黑名单对抗赛 / 用 5 个工具手动跑一个真任务
- 选做 2 题：webfetch / 把 5 个工具接到 Day3 ReAct Agent

## 参考资产

| 资产 | 用途 |
|---|---|
| [`examples/04-my-agent/tools/impl/`](../examples/04-my-agent/tools/impl/) | 9 个工具的工程级 OOP 实现，对比今天教的函数式版本 |
| [`examples/04-my-agent/tools/impl/edit.py`](../examples/04-my-agent/tools/impl/edit.py) | OOP 风格 + multi_edit 模式（Day7 / Day8 时再讲） |
| [`examples/04-my-agent/tools/impl/bash.py`](../examples/04-my-agent/tools/impl/bash.py) | 工程级 bash，对照今天的 4 道闸门看够不够 |
