# Day 5 · 课后练习题

> 课后完成。每题 30-90 分钟。下次课前提交。

## 必做（3 题）

### 练习 5.1 · 给 Coding Agent 加 grep（选做扩展）

实现一个 `grep` 工具，递归在目录里搜索包含某个正则的行：

```python
def grep(pattern: str, path: str = ".", file_glob: str = "*", max_matches: int = 100) -> str:
    """返回每条匹配的 path:lineno: content 格式。"""
    ...
```

要求：
1. 跳过 `.git / node_modules / __pycache__ / .venv` 等"垃圾目录"
2. `file_glob` 至少支持 `*.ext`（按后缀过滤）
3. `max_matches` 上限达到时截断
4. 路径不是目录 → 友好报错
5. 正则非法 → 友好报错（不崩）

参考 [`demos/coding_tools/grep.py`](../lab/demos/coding_tools/grep.py)。

提交：
- `grep.py`
- 一段日志：在你的 05-checkpoint 目录跑 `grep("def ", file_glob="*.py")` 的输出
- 50 字反思：为什么 grep 比 bash + grep 命令好（提示：跨平台 / 不依赖 shell）

---

### 练习 5.2 · bash 黑名单的"对抗赛"

你的 bash 工具有一份 DANGER_PATTERNS。同学 A 写的 bash 是 LLM，同学 B 写的 prompt 是"绕过 A 的拦截"。

**实战题**：自己扮演两个角色：

1. 拿你 lab 写的 bash，跑 5 条**你想绕过**自己拦截的命令（提示：用变量替换、字符拼接、base64 编码、多行命令、git hooks……）
2. 看哪些命中、哪些没命中
3. 改进 DANGER_PATTERNS，把没命中的也拦下

提交：
- 改造前后的 DANGER_PATTERNS
- 5 条对抗命令的命中表
- 100 字反思：黑名单为什么永远不可能完美？什么时候应该上"白名单 + 沙箱"？

---

### 练习 5.3 · 用你的 5 个工具完成一个真任务

不用 LLM，**自己手动**调用 5 个工具完成下面这个任务，把每一步贴出来：

**任务**：在临时目录里建一个 Python 项目，包含：
- `app.py` 一个简单的 Flask hello world
- `test_app.py` 测试 / 路由
- `requirements.txt` 列依赖
然后 `pip install` + `pytest` 跑通。

提交一份 `task.md`，按下面格式：

```markdown
# 用 5 个工具手动跑一个真任务

## Step 1: list_dir(workdir)
（输出）

## Step 2: write(workdir + '/app.py', ...)
（输出）

...

## Step N: bash('pytest', workdir)
（输出）

## 总结
（你跑了几步？哪一步出错了？怎么修的？）
```

> 这道题让你**当一回 LLM 自己**——感受"模型每一步要看什么、决定什么"。

---

## 选做（任选 1 题）

### 练习 5.4 · webfetch 工具

实现一个 `webfetch(url)` 工具，抓取一个 URL 的内容，返回前 N 字节的纯文本：

```python
def webfetch(url: str, max_bytes: int = 10000) -> str:
    """抓 URL，返回 HTML 转纯文本的前 N 字节。"""
    ...
```

要求：
- 用 `urllib.request` 不引入 requests
- HTML 用最朴素的方式去标签（`re.sub(r'<[^>]+>', '', html)`）
- 超时 10 秒
- 域名/协议黑名单（不允许 `file://`、`ftp://`，不允许内网 IP）

提交：
- `webfetch.py`
- 跑通三个 URL（example.com / wikipedia / 你自己的博客）
- 50 字反思：为什么不直接用 bash 调 curl？（提示：跨平台 / 安全约束）

---

### 练习 5.5 · 把 5 个工具搬进 Day3 ReAct Agent

把你 Day3 写的 ReAct 范式 Agent + 今天的 5 个工具拼起来：

```python
# 你 Day3 的 agent_react.py，把工具集换成 day5 的
from coding_tools import build_registry
agent = ReActAgent(tools=build_registry())
```

跑一个真任务："读 README.md 的前 20 行，告诉我课程 Day1-Day5 各讲了什么"。

观察：
- ReAct Agent 用 5 个工具时表现如何？
- 比 Day2 的 Function Calling Agent 多花多少 token？

提交：
- 改造后的 agent
- 一段日志
- 100 字反思：ReAct + Coding 工具集 vs Function Calling + Coding 工具集，你更倾向哪个？

> Day6 整合时你需要做出这个选择。

---

## 评分标准

- 必做每题 5 分（共 15 分）
- 选做每题 5 分（加分上限 10 分）
- 反思深度 5 分

---

## 答案要点（仅老师参考）

> ⚠️ **学生版本应删除此部分**。

### 5.1
- 基础版本就是参考实现的样子
- 加分项：学生意识到 grep 在 Windows / macOS / Linux 都能跑，bash + grep 在 Windows PowerShell 上得换 Select-String

### 5.2
- 常见的绕过：
  1. `R=rm; $R -rf /`（变量拼接）
  2. `bash -c "rm -rf /"`（嵌套 bash）
  3. base64 编码再 `base64 -d | sh`
  4. `git config core.hooksPath /evil`（用 git hooks 间接执行）
- 改进黑名单很快就跟不上——这正是反思的目标
- 加分项：学生提议"白名单 + 容器"

### 5.3
- 一般 5-8 步能跑通
- 学生最常翻车：
  - 忘了 mkdir -p（write 失败）
  - edit 的 old_content 写错（字符没对齐 / 空格不一致）
  - bash 跑 pip install 时 timeout=30 不够（要传更长的）

### 5.4
- 加分项：学生意识到 HTML 转纯文本是大坑（最低限度去标签 / 用 BeautifulSoup / 用 readability）
- 黑名单要拦内网（`localhost / 127.0.0.1 / 10.x / 192.168.x / 169.254.x` —— SSRF 防御）

### 5.5
- ReAct + Coding 工具集会有解析翻车风险（Day3 已经讲过）
- token 消耗 ReAct 比 Function Calling 高 30-50%（每步多 Thought 输出）
- 工业 Coding Agent 几乎都用 Function Calling，但 system prompt 里**鼓励 Thought 输出**作为内容
