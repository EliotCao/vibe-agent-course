# Example: context_builder 笔记



## Source 类设计

### 当前实现

```python
from enum import StrEnum, auto


class Source(StrEnum):
    USER = auto()
    SYSTEM = auto()
    MEMORY = auto()
    TOOL = auto()
    ASSISTANT = auto()
```



### `StrEnum` 是什么

`StrEnum` 是 Python **3.11 新增**的标准枚举类型。它在 `(str, Enum)` 基础上做了 3 件事：

1. 强制成员类型必须是字符串

2. `__str__` 返回纯 value

3. 默认 `auto()` 生成小写成员名

   ```python
   from enum import auto
   
   class Source(StrEnum):
       USER = auto()   # 自动 = "user"
       TOOL = auto()   # 自动 = "tool"
   ```

   —— 这是 `StrEnum` 独有的便利，省去手写字符串。



## @dataclass 装饰器

`@dataclass` 是 Python 3.7+ 内置的一个**类装饰器**，加在类上之后，Python 会**自动帮你生成 `__init__`、`__repr__`、`__eq__` 这些样板方法**，让你只用写「这个类有哪些字段」就够了。



### 1. 不用 `@dataclass` 时你得这么写

假设你想表达「一个候选信息包，有 content / source / relevance 三个字段」：

```python
class ContextPacket:
    def __init__(self, content, source="user", relevance=0.5):
        self.content = content
        self.source = source
        self.relevance = relevance

    def __repr__(self):
        return (f"ContextPacket(content={self.content!r}, "
                f"source={self.source!r}, relevance={self.relevance!r})")

    def __eq__(self, other):
        if not isinstance(other, ContextPacket):
            return NotImplemented
        return (self.content == other.content
                and self.source == other.source
                and self.relevance == other.relevance)
```

啰嗦、重复、容易写漏。



### 2. 用 `@dataclass` 后

```python
from dataclasses import dataclass

@dataclass
class ContextPacket:
    content: str
    source: str = "user"
    relevance: float = 0.5
```

**就这 4 行。** Python 在导入时偷偷帮你把上面那一大坨方法都生成好了。

效果：

```python
from dataclasses import dataclass

class ContextPacketWithoutDataclass:
    def __init__(self, content, source="user", relevance=0.5):
        self.content = content
        self.source = source
        self.relevance = relevance

    def __eq__(self, other):
        if not isinstance(other, ContextPacket):
            return NotImplemented
        return (self.content == other.content
                and self.source == other.source
                and self.relevance == other.relevance)

@dataclass
class ContextPacket:
    content: str
    source: str = "user"
    relevance: float = 0.5


if __name__ == '__main__':
    p1 = ContextPacketWithoutDataclass(content="hello", source="memory", relevance=1)
    print(p1)   # <__main__.ContextPacketWithoutDataclass object at 0x1044fe950>

    p2 = ContextPacket(content="hello", source="memory", relevance=2)
    print(p2)   # ContextPacket(content='hello', source='memory', relevance=2)

    p2_1 = ContextPacket(content="hello", source="memory", relevance=2)
    print(p2 == p2_1)   # True
```



### 3. 它具体生成了哪些方法

| 方法                                      | 默认是否生成                                | 作用                                      |
| ----------------------------------------- | ------------------------------------------- | ----------------------------------------- |
| `__init__`                                | ✅                                           | 用字段顺序创建对象                        |
| `__repr__`                                | ✅                                           | 打印对象时显示 `ClassName(field=值, ...)` |
| `__eq__`                                  | ✅                                           | 字段全相等就认为对象相等                  |
| `__hash__`                                | 默认禁用，可开                              | 让对象能放进 set / 当 dict key            |
| `__lt__` / `__le__` / `__gt__` / `__ge__` | 默认不生成，`@dataclass(order=True)` 才生成 | 大小比较                                  |

需要哪些，靠 `@dataclass(...)` 的参数控制：

```python
@dataclass(frozen=True)   # 字段不可改（immutable）
@dataclass(order=True)    # 加上比较方法
@dataclass(slots=True)    # Python 3.10+，省内存
```



### 4. 回到代码中

```python
@dataclass
class ContextPacket:
    """候选信息包：上下文构建的最小单元。"""

    content: str
    source: str = "user"  # user / system / memory / tool / assistant
    relevance: float = 0.5  # 相关性 0.0~1.0
    timestamp: datetime = field(default_factory=datetime.now)
```

- `content: str` —— **必填字段**（没默认值）。
- `source: str = "user"` —— **选填字段**，不传就是 `"user"`。
- `relevance: float = 0.5` —— 同上。
- `timestamp: datetime = field(default_factory=datetime.now)` —— 这里有个**坑点**，重点讲。



#### 为什么要用 `field(default_factory=...)` 而不是 `= datetime.now()`？

错误写法（你可能会本能这么写）：

```python
timestamp: datetime = datetime.now()   # ❌ 大坑！
```

这样写的话，`datetime.now()` **只在类定义时（程序启动时）执行一次**，所有 `ContextPacket` 实例的 `timestamp` 会是**同一个时间** —— 你创建第 100 个包时，它的时间戳还是程序启动那一刻。

正确写法（代码里的写法）：

```python
timestamp: datetime = field(default_factory=datetime.now)   # ✅
```

`default_factory=datetime.now` 表示「**每次创建新实例时再调用一次** `datetime.now()`」，这样每个包的时间戳才是它自己被创建时的时间。

> [!NOTE]
>
> **规律记一下**：`@dataclass` 字段的默认值**不能是可变对象或带副作用的表达式**（比如 `[]`、`{}`、`datetime.now()`、`uuid.uuid4()`）。这种情况一律用 `field(default_factory=...)`。



### 5. 几个常用的进阶招式

