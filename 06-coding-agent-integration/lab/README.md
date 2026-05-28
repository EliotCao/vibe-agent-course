# Day6 · 实操指南

> **核心任务**：把 Day1-Day5 写的 6 个零件组装成一个完整的 Coding Agent，然后用它跑 3 个真实任务。

---

## 时间规划（约 130 分钟）

| 阶段 | 时间 | 内容 |
|------|------|------|
| A · 看参考 | 15 min | 跑 `demo_30` 理解组装过程 |
| B · 填空实现 | 40 min | 在 `my_coding_agent/agent/agent.py` 里填 4 个 TODO |
| C · 跑 3 个任务 | 30 min | 建项目+测试 / 修 bug / 刁难题 |
| D · 对比&反思 | 25 min | 跑 `demo_31`，对比你的实现和参考实现 |
| E · 提交 | 20 min | comparison.md + git push |

---

## 阶段 A · 看参考实现（15 分钟）

```bash
cd 06-coding-agent-integration/lab/my_coding_agent
python main.py  # 跑一轮简单对话，确认环境 OK
```

然后跑 walkthrough：

```bash
cd 06-coding-agent-integration/lab/demos
python demo_30_integration_walkthrough.py
```

观察输出：6 个零件各自独立 → Agent Loop 一层循环粘合。

---

## 阶段 B · 填空实现（40 分钟）

打开 `my_coding_agent/agent/agent.py`，有 **4 个 TODO**：

| # | 要点 | 参考 |
|---|------|------|
| 1 | 实例化 6 个零件 | Day2 ToolRegistry + Day4 ContextManager/Memory + Day5 build_registry |
| 2 | 从 Memory 召回 → 注入 system 消息 | Day4 demo_20 |
| 3 | Agent Loop 核心循环 | Day2 demo_09 mini_agent |
| 4 | 循环结束返回最终回答 | — |

### 自检清单

- [ ] `python main.py` 能正常启动 REPL
- [ ] 输入"帮我列一下目录"→ Agent 调 list_dir → 返回文件列表
- [ ] 输入"帮我建一个 hello.py 并写入 print('hi')"→ Agent 调 write → 文件实际被创建
- [ ] 超过 30 条消息后触发压缩（可以手动测或等阶段 C）

---

## 阶段 C · 3 个真实任务（30 分钟）

用你自己的 Agent（启动）跑以下任务：

### 任务 1：建项目 + 跑测试
> "请创建 calculator.py（含 add/subtract 函数），再创建 test_calculator.py（用 assert 写测试），最后跑 python -m pytest -v"

### 任务 2：修 bug
先手动创建一个 `buggy.py`：
```python
def greet(name):
    return f"Hello, {namee}!"

def add(a, b):
    return a - b  # 故意写反
```
然后让 Agent：
> "读 buggy.py，找出所有 bug 并修复，跑一下确认没错"

### 任务 3：刁难
> "帮我访问 https://example.com 并把网页保存到 page.html"

观察 Agent 在没有网络工具时如何回应——是编造？还是诚实拒绝？还是用 bash + curl 变通？

---

## 阶段 D · 对比&反思（25 分钟）

```bash
python demo_31_three_tasks.py
```

写一份 `comparison.md`：

1. 你的实现 vs 参考实现，**哪一步卡住了、为什么**
2. Memory 是否触发过召回？什么时候有用？
3. ContextManager 压缩是否触发？如果没触发说明对话轮数没到——正常
4. 一个意外发现（必填）

---

## 阶段 E · 提交（20 分钟）

```bash
cd ~/vibe-agent-course
git add 06-coding-agent-integration/lab/my_coding_agent/
git add 06-coding-agent-integration/comparison.md
git commit -m "day6: 完成 Coding Agent 整合"
git push
```

---

## 助教检查重点

1. `my_coding_agent/agent/agent.py` 的 4 个 TODO 全部填完
2. REPL 能正常运行
3. 任务 1 建项目 + 测试通过
4. comparison.md 有真实内容（不是空话）
