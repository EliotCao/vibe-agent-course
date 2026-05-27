# 工具系统设计文档

## 概述

`tools.py` 实现了一个极简的工具系统，提供统一的工具注册、描述和执行能力。工具系统是 Agent 的"手脚"——让 LLM 能够与外部世界交互。

## 设计原则

1. **两种注册方式** —— 装饰器（简单函数）+ Tool 类（复杂工具），覆盖不同场景
2. **自描述** —— 每个工具自带名称、描述和参数定义，可自动生成 LLM 所需的 schema
3. **统一执行接口** —— `registry.execute(name, **kwargs)` 一种方式调用所有工具
4. **安全容错** —— 执行失败返回错误字符串，不抛异常

## 核心结构

```
ToolParameter     参数定义（name, type, description, required）
     │
     ▼
Tool (ABC)        工具基类（复杂工具继承它）
     │            ├── run(**kwargs) → str
     │            ├── get_parameters() → List[ToolParameter]
     │            └── to_openai_schema() → Dict
     ▼
ToolRegistry      注册表（管理中枢）
                  ├── register(装饰器) → 注册简单函数
                  ├── register_tool() → 注册 Tool 实例
                  ├── execute(name, **kwargs) → str
                  ├── get_tools_description() → str（注入 prompt）
                  └── to_openai_schema() → List[Dict]（function calling）
```

## 两种注册方式

### 方式一：装饰器（适合简单工具）

```python
registry = ToolRegistry()

@registry.register(
    "get_weather",
    "获取天气",
    params=[ToolParameter(name="city", type="string", description="城市")]
)
def get_weather(city: str) -> str:
    return f"{city}: 晴天"
```

### 方式二：Tool 类（适合复杂工具）

```python
class SearchTool(Tool):
    def __init__(self):
        super().__init__("search", "搜索互联网信息")

    def get_parameters(self):
        return [ToolParameter(name="query", type="string", description="搜索词")]

    def run(self, query: str) -> str:
        # 复杂逻辑：多源搜索、降级、缓存...
        return results

registry.register_tool(SearchTool())
```

## 与 LLM 的集成方式

### 方式一：提示词注入（简单但通用）

```python
system_prompt = f"""你是一个助手，你可以使用以下工具：
{registry.get_tools_description()}

需要使用工具时，请输出：[TOOL_CALL:工具名:参数]
"""
```

### 方式二：OpenAI Function Calling（推荐）

```python
response = client.chat.completions.create(
    model="...",
    messages=messages,
    tools=registry.to_openai_schema(),  # 直接传入
)
```

## 执行流程

```
用户输入
   ↓
ContextBuilder 构建 messages（含工具描述）
   ↓
LLM 推理 → 决定调用哪个工具 + 参数
   ↓
registry.execute(tool_name, **params) → 结果字符串
   ↓
结果注入上下文 → LLM 生成最终回答
```

## 架构位置

```
04-my-agent/
├── llm.py              # LLM 客户端
├── context_builder.py  # 上下文构建器
├── tools.py            # ← 工具系统（本模块）
├── main.py             # 入口 & 示例
└── docs/
    ├── llm.md
    ├── context_builder.md
    └── tools.md        # ← 本文档
```

## 后续扩展方向

| 方向 | 说明 |
|------|------|
| 工具链编排 | 支持多个工具顺序执行，上下文传递（A 的输出作为 B 的输入） |
| 异步执行 | 多个独立工具并行调用，提升响应速度 |
| 参数校验 | 执行前自动检查必填参数和类型匹配 |
| 工具权限 | 区分只读/写入工具，敏感操作需确认 |
| 自动发现 | 扫描目录自动注册符合规范的工具模块 |
