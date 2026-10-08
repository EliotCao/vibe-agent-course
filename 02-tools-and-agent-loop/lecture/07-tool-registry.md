# 第 7 节 · ToolRegistry：让加工具像加函数一样简单

## 一句话回答

> **`ToolRegistry` 是一个"装饰器 + 反射"的小工具，让你写一个普通 Python 函数 → 自动成为 LLM 能调用的工具。**

它不是魔法，是把第 6 节那 30 行 schema JSON **从手写挪到了自动生成**。

## 没有 ToolRegistry 时的痛

回到第 6 节：每加一个工具，你都要写两份东西。

```python
# 1. 函数本体
def get_weather(city: str) -> str:
    return f"{city} 晴 25°C"

# 2. 一份 30 行的 schema（重复信息）
{
    "type": "function",
    "function": {
        "name": "get_weather",                   # ← 函数名重复一次
        "description": "查询指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {                         # ← 参数名重复一次
                    "type": "string",             # ← 参数类型重复一次
                    "description": "城市名",
                }
            },
            "required": ["city"],                # ← required 重复一次
        },
    },
}
```

工具一多，**重复代码爆炸**：参数名、参数类型、required 列表，每加一个工具都要在两个地方写一遍。一旦改了函数签名忘了改 schema，模型就调错。

## ToolRegistry 长什么样

![ToolRegistry 三步注册：写函数 → 装饰器 → LLM 自取](./images/08-tool-registry.png)

```python
registry = ToolRegistry()

@registry.tool("查询指定城市的当前天气")
def get_weather(city: str) -> str:
    return f"{city} 晴 25°C"
```

**就这两行**。`name` / `parameters` / `required` 全部从函数签名自动读出来。

调 LLM 时：

```python
resp = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=registry.to_schemas(),    # ← 自动生成所有 schema
)

for tc in resp.choices[0].message.tool_calls:
    args = json.loads(tc.function.arguments)
    result = registry.invoke(tc.function.name, args)   # ← 自动调度
```

## 装饰器在这里干了什么（一句话版）

`@registry.tool("...")` 不是框架魔法。它做的就一件事：**把你这个函数偷偷登记到 `registry._funcs` 里，函数本身原封不动还回去**。所以 `get_weather()` 还是照常能调，registry 也认识它了。

> 想知道 `@deco` 到底怎么被 Python 翻译、为什么带参装饰器要写两层函数，看本节结尾的 **扩展阅读 · 装饰器脱糖**。本章正文里你只需要记住"它就是个登记动作"。

## 它是怎么"自动"的（一句话版）

ToolRegistry 用 Python 自带的 `inspect.signature()` **读函数签名**——参数名、类型注解、有没有默认值——再按一张映射表（`str→"string"`、`int→"integer"`……）翻译成 OpenAI schema。**没有默认值的参数自动进 `required`**，仅此而已。

> 想看 `inspect` 怎么用、想知道为什么本章选"运行时反射"而不是 pydantic 那种"编译期缓存"的工业方案，看本节结尾的 **扩展阅读 · inspect 与编译时 vs 运行时**。

## 极简实现：80 行以内

```python
import inspect
from typing import Any, Callable

class ToolRegistry:
    _TYPE_MAP = {
        str: "string", int: "integer", float: "number",
        bool: "boolean", list: "array", dict: "object",
    }

    def __init__(self) -> None:
        self._funcs: dict[str, Callable] = {}
        self._descs: dict[str, str] = {}

    # ① 装饰器：注册函数
    def tool(self, description: str):
        def deco(func):
            self._funcs[func.__name__] = func
            self._descs[func.__name__] = description
            return func
        return deco

    # ② 自动生成 schema 列表
    def to_schemas(self) -> list[dict]:
        out = []
        for name, func in self._funcs.items():
            sig = inspect.signature(func)
            properties, required = {}, []
            for pname, p in sig.parameters.items():
                properties[pname] = {
                    "type": self._TYPE_MAP.get(p.annotation, "string"),
                    "description": f"参数 {pname}",
                }
                if p.default is inspect.Parameter.empty:
                    required.append(pname)
            out.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": self._descs[name],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                },
            })
        return out

    # ③ 按工具名调度
    def invoke(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._funcs:
            return f"未知工具: {name}"
        try:
            return str(self._funcs[name](**args))
        except Exception as e:
            return f"工具 {name} 执行出错: {e}"
```

够你本章用了。第5章我们会把它再扩展（异步执行 / 参数校验 / 工具集分组），但现在**不需要**。

