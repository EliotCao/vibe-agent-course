# edit 工具

## 功能

精确替换文件中的已有内容。要求 `old_content` 在文件中**唯一匹配**。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `path` | string | ✅ | - | 文件路径 |
| `old_content` | string | ✅ | - | 要替换的原始内容 |
| `new_content` | string | ✅ | - | 替换后的新内容 |

## 行为

- `old_content` 匹配 0 次 → 报错
- `old_content` 匹配 >1 次 → 报错（要求提供更多上下文使其唯一）
- `old_content` 匹配恰好 1 次 → 执行替换

## 设计意图

比全文覆写更安全——只改动你指定的片段，避免意外丢失内容。

## 示例

```python
registry.execute("edit",
    path="main.py",
    old_content="print('hello')",
    new_content="print('world')",
)
```
