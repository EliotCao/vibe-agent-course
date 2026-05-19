# Skills 设计文档

## 概述

Skills 是可动态加载的知识/规范片段，存放在 `.codebuddy/skills/` 目录下，以 `.md` 文件形式存在。启动时自动加载，注入到 system prompt 中，让 Agent 具备特定领域的知识和行为规范。

## 设计理念

| 产品 | 类似功能 | 我们的实现 |
|------|----------|-----------|
| Claude Code | `.claude/` 下的 .md 文件 | `.codebuddy/skills/*.md` |
| Cursor | `.cursorrules` | 同上 |
| Aider | `.aider.conf` | 同上 |

核心思想：**用 Markdown 文件声明规范，Agent 自动遵循。**

## 目录结构

```
project/
└── .codebuddy/
    └── skills/
        ├── python-style.md      # Python 编码规范
        ├── git-workflow.md      # Git 工作流
        ├── project-context.md   # 项目背景
        └── testing.md           # 测试要求
```

## 使用方式

### 自动加载

启动时自动扫描 `.codebuddy/skills/` 目录，加载所有 `.md` 文件。

### 命令行管理

```
/skill              # 列出所有 skills
/skill list         # 同上
/skill load name    # 手动加载指定 skill
/skill unload name  # 卸载指定 skill
/skill show name    # 查看 skill 内容
```

### 编写 Skill

创建 `.codebuddy/skills/你的skill名.md`，内容是纯 Markdown：

```markdown
编写代码时请遵循：
- 使用 type hints
- docstring 用中文
- 函数不超过 30 行
```

## 注入方式

Skills 内容拼接后，追加到 system prompt 的末尾：

```
[原始 system prompt]

## Skills

### python-style
编写 Python 代码时请遵循以下规范...

### git-workflow
提交代码时请遵循...
```

## 接口

```python
skills = Skills(workdir=".")

skills.load_all()            # 加载所有
skills.load("name")          # 加载指定
skills.unload("name")        # 卸载指定
skills.list()                # 已加载列表
skills.list_available()      # 可用列表
skills.get("name")           # 获取内容
skills.to_prompt()           # 生成 prompt 文本
skills.create("name", "...")  # 创建新 skill
```

## 架构位置

```
ch04-my-agent/
├── skills.py           # ← Skills 模块
├── coding_agent.py     # 集成 Skills
├── .codebuddy/
│   └── skills/         # Skill 文件存放目录
│       └── python-style.md
└── docs/
    └── skills.md       # ← 本文档
```

## 后续扩展

| 方向 | 说明 |
|------|------|
| 条件加载 | 根据文件类型自动启用对应 skill（检测到 .py 加载 python-style） |
| skill 模板库 | 内置常用 skill 模板，一键初始化 |
| 带工具的 skill | 除了 prompt 片段，还可以注册专用工具 |
| 优先级 | 多个 skill 冲突时的优先级机制 |
