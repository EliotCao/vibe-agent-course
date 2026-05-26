---
name: add-docstring
description: 给 Python 函数添加 Google 风格 docstring
---

# 规则

当用户要求"加注释""加文档""补 docstring"时，遵循以下规范：

## 格式要求

1. 使用 **Google 风格** docstring
2. 第一行是简短描述（不超 72 字符）
3. 空一行后写 Args / Returns / Raises（如适用）
4. 类型在函数签名已有则不重复，否则在 docstring 里标注

## 示例

```python
def fetch_user(user_id: int, timeout: float = 5.0) -> dict:
    """根据 ID 获取用户信息。

    Args:
        user_id: 用户唯一标识符。
        timeout: HTTP 超时（秒），默认 5.0。

    Returns:
        用户信息字典，包含 name / email / role。

    Raises:
        NotFoundError: user_id 不存在时。
        TimeoutError: 请求超时时。
    """
```

## 注意

- 如果函数已有 docstring，保留原有内容并按规范补全
- 不要给 `__init__` 加多余的 Returns
- 私有方法（`_xxx`）可以简单一行即可
