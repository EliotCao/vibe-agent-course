# Day6 · 课后练习

---

## 必做（3 道）

### 6.1 给 Agent 加流式输出

**要求**：修改 `agent.py` 的 `chat` 方法，让最终回答是流式打印（而非一次性输出），使用 `llm.chat_stream()` 的 `on_text` 回调。

**验收标准**：
- REPL 中 Agent 回答时文字逐字出现
- tool_calls 阶段不受影响（仍然是非流式 → 执行工具 → 再流式输出最终答案）

**提示**：
- 只有循环里"不再有 tool_calls"那次才需要走流式
- 之前每轮还需要调用工具的时候，非流式更简单

---

### 6.2 让 Agent 自己给 edit.py 写单测

**要求**：用你自己的 Agent 完成以下任务：

> "请阅读 tools/coding_tools/edit.py，为它写一个 test_edit.py（覆盖正常替换、old_content 不唯一、old_content 不存在 3 种 case），然后跑测试确认全部通过。"

**验收标准**：
- `test_edit.py` 存在且 3 个 case 都通过
- 截图或终端录像证明是 Agent 自己完成的（不是你手写的）

---

### 6.3 添加"输入历史 + 上翻"功能

**要求**：给 `ui/repl.py` 加上 readline 支持，让用户可以用上/下箭头翻阅历史输入。

**提示**：
```python
import readline  # 导入即生效（Linux/macOS）
```

**验收标准**：
- REPL 中输入过的命令可以用 ↑↓ 翻阅
- 退出后历史不丢失（可选：保存到 `.agent_history` 文件）

---

## 选做（2 道）

### 6.4 ★ 多文件联动 —— 让 Agent 一次性重构 3 个文件

**要求**：给 Agent 一个任务：
> "我有 a.py b.py c.py 三个文件，请把它们里面重复的 `validate_input()` 函数抽取到 `utils.py`，然后让三个文件都改成 `from utils import validate_input`。完事跑测试确认。"

先手动创建 a/b/c.py（各含一份相同的 validate_input + 一个调用它的函数），然后让 Agent 做。

**验收标准**：
- utils.py 存在且只有一份 validate_input
- a/b/c.py 的 import 正确
- 测试通过

---

### 6.5 ★ 让 Agent 自己优化自己 —— meta-programming

**要求**：给 Agent 一个任务：
> "请阅读你自己的 agent.py 源码，找出一个可以优化的点，用 edit 修改自己，然后重启验证改进。"

**开放题**，观察 Agent 是否能：
1. 准确定位 agent.py 的绝对路径
2. 提出合理的优化建议
3. 用 edit 修改自身
4. 意识到"修改自身需要重启才能生效"

记录你的观察到 comparison.md 的附录里。

---

## 答案要点（教师参考）

| 题号 | 关键点 |
|------|--------|
| 6.1 | 在 Agent Loop 里判断 `not resp.tool_calls` 时走 `llm.chat_stream(..., on_text=print_chunk)`，其他轮次照旧 |
| 6.2 | 学生只需要用自己的 Agent 发一句话；如果 Agent 写的测试不对，让学生重试/修改 prompt |
| 6.3 | `import readline` + `readline.read_history_file` / `readline.write_history_file` |
| 6.4 | 关键：Agent 需要**先读 3 个文件确认内容相同**，再写 utils.py，再 edit 三个文件 |
| 6.5 | 开放题；常见优化：加更好的错误提示 / 在 verbose 里打印 token 用量 |
