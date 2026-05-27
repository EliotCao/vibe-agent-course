# read 工具

## 功能

读取文件内容，返回带行号的文本。支持部分读取。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `path` | string | ✅ | - | 文件路径 |
| `offset` | integer | ❌ | 1 | 起始行号（从 1 开始） |
| `limit` | integer | ❌ | 全部 | 读取行数 |
| `max_bytes` | integer | ❌ | 100000 | 最大读取字节数 |

## 返回格式

带行号的文本，格式为 `行号:内容`：

```
 1:import os
 2:from typing import Dict
 3:
```

## 示例

```python
registry.execute("read", path="main.py")
registry.execute("read", path="main.py", offset=10, limit=5)
```
