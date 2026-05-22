# Day 5 · Coding Agent 工具集

> 今天结束时，每个学生写完 9 个 Coding Agent 必备工具，知道为什么是这 9 个、为什么要这样设计。

## 学习目标

- [ ] 能讲清 Coding Agent 的 5 阶段工作流：浏览-定位-理解-修改-验证
- [ ] 能解释为什么 `edit_file` 用 old_str/new_str 而不是行号
- [ ] 能解释 `bash` 工具的 4 个安全要点
- [ ] 能为读类工具加路径校验、大小限制、行号输出
- [ ] 能用 Git 把作业 push 到 CNB（push / branch / PR / 解决冲突）

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 24 | 25min | 理论 | Coding Agent 的工作模式：浏览-定位-理解-修改-验证 | [24-coding-agent-workflow.md](./lecture/24-coding-agent-workflow.md) |
| 25 | 35min | 理论 | 9 个工具的设计哲学 | [25-tool-design.md](./lecture/25-tool-design.md) |
| 25.5 | 30min | 理论+实操 | Git 速通：5 个命令搞定 push / branch / PR | [25.5-git-quick.md](./lecture/25.5-git-quick.md) |
| 26 | 60min | 实操 | 实现"读类"工具：read / list / glob / grep | [lab/part1](./lab/README.md#part1) |
| 27 | 60min | 实操 | 实现"写类"工具：write / edit / bash + todo + webfetch | [lab/part2](./lab/README.md#part2) |

## 当日产物

```
day5/
├── coding_tools/
│   ├── __init__.py        # ALL_TOOLS 集合
│   ├── read.py
│   ├── write.py
│   ├── edit.py
│   ├── list.py
│   ├── glob.py
│   ├── grep.py
│   ├── bash.py
│   ├── todo.py            # 选做
│   └── webfetch.py        # 选做
└── tests/                 # 每个工具至少 1 个 unit test
```

## Checkpoint

1. **必做**完成 7 个核心工具（read / write / edit / list / glob / grep / bash），选做 todo / webfetch
2. **每个工具至少 1 个单元测试**
3. **代码 push 到 CNB 仓库**（这就是今天 Git 速通的成果）
4. 一段你的"如果只能保留 3 个工具，你会选哪 3 个" + 理由
5. 100-200 字反思

## 教师演示备用

- `ch04-my-agent/tools/impl/` —— 9 个工具的工程级实现，全部可投屏对照
- `ch04-my-agent/tools/impl/edit.py` —— 重点：multi_edit 模式
- `ch04-my-agent/tools/impl/bash.py` —— 重点：危险命令拦截 + timeout

## Git 速通（25.5 节，30min）

只讲让作业能交出去的最小子集：

| 命令 | 用法 |
|------|------|
| `git init` + `git remote add origin ...` | 关联仓库 |
| `git add .` + `git commit -m "..."` | 提交 |
| `git push -u origin main` | 推送 |
| `git checkout -b feature-x` | 开分支 |
| `git push origin feature-x` | 推分支 |
| 在 CNB 网页点 PR | 提交 PR |

不讲：rebase / cherry-pick / stash / reset / 钩子 / 子模块。这些课程不需要。

冲突解决：当场制造一次双人冲突，演示一遍 `<<< === >>>` 标记怎么删。
