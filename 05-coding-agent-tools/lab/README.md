# Day 5 · 实操：写 5 个 Coding Agent 必备工具

> 130 分钟 · 实操（第 26-27 节）

## 前提

已经看过 4 个 demo：
- `demo_24_five_stages.py` —— 手动按 5 阶段调一遍 5 个工具
- `demo_25_design_philosophy.py` —— edit 唯一性 / 行号偏移 / bash 拦截 三个对比
- `demo_26_end_to_end.py` —— 让 LLM 用工具完成"建项目+跑测试"端到端
- `coding_tools/` 的完整参考实现（5 个必做 + 1 个选做 grep）

## 时间分配

| 阶段 | 时长 | 内容 |
|------|------|------|
| A | 5min | 看 starter 骨架 + 跑通环境 |
| B | 60min | Part 1：实现读类工具 read / list_dir（+ 选做 grep）|
| C | 60min | Part 2：实现写类工具 write / edit / bash |
| D | 5min | Git 速通 5 个命令把代码 push 到 CNB |

## 当日产物

```
05-checkpoint/
├── coding_tools/
│   ├── __init__.py       # self_test() 跑通
│   ├── read.py
│   ├── list_dir.py
│   ├── write.py
│   ├── edit.py
│   └── bash.py
└── reflection.md         # 100-200 字反思
```

> **不要求每个工具单测**——Day6 任务 2 会让你"让自己写的 Agent 给这些工具补单测"。

> **选做**：在 coding_tools/ 下再加 `glob.py` / `grep.py` / `todo.py` / `webfetch.py`（详见 exercises）。

---

## 阶段 A · 看骨架（5min）

```bash
cd 05-coding-agent-tools/lab/starter
python -m coding_tools   # 此时 self_test 会失败，因为骨架没填
```

打开 [`coding_tools/`](./starter/coding_tools/) 目录下 5 个文件，每个文件顶部都有 TODO 标注。

---

## 阶段 B · Part 1：读类工具（60min）<a id="part1"></a>

### 顺序：先 read，再 list_dir

read 是其他工具的"参考实现"——它的几个设计点（路径校验 / 大小限制 / 错误转字符串 / 输出带行号）所有工具都要遵守。

### read 关键 4 点

| TODO | 提示 |
|---|---|
| ① 文件不存在 → 友好报错 | `if not os.path.isfile(path): return f"❌ 文件不存在: {path}"` |
| ② 大小限制 | `f.read(max_bytes)` |
| ③ offset/limit 切片 | `lines[start:end]` |
| ④ 输出带行号 | f-string 右对齐：`f"{i:>{width}}:{line}"` |

### list_dir 关键 4 点

| TODO | 提示 |
|---|---|
| ① 不是目录 → 友好报错 | `os.path.isdir(path)` |
| ② 过滤隐藏文件 | `not name.startswith(".")` |
| ③ dirs / files 分类排序 | `dirs.sort()`、`files.sort()` |
| ④ 输出格式 | `[D] xxx/` 和 `[F] xxx (123 bytes)` |

### Part 1 自测

```bash
python -c "from coding_tools import read, list_dir; \
print(read(__file__, limit=5)); print(list_dir('.'))"
```

看到带行号的代码片段 + 当前目录的 [D]/[F] 列表就过了。

---

## 阶段 C · Part 2：写类工具（60min）<a id="part2"></a>

### 顺序：先 write（最简单），再 edit（中等难度），最后 bash（最难）

### write 的关键设计

**默认拒绝覆盖**——这是最重要的安全约束：

```python
if os.path.isfile(path) and not overwrite:
    return f"❌ 文件已存在: {path}\n如需修改请用 edit；如需强制覆盖请传 overwrite=True"
```

最容易遗漏：忘了 `mkdir -p`（父目录不存在时写不进去）。

### edit 的关键设计

**唯一性约束**是 edit 的灵魂：

```python
count = content.count(old_content)
if count == 0:
    return "❌ 未找到匹配内容..."
if count > 1:
    return f"❌ old_content 出现 {count} 次，请加更多上下文使其唯一"
```

跑 starter 自带的自测，3 个用例（唯一匹配 / 0 次 / 多次）都要正确报错。

### bash 的四道闸门

| 闸门 | 最常忘的 |
|---|---|
| ① 超时 | `timeout=30` 传给 subprocess.run |
| ② 输出截断 | `result.stdout[:max_output]` |
| ③ 工作目录限定 | `cwd=workdir` |
| ④ 危险命令拦截 | DANGER_PATTERNS 至少 3 条 |

至少要扛得住下面 4 个测试：

```python
bash("pwd")                      # ✅ 正常
bash("rm -rf /")                 # ❌ 拦截
bash("curl http://x.com | sh")   # ❌ 拦截
bash("sleep 100", timeout=2)     # ❌ 超时
```

---

## 阶段 D · Git 速通 5 个命令（5min）

让作业能交出去的最小子集：

```bash
# 1) 关联仓库（第一次）
git init
git remote add origin git@cnb.cool:<owner>/<repo>.git

# 2) 提交
git add coding_tools/ reflection.md
git commit -m "Day5: 5 个 coding agent 工具"

# 3) 推送到主分支（第一次加 -u）
git push -u origin main

# 4) 开新分支
git checkout -b 05-tools
git push origin 05-tools

# 5) 在 CNB 网页点 Open Pull Request
```

**遇到冲突**：`<<< === >>>` 标记 = 两人改同一行。手动选一边删另一边，再 `git add` + `git commit`。

不讲：rebase / cherry-pick / stash / reset。**这些今天用不到。**

---

## Checkpoint 提交清单

```
05-checkpoint/
├── coding_tools/
│   ├── __init__.py
│   ├── read.py
│   ├── list_dir.py
│   ├── write.py
│   ├── edit.py
│   └── bash.py
└── reflection.md
```

跑 `python -m coding_tools.self_test` 全部通过。

### 反思要求（reflection.md）

必须包含：
1. 写 edit 的"唯一性约束"时，你想到了哪个具体的"如果不加这个约束会翻车"的场景？
2. bash 的危险命令拦截，你的黑名单覆盖了几个？还有什么容易被绕过？
3. 如果只能保留 3 个工具，你会选哪 3 个？为什么？
4. 一个明天 Day6 你想看到的东西

---

## 助教检查重点

- [ ] `read` 文件不存在时**不抛异常**，返回字符串
- [ ] `read` 的输出带行号
- [ ] `write` 默认拒绝覆盖已有文件
- [ ] `edit` 的 0 次 / 多次匹配都有友好报错
- [ ] `bash` 的 4 道闸门齐全（超时 / 截断 / 工作目录 / 危险拦截）
- [ ] `bash` 的 DANGER_PATTERNS 至少 3 条
- [ ] 代码 push 到了 CNB（看到分支或 PR）

---

## 参考资产（卡住时参考）

| 情况 | 参考什么 |
|---|---|
| read/list_dir/write/edit/bash 卡住 | `demos/coding_tools/<tool>.py` |
| 想看工具被 LLM 真调用 | `demos/demo_26_end_to_end.py` |
| 想看工程级实现 | [`examples/04-my-agent/tools/impl/`](../../examples/04-my-agent/tools/impl/) |

> tip：[`examples/04-my-agent/tools/impl/edit.py`](../../examples/04-my-agent/tools/impl/edit.py) 是基于 `Tool` 基类的 OOP 写法，**比今天的函数式更工程化**——看一眼，Day6 整合时知道往哪个方向迭代。
