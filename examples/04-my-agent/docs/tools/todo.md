# todo 工具

## 功能

维护任务 todo 列表，支持增删改查，JSON 持久化存储。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `action` | string | ✅ | - | 操作：`add` / `done` / `list` / `remove` |
| `text` | string | ❌ | "" | 任务内容（`add` 时必填） |
| `index` | integer | ❌ | - | 任务序号（`done` / `remove` 时必填） |

## 操作说明

| 操作 | 说明 |
|------|------|
| `add` | 添加新任务 |
| `done` | 标记任务为已完成 |
| `remove` | 删除任务 |
| `list` | 列出所有任务及状态 |

## 存储

默认存储在工作目录的 `.todo.json` 文件中。

## 示例

```python
registry.execute("todo", action="add", text="实现 coding agent")
registry.execute("todo", action="list")
registry.execute("todo", action="done", index=1)
registry.execute("todo", action="remove", index=2)
```
