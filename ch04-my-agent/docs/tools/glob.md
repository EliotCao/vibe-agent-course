# glob 工具

## 功能

按 glob 模式匹配文件名，支持 `**` 递归匹配。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `pattern` | string | ✅ | - | glob 模式，如 `**/*.py` |
| `path` | string | ❌ | `.` | 搜索根目录 |

## 模式语法

| 模式 | 匹配 |
|------|------|
| `*.py` | 当前目录下所有 .py 文件 |
| `**/*.py` | 递归所有 .py 文件 |
| `src/**/*.ts` | src 下所有 .ts 文件 |
| `test_*.py` | 以 test_ 开头的 .py 文件 |

## 示例

```python
registry.execute("glob", pattern="**/*.py")
registry.execute("glob", pattern="docs/**/*.md", path="/workspace")
```
