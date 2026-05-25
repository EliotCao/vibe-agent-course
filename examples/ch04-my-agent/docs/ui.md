# 终端 UI 设计文档

## 概述

`ui.py` 基于 [Rich](https://github.com/Textualize/rich) 库实现终端美化输出，提供 Markdown 渲染、工具调用面板、语法高亮等能力，模仿 Aider 等主流 AI Coding Agent 的终端体验。

## 技术选型

| 方案 | 代表产品 | 语言 | 我们的选择 |
|------|----------|------|-----------|
| 自研 Ink (React Reconciler) | Claude Code | TypeScript | ❌ 过重 |
| Ratatui | Codex CLI | Rust | ❌ 非 Python |
| Rich | Aider | Python | ✅ 极简且效果好 |
| Textual | - | Python | 备选（更复杂的 TUI） |

选择 Rich 的理由：
- **零学习成本**：API 直观，`console.print()` 即用
- **Markdown 原生支持**：LLM 回答直接渲染
- **面板/表格/语法高亮**：内置组件丰富
- **Aider 同款**：经过大规模验证

## UI 组件

### 1. 欢迎界面

```
──────────────────── Coding Agent ────────────────────
  📁 工作目录: /workspace/ch04-my-agent
  🔧 已加载 9 个工具
  💡 输入 /quit 退出, /reset 重置对话
──────────────────────────────────────────────────────
```

### 2. 用户输入提示

```
▶ 帮我看一下 main.py
```

绿色箭头提示符，支持 readline 行编辑。

### 3. 工具调用面板

```
╭─ 🔧 read  main.py ─────────────────────────────╮
│ 1:import os                                      │
│ 2:def main():                                    │
│ ...                                              │
╰──────────────────────────────────────────────────╯
```

面板颜色根据工具类型区分：
- 蓝色：读取类（read, grep, glob, list）
- 绿色：写入类（write, edit）
- 黄色：命令类（bash）
- 青色：其他（todo, webfetch）

### 4. LLM 回答

Markdown 渲染输出，支持：
- 标题、列表、粗体/斜体
- 代码块（带语法高亮）
- 表格

### 5. 思考中状态

```
⠋ 思考中...
```

使用 `console.status()` 显示 spinner，LLM 响应后自动消失。

## 模块接口

| 函数 | 用途 |
|------|------|
| `print_welcome(workdir, tool_count)` | 打印欢迎界面 |
| `print_tool_call(name, result, args)` | 工具调用面板 |
| `print_response(content)` | Markdown 渲染 LLM 回答 |
| `print_error(message)` | 红色错误信息 |
| `print_info(message)` | 灰色提示信息 |
| `print_reset()` | 重置提示 |
| `print_bye()` | 退出提示 |
| `get_user_prompt()` | 返回提示符字符串 |
| `console` | Rich Console 实例 |

## 架构位置

```
ch04-my-agent/
├── coding_agent.py     # Agent 逻辑（调用 ui 输出）
├── ui.py               # ← 终端 UI 模块（本文件）
└── docs/
    └── ui.md           # ← 本文档
```

## 后续扩展

| 方向 | 说明 |
|------|------|
| Diff 高亮 | edit 工具的结果显示红删绿增 |
| 流式输出 | LLM 文本边生成边渲染 Markdown |
| 可折叠面板 | 长工具输出默认折叠，按键展开 |
| 主题系统 | 支持亮色/暗色主题切换 |
| 多行输入 | 支持粘贴多行代码 |
