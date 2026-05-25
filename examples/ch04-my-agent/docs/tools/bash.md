# bash 工具

## 功能

在工作区内执行 shell 命令（`/bin/sh -lc`），带超时和输出大小限制。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `command` | string | ✅ | - | 要执行的 shell 命令 |
| `workdir` | string | ❌ | 当前目录 | 工作目录 |

## 安全限制

| 限制 | 默认值 |
|------|--------|
| 超时 | 30 秒 |
| 最大输出 | 50000 字符 |
| 执行方式 | `/bin/sh -lc`（login shell） |

## 返回格式

- 正常：stdout 内容
- 有 stderr：`[stderr]\n...`
- 非零退出码：`[exit code: N]\n...`
- 超时：错误提示

## 示例

```python
registry.execute("bash", command="python --version")
registry.execute("bash", command="ls -la src/", workdir="/workspace")
registry.execute("bash", command="pip install requests")
```
