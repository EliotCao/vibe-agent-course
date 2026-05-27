# 第 25 节 · 工具的设计哲学：4 个关键选择

## 一句话回答

> **工具的设计不是"实现功能"就完了，而是"帮 LLM 不犯错"。** 今天讲 4 个最关键的设计选择，每一个都对应一类典型的 LLM 翻车场景。

## 选择 ① edit 用 old_content / new_content，不用行号

![edit 为什么用 old new 不用行号](./images/25-edit-old-new.png)

### 翻车场景

假设 edit 接收 `line_number` 参数：

```python
# 第 1 步：在第 5 行前面插入新函数（3 行）
edit_at_line("main.py", line=5, mode="insert_before", content="...")
# → 此时第 12 行 = 原文件的第 9 行

# 第 2 步：修改"原本的第 12 行"
edit_at_line("main.py", line=12, mode="replace", content="...")
# → 但 LLM 不知道行号偏移了，改错了位置
```

### 解法

接收 `old_content` / `new_content`，**按内容定位**：

```python
edit("main.py", 
     old_content="def greet():\n    print('hi')",
     new_content="def greet():\n    print('hello')")
```

不管前面增删多少行，目标文本永远精确。

### 唯一性约束

`old_content` **必须在文件中只出现一次**。这是为什么？

```
old_content = "return"
```

文件里 30 个 `return`——LLM 不知道改哪个。**强制要求唯一**就能逼模型加足够的上下文。

```
old_content = "def add(a, b):\n    return a + b"
```

这就唯一了。

> 这个约束是 Cursor / Claude Code 的 edit 工具几乎一致的设计。

## 选择 ② bash 工具的四道安全闸门

![bash 工具的四道安全闸门](./images/25-bash-safety.png)

`bash` 是最强大也最危险的工具——能跑任意命令。**LLM 一不小心就能把你仓库删了**。

四道闸门是底线：

| 闸门 | 长什么样 | 为什么 |
|---|---|---|
| **超时** | `timeout=30` | LLM 偶尔会写 `while True`，没超时直接挂死 |
| **输出截断** | `max_output=50000` | 一次 `find /` 几百万行返回会爆 messages |
| **工作目录限定** | `cwd=workdir` | 防止跑到 `~` 或 `/etc` 那种地方动东西 |
| **危险命令拦截** | 黑名单 regex | `rm -rf /`、`sudo`、远程脚本下载、fork 炸弹 |

### 黑名单不是终极方案

我们的 `bash.py` 里有这样一段：

```python
DANGER_PATTERNS = [
    r"\brm\s+-rf\s+/",
    r"\bsudo\b",
    r"\b(curl|wget)\s+.*\|\s*(sh|bash)",
    ...
]
```

这是**最低限度**。真正生产级的方案是：
- 容器化（Docker / Firejail）—— Agent 跑在隔离的小盒子里
- 命令白名单（只允许 `python` / `pytest` / `git` 等明确命令）
- 文件系统 read-only 挂载（除了 workdir）

**今天我们做最低版**，让你看到"边界在哪"。

## 选择 ③ 读类工具大胆调，写类工具严防死守

![读类工具大胆调 写类工具严防死守](./images/25-read-vs-write.png)

工具分两类，**对它们的设计心态完全不同**：

| | 读类（read / list_dir / glob / grep） | 写类（write / edit / bash） |
|---|---|---|
| 失败成本 | 低（重试就行） | 高（可能写坏文件 / 删错东西） |
| 副作用 | 无 | 有（文件系统改了） |
| 模型策略 | LLM 可以"试错" | 每次必须有明确意图 |
| 设计心态 | 友好 / 容错 / 信息丰富 | 严格 / 校验 / 可回滚 |

### 读类工具的设计要点

- **路径不存在 → 友好报错**（不要 raise，让模型看到"文件不存在: xxx" 自己处理）
- **大文件 → 自动截断**（默认 100KB，避免一次塞满 messages）
- **输出带行号**（让 LLM 后续能精确引用）

### 写类工具的设计要点

- **write**: 默认拒绝覆盖已有文件（要 `overwrite=True` 才能覆盖）
- **edit**: 强制 old_content 唯一
- **bash**: 4 道闸门
- **所有写类工具**: 失败时 **不要 raise**，把错误转成字符串返回 —— 让 LLM 能看到错误自己重试

## 选择 ④ 工具失败 → 字符串返回，不抛异常

```python
def edit(path, old_content, new_content):
    if not os.path.isfile(path):
        return f"❌ 文件不存在: {path}"   # ← 不 raise
    if count == 0:
        return f"❌ 未找到匹配内容..."    # ← 不 raise
    ...
```

**为什么**？

如果 raise，整个 Agent Loop 就崩了。但如果返回字符串：

```
LLM 调 edit("a.py", "old", "new")
↓
工具返回："❌ 未找到匹配内容: a.py"
↓
LLM 看到错误 → "啊我搞错了，先 read 看看再来" → 自己纠正
```

**让模型自己看到错误，自己决定下一步。**这是 Day2 第 8 节就讲过的"工具异常兜底"原则——Day5 的所有工具一律遵守。

## 把这 4 条总结成一句话

> **工具的输出是给 LLM 看的 UI**——用了什么参数、输出什么格式、怎么报错，全部都是"给 LLM 看"，不是给人看。

## 一些常见的"误用工具"案例

| 误用 | 现象 | 怎么防 |
|---|---|---|
| LLM 用 write 覆盖已有文件 | 整个文件被替换 | `write` 默认拒绝覆盖 |
| LLM 用 edit 改文件，但 old_content 写错 | 静默失败 | 唯一性约束 + 友好报错 |
| LLM 用 bash 跑 `find /` | 几百万行返回爆 messages | 输出截断 + 工作目录限定 |
| LLM 反复同样调用同一工具 | 死循环 | Day3 已经讲了：max_iters + 重复检测 |

## 设计思路总结

写好 Coding Agent 的工具，3 件事：

1. **默认安全**：写类工具默认拒绝危险操作（覆盖、删除、远程执行）
2. **失败可读**：错误转字符串返回，含具体原因 + 修复建议
3. **输出友好**：带行号 / 含状态码 / 含元数据，让下一个工具的 LLM 调用方便

跟 04-my-agent 的工具集对照看，[`examples/04-my-agent/tools/impl/`](../../examples/04-my-agent/tools/impl/) 全部 9 个工具都遵守这 3 条。

## 动手试试

```bash
python demo_25_design_philosophy.py
```

会跑 3 个对比演示：edit 唯一性约束、行号偏移问题、bash 危险命令拦截。

## 小结

| 设计选择 | 防什么翻车 |
|------|-----------|
| edit 用 old/new | 防多步编辑后行号偏移 |
| edit 唯一性约束 | 防一次修改改了不该改的多处 |
| bash 4 道闸门 | 防仓库被删 / 输出爆 / 死循环 |
| 失败返回字符串 | 防 Agent Loop 崩溃，让模型自己纠错 |

---

理论结束。下面 lab：
- Part 1（60min）：实现 `read` / `list_dir` / `grep`（读类，失败成本低）
- Part 2（60min）：实现 `write` / `edit` / `bash`（写类，严防死守）
- 末尾 5min：Git 速通 5 个命令把代码推到 CNB
