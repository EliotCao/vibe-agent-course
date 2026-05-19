# grep 工具

## 功能

在文件内容中搜索文本或正则表达式，返回 `file:line: content` 格式。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | string | ✅ | - | 搜索模式（支持正则） |
| `path` | string | ✅ | - | 搜索路径（文件或目录） |
| `recursive` | boolean | ❌ | true | 是否递归搜索子目录 |
| `max_results` | integer | ❌ | 50 | 最大返回条数 |

## 行为

- 自动跳过隐藏文件/目录、`node_modules`、`__pycache__`
- 支持完整正则语法
- 输出格式：`文件路径:行号: 匹配行内容`

## 示例

```python
registry.execute("grep", pattern="def main", path=".")
registry.execute("grep", pattern="import.*os", path="src/")
registry.execute("grep", pattern="TODO", path=".", max_results=20)
```
