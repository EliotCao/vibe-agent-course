# write 工具

## 功能

写入文件内容，自动创建父目录，支持覆盖或追加模式。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `path` | string | ✅ | - | 文件路径 |
| `content` | string | ✅ | - | 要写入的内容 |
| `append` | boolean | ❌ | false | 是否追加模式（否则覆盖） |

## 行为

- 文件不存在：自动创建（含父目录）
- `append=False`：覆盖已有内容
- `append=True`：在文件末尾追加

## 示例

```python
registry.execute("write", path="hello.py", content="print('hello')\n")
registry.execute("write", path="log.txt", content="新日志\n", append=True)
```