## 设计上的几个取舍

### 取舍 1：description 必填，不读 docstring

很多框架会去解析 docstring 自动当 description。我们今天**故意**让 description 写在装饰器里：

```python
@registry.tool("查询指定城市的当前天气")    # ← 显式写
def get_weather(city: str) -> str:
    """获取天气。"""                       # ← 不读这个
```

为什么？因为 docstring 经常写得"对人类讲"，而 LLM 看的 description 经常需要更**面向调用决策**（"什么时候该用我"）。强制显式写一份给 LLM 看，避免歧义。

### 取舍 2：所有工具返回 `str`

```python
def calculator(expr: str) -> str:
    return str(eval(expr))    # ← 强转字符串
```

为什么？因为 `tool` 消息的 `content` 字段就是字符串。返回 `dict` / `int` 你最后还得 `json.dumps`。统一约定为 `str`，调用方少踩一个坑。

### 取舍 3：异常被捕获、转成字符串返回

```python
def invoke(self, name, args):
    try:
        return str(self._funcs[name](**args))
    except Exception as e:
        return f"工具 {name} 执行出错: {e}"
```

为什么？因为**工具失败不应该让整个 Agent 崩**。把错误转成字符串塞回 messages，**让模型自己看到错误，自己决定下一步**（重试 / 换参数 / 放弃）。

> 这是 Coding Agent 健壮性的关键 design——你会在第5章工具集和第6章整合里反复看到。

## 一些可能的扩展（今天不做）

- 参数 enum：`city: Literal["北京", "上海"]` → schema 自动生成 enum
- 异步工具：`async def` 函数 → `await registry.ainvoke(...)`
- 工具命名空间：`@registry.tool("...", group="git")`
- pydantic 模型作为参数类型，自动生成嵌套 schema

这些**不是本章必须**的。第5章 / 第6章在真做 Coding Agent 时再加。

## 动手试试

运行 `demo_07_tool_registry.py`：

```bash
python demo_07_tool_registry.py
```

它会：
1. 注册 3 个工具
2. **打印自动生成的 schemas**——你能看到 inspect 推出来的类型对不对
3. 跟 LLM 跑一次完整 function calling，让模型同时调三个工具

## 小结

| 概念 | 一句话理解 |
|------|-----------|
| ToolRegistry | "装饰器 + 反射"做出来的工具注册表 |
| `@registry.tool(desc)` | 一行注册一个工具 |
| `to_schemas()` | 自动从函数签名生成 OpenAI schema |
| `invoke(name, args)` | 按名分发执行，异常自动捕获返回字符串 |
| 关键设计 | description 必填 / 工具返回 str / 异常不上抛 |

---

> ### 📎 扩展阅读 · 装饰器脱糖（本章主线之外，按需展开）
>
> 这一节解决一个疑惑：`@registry.tool("...")` 这一行到底被 Python 翻译成了什么。
> 不影响你用 ToolRegistry，但讲到这里有同学想往下挖一层，可以读。
>
> **① 不带参数的装饰器：`@deco`**
>
> ```python
> @deco
> def f(): ...
>
> # 完全等价于
> def f(): ...
> f = deco(f)          # 把函数自己传给 deco，把 deco 的返回值赋回 f
> ```
>
> **② 带参数的装饰器：`@deco(args)`**
>
> ```python
> @registry.tool("查询天气")
> def get_weather(city: str) -> str: ...
>
> # 完全等价于
> def get_weather(city: str) -> str: ...
> get_weather = registry.tool("查询天气")(get_weather)
> #             └────────┬────────┘
> #                      └─ 这是一次"普通函数调用"，返回值才是真正的装饰器
> ```
>
> 也就是说，**带参装饰器是两层函数调用**：
>
> ```python
> def tool(self, description: str):    # 第一层：吃 description
>     def deco(func):                  # 第二层：吃函数本体
>         self._funcs[func.__name__] = func
>         self._descs[func.__name__] = description
>         return func                  # 注意：返回的还是原函数，不替换
>     return deco
> ```
>
> **三句话总结，装饰器对你来说就再没有秘密：**
>
> 1. **`@deco` 等价于 `func = deco(func)`**，仅此而已。
> 2. **带参装饰器是"先调用一次、再返回真正的装饰器"**，所以 `@registry.tool("...")` 比 `@deco` 多一对括号。
> 3. **装饰器可以"假装什么都没干"**——`return func` 把原函数原封不动还回去，副作用只是在 registry 里偷偷登记了一下。
>
> 这意味着 `get_weather()` 还是 `get_weather()`，你照常调它；同时 `registry` 已经知道它的存在了。**没有魔法**，只有作用域 + 闭包。
>
> 想再深一点：`functools.wraps`（保留被装饰函数的 `__name__` / `__doc__`）、装饰器叠加顺序（**离函数最近的先生效**）、类装饰器（`__call__`）——这些等你写真实框架时再看。