```python
from dataclasses import dataclass, asdict

@dataclass(frozen=True)    # 创建后字段不可改（防误改）
class Point:
    x: int
    y: int

if __name__ == '__main__':
    p = Point(1, 2)
    # p.x = 9    ❌ 报错 dataclasses.FrozenInstanceError: cannot assign to field 'x'

    # 转 dict 一行搞定（很常用，比如序列化）
    my_dict = asdict(p)
    print(my_dict)    # {'x': 1, 'y': 2}
```



```python
from dataclasses import dataclass, field

@dataclass
class Bag:
    items: list[str] = field(default_factory=list)   # 同样的坑：list 也得用 factory
```

> [!NOTE]
>
> 因为 **Python 的默认值在函数定义那一刻就被求值一次，之后所有调用都共享同一个对象**。所以必须用 `field(default_factory=list)`



### 6. `__post_init__`

在 `@dataclass` 装饰的类里：

```
调用被装饰的类
   │
   ├─ 1. dataclass 自动生成的 __init__ 执行
   │       └─ 给属性赋值
   │
   └─ 2. __init__ 末尾自动调用 self.__post_init__()
           └─ 在这里跑你写的校验/派生计算
```

> [!IMPORTANT]
>
> 1. 它不是 Python 通用机制，只对 `@dataclass` 装饰过的类生效
>
>    ```python
>    class Foo:
>        def __init__(self):
>            self.x = 1
>        
>        def __post_init__(self):  # 永远不会被自动调用
>            print("never runs")
>    ```
>
> 2. 哪怕被 `@dataclass` 装饰，如果自己重写了 `__init__`，也会“短路”：
>
>    ```python
>    @dataclass
>    class Bad:
>        x: int = 0
>        
>        def __init__(self, x):       # ← 覆盖了 dataclass 自动生成的
>            self.x = x
>        
>        def __post_init__(self):     # ← 永远不会被调用
>            print("never")
>    ```
>
>    正确的做法是：
>
>    ```python
>    @dataclass
>    class Bad:
>        x: int = 0
>        
>        def __init__(self, x):       # ← 覆盖了 dataclass 自动生成的
>            self.x = x
>            if hasattr(self, '__post_init__'):    # 要手动保证在末尾执行
>                self.__post_init__()
>        
>        def __post_init__(self):
>            print("never ?")
>    ```
>
> 3. 异常时机：`__post_init__` 抛异常 = 整个 `__init__` 抛异常 = 对象**没创建成功**。
>
> 4. 继承时的调用链：子类的 `__post_init__` 会覆盖父类的，需要手动调 `super().__post_init__()`：
>
>    ```python
>    @dataclass
>    class Child(Parent):
>        extra: int = 0
>        
>        def __post_init__(self):
>            super().__post_init__()   # ← 别忘了
>            if self.extra < 0:
>                raise ValueError(...)
>    ```



### 7. field

`@dataclass` 看到类里的注解字段时，会自动生成 `__init__` / `__repr__` / `__eq__` / `__hash__` 等方法。`field()` 就是给某个字段提供**额外配置**——告诉 dataclass："针对这个字段，请这样处理"：

```python
from dataclasses import dataclass, field

@dataclass
class Foo:
    a: int                      # 默认行为：进入 init/repr/eq
    b: int = 0                  # 同上，但有默认值
    c: int = field(default=0)   # 同 b，写法更显式
    d: int = field(init=False)  # 不进入 __init__ 参数
```

`field()` 是 dataclass 的"字段配置器"。下面介绍它的常见参数：



#### init

控制是否出现在 `__init__` 参数里。默认为 `True`。

```python
from dataclasses import dataclass, field

@dataclass
class Demo:
    x: int                                  # 必须由调用方传
    y: int = field(init=False, default=0)   # 不允许调用方传

if __name__ == '__main__':
    Demo(x=1)  # ✅ OK
    Demo(x=1, y=2)  # ❌ TypeError: __init__() got an unexpected keyword argument 'y'
```

**生成的 `__init__` 签名差异**：

```python
# 不加 init=False
def __init__(self, content, ..., token_count: int): ...

# 加了 init=False
def __init__(self, content, ...): ...   # token_count 不在参数列表里
```

> [!TIP]
>
> 在实际代码实现中，`token_count` 不应该由调用方决定——它必须由 `content` **算**出来。如果允许传 `ContextPacket("hello", token_count=999)`，调用方就能伪造一个不一致的 token 数，破坏不变量。`init=False` 把"创建权"从外部夺回，交给 `__post_init__` 独占。



#### repr

dataclass 默认生成的 `__repr__` 会列出所有字段，禁用后不包含。



#### compose

是否参与比较。dataclass 默认基于"所有字段相等"判断对象相等。当禁用时，不参与 `__eq__`、`__lt__` 等比较。



#### hash

是否参与哈希。我们看看 `__hash__` 的生成规则：

| 装饰器配置                | `__hash__` 行为                                |
| ------------------------- | ---------------------------------------------- |
| `@dataclass` (默认)       | `__hash__ = None`，**对象不可哈希**            |
| `@dataclass(frozen=True)` | 自动生成 `__hash__`，基于“参与 compare 的字段” |
| `@dataclass(eq=False)`    | 继承 `object.__hash__`（按 id 哈希）           |

> **哈希 = 把任意对象映射成一个固定大小的整数（hash value）**。
>
> ```python
> hash("hello")           # 例如：-5237692791148523989
> hash(42)                # 42
> hash((1, 2, 3))         # 529344067295497451
> hash(Source.USER)       # 某个整数
> ```
>
> 它的核心目的**不是判断相等**，而是**让 Python 能用 O(1) 的代价把对象塞进/找出 `dict` 和 `set`。**