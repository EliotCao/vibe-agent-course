---
name: commit-convention
description: Git commit 使用 Conventional Commits 格式
---

# 规则

当用户要求"提交""commit""写 commit message"时，遵循以下规范：

## 格式

```
<type>(<scope>): <subject>

[可选 body]

[可选 footer]
```

## type 允许值

| type | 含义 |
|------|------|
| feat | 新功能 |
| fix | 修 bug |
| docs | 文档 |
| style | 格式（不影响逻辑） |
| refactor | 重构（非 feat 非 fix） |
| test | 测试 |
| chore | 构建/工具链 |

## 规则

- subject 不超过 50 字符
- 全小写，不加句号
- 用祈使句（"add" 不是 "added" 不是 "adds"）
- scope 可选，但如果改了多个模块建议拆成多个 commit

## 示例

```
feat(tools): add grep tool for recursive text search

fix(edit): reject when old_content appears more than once

docs(readme): add ch7 skills section
```
