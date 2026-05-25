# list 工具

## 功能

列出目录内容，支持递归遍历和显示隐藏文件。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `path` | string | ✅ | - | 目录路径 |
| `recursive` | boolean | ❌ | false | 是否递归列出子目录 |
| `show_hidden` | boolean | ❌ | false | 是否显示隐藏文件（.开头） |

## 返回格式

- 目录以 `/` 结尾
- 递归模式返回相对路径
- 超过 500 条自动截断

## 示例

```python
registry.execute("list", path=".")
registry.execute("list", path="src/", recursive=True)
```
