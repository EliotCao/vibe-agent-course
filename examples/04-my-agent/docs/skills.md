# Skills 设计文档

## 概述

Skills 是可动态加载的知识/规范片段，遵循 **Anthropic Agent Skills 开放标准**（2025 年发布，已被 33+ Agent 产品采纳）。

采用**渐进式披露（Progressive Disclosure）**策略：启动时只解析元数据，按需加载完整内容。

## 行业标准格式

每个 Skill 是一个 `SKILL.md` 文件，由 YAML frontmatter + Markdown body 组成：

```markdown
---
name: code-review
description: PR 代码评审，检查安全漏洞、Bug 和代码质量。
---

# PR 代码评审

对 PR 的代码变更进行专业评审...

## 评审步骤
...
```

### Frontmatter 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | Skill 唯一标识（小写字母、数字、连字符） |
| `description` | ✅ | 简短描述（供 LLM 判断是否相关） |

### 目录结构

```
~/.codebuddy/skills/
├── code-review/
│   └── SKILL.md
├── code-commit/
│   └── SKILL.md
└── python-style.md      # 也支持单文件形式
```

## 渐进式加载

```
┌─────────────────────────────────────────────────────────┐
│  Level 1: 索引（启动时注入 system prompt）              │
│                                                          │
│  ## 可用 Skills                                          │
│  - code-review: PR 代码评审...                           │
│  - code-commit: 编写代码、提交推送...                    │
│  - cnb-api: CNB 平台交互命令...                          │
│                                                          │
│  → LLM 知道有哪些 skill 可用，但不占大量 token           │
├─────────────────────────────────────────────────────────┤
│  Level 2: 按需加载（匹配到相关 skill 时）               │
│                                                          │
│  ## 已激活 Skills                                        │
│  ### code-review                                         │
│  （完整的评审步骤、规范、模板...）                        │
│                                                          │
│  → 只有相关的 skill 才加载完整内容                       │
└─────────────────────────────────────────────────────────┘
```

### 匹配策略

用户输入中的关键词与 skill 的 `name` + `description` 做交集匹配：

```
用户: "帮我做个代码评审"
       ↓ 匹配 "代码评审"
自动加载: code-review
```

## 使用方式

### 自动匹配

用户提问时自动匹配相关 skill 并加载，无需手动干预：

```
▶ 帮我提交代码并创建 PR
  📚 已激活 skill: code-commit
  ...
```

### 手动管理

```
/skill              # 列出所有 skills 及状态
/skill load name    # 手动加载
/skill unload name  # 卸载（释放 token）
/skill show name    # 查看内容
```

### `/skill list` 输出示例

```
Skills（13 个）:
  ● code-review — PR 代码评审，检查安全漏洞...
  ○ cnb-api — CNB 平台交互命令...
  ○ cnb-pipeline — 编写、修改 CI 配置文件...

●=已加载  ○=仅索引
```

## 接口

```python
skills = Skills()

# 查询
skills.list()           # 所有发现的 skill 名
skills.list_loaded()    # 已加载 body 的 skill
skills.get_meta(name)   # 获取元数据

# 加载/卸载
skills.load(name)       # 加载完整 body
skills.unload(name)     # 释放 body

# 匹配
skills.match(query)     # 根据问题匹配相关 skill

# 生成 prompt
skills.to_index_prompt()   # Level 1: name + description
skills.to_active_prompt()  # Level 2: 已加载的完整内容
```

## 与 CodingAgent 的集成

1. **启动时**：`_scan()` 解析所有 frontmatter → `to_index_prompt()` 注入 system prompt
2. **每轮对话**：`match(user_input)` 匹配 → `load()` 加载 → `to_active_prompt()` 注入
3. **token 节约**：未匹配的 skill 只占索引行（~20 token），不浪费上下文空间

## 后续扩展

| 方向 | 说明 |
|------|------|
| 语义匹配 | 用 embedding 替代关键词匹配 |
| `/skill-name` 命令 | 像 Claude Code 一样用 `/code-review` 直接触发 |
| 带脚本的 skill | `scripts/` 目录下放可执行脚本 |
| 引用文档 | `references/` 目录按需加载参考资料 |
| 远程 skill 仓库 | 从网络安装社区 skill |
