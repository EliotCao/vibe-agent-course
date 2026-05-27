# webfetch 工具

## 功能

抓取 HTTP(S) 页面或接口内容，HTML 自动剥离标签返回纯文本。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `url` | string | ✅ | - | 要抓取的 URL（http/https） |
| `max_bytes` | integer | ❌ | 100000 | 最大读取字节数 |

## 行为

- HTML 响应：自动移除 `<script>`/`<style>` 块和所有标签，返回纯文本
- JSON/文本响应：原样返回
- 超过 `max_bytes` 自动截断

## 安全限制

| 限制 | 默认值 |
|------|--------|
| 超时 | 15 秒 |
| 最大字节 | 100KB |
| User-Agent | `Mozilla/5.0 (CodingAgent/1.0)` |

## 示例

```python
registry.execute("webfetch", url="https://httpbin.org/get")
registry.execute("webfetch", url="https://example.com", max_bytes=5000)
```