---

> ### 📎 扩展阅读 · `inspect` 与编译时 vs 运行时（本章主线之外，按需展开）
>
> 这一节回答两个问题：① `inspect.signature()` 到底从函数里"反射"出了什么；② 工业框架为什么有些不用 `inspect`，改在导入期就把 schema 缓存好。
>
> #### 一、`inspect.signature()` 在反射什么
>
> ```python
> import inspect
>
> def get_weather(city: str) -> str:
>     ...
>
> sig = inspect.signature(get_weather)
> for pname, param in sig.parameters.items():
>     print(pname, param.annotation, param.default)
>
> # city <class 'str'> <Parameter.empty>
> ```
>
> 拿到这三样信息（参数名、类型注解、默认值），按一张映射表翻成 OpenAI schema 即可：
>
> | 函数签名 | OpenAI schema |
> |---|---|
> | `city: str` | `properties.city.type = "string"` |
> | `count: int` | `properties.count.type = "integer"` |
> | `score: float = 0.5` | `properties.score.type = "number"`，**不在 required 里**（有默认值） |
> | `flag: bool` | `properties.flag.type = "boolean"` |
>
> 关键约定：**默认值 `inspect.Parameter.empty` ⇨ 该参数进 `required`**。这就是为什么你不用手写 required 列表。
>
> #### 二、编译时 vs 运行时：什么时候把 schema 算出来
>
> `inspect.signature()` 是**运行时反射**——程序跑起来、`to_schemas()` 被调用的那一刻，才现场读函数签名。这是本章方案。
>
> 工业框架还有另一条路：**编译时（更准确：导入期/静态期）取 schema**——程序刚 `import` 这个模块时，就把所有工具的 schema 算好缓存，之后 `to_schemas()` 直接还缓存。
>
> | 维度 | 运行时反射（本章用法） | 编译时/导入期取 schema |
> |---|---|---|
> | 时机 | `to_schemas()` 被调用时现场算 | 导入模块时算一次，之后还缓存 |
> | 实现 | `inspect.signature(func)` | AST 解析 / `typing.get_type_hints` + 缓存 / `pydantic.TypeAdapter` |
> | 优点 | 简单、对动态生成的函数和 lambda 也好使 | 性能好、能在程序启动时就发现 schema 错误 |
> | 缺点 | 每次都反射，有开销；类型错只在第一次跑到才暴露 | 实现复杂、对动态注册不友好 |
> | 典型代表 | 本章的 `ToolRegistry`、LangChain 老版的 `Tool` | `pydantic` 字段、FastAPI 路由参数、某些 IDE 插件读 `.pyi` |
>
> 工程化对照（**仅作参考，本章不引入 pydantic**）：
>
> ```python
> from pydantic import BaseModel, TypeAdapter
>
> class GetWeatherArgs(BaseModel):
>     city: str
>
> # 类一定义完，schema 就算好了，之后调用是 O(1) 还缓存
> SCHEMA = TypeAdapter(GetWeatherArgs).json_schema()
> ```
>
> **为什么本章选运行时方案？**
>
> 1. 教学上更直白：你能亲眼看到 `inspect.signature` 在干活，没有"模块导入魔法"挡在中间。
> 2. 工具数量少：本章 demo 一共也就 3-5 个工具，反射开销可以忽略。
> 3. 不锁死框架：用 `inspect` 谁都能读懂；上 pydantic 就要先讲一遍 pydantic。
>
> **什么时候该升级到编译时方案？**
>
> - 工具数量上百，每次调度都要拼 schema 时（比如一个大型 Coding Agent 暴露上百个 git/文件/搜索工具）。
> - 想在 CI / 启动期就拦截"参数类型写错"的工具，而不是等用户问到才报错。
> - 已经在用 pydantic / FastAPI 这类带 schema 能力的框架，顺势复用。
>
> 第 5 章我们做 Coding Agent 工具集时工具会变多，但本课程**仍坚持运行时方案**——把工程化优化的边界留给你的真实项目。

---

下一节：注册表有了，怎么把它放进**循环**里跑起来——**最小 Agent Loop 的 5 个核心点**。
