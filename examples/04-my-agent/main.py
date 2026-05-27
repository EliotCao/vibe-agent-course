"""CodingAgent —— 极简版 Claude Code。

基于 Function Calling + 对话循环 + 多工具，实现一个交互式编程助手。
通过 ContextBuilder 统一管理所有消息（含 tool_calls），自动压缩长对话。
"""

import json
import os
from typing import List, Optional

from llm import LLM
from tools import ToolRegistry
from tools.impl import ALL_TOOLS
from context import ContextBuilder, ContextConfig
from memory import Memory
from skills import Skills
import ui

SYSTEM_PROMPT = """你是一个专业的编程助手（Coding Agent），可以帮助用户阅读、编写和修改代码。

## 能力
- 阅读和分析文件内容
- 创建和编辑文件
- 在项目中搜索代码
- 执行 shell 命令（安装依赖、运行测试等）
- 管理任务列表
- 抓取网页参考资料

## 工作原则
1. 先理解再动手：修改代码前先阅读相关文件
2. 最小改动：只修改必要的部分，避免重写整个文件
3. 解释清楚：告诉用户你做了什么、为什么这么做
4. 安全优先：危险操作前说明风险
5. 语法验证：写入或编辑文件后，务必用 bash 工具执行对应语言的语法检查（如 python -m py_compile、node --check 等），确认无语法错误。如果有错误，立即修复。

## 思考过程
每次调用工具前，你必须在 content 中简短说明你的思考：
- 你在做什么、为什么这么做（一两句话即可）
这样用户可以跟随你的推理过程。
"""


class CodingAgent:
    """交互式编程助手，基于 Function Calling 驱动工具调用。

    核心循环:
        用户输入 → context.append → context.get_messages（自动压缩）
        → LLM 推理 → [工具调用 → 结果注入 context → LLM 再推理]*
        → 输出回答
    """

    def __init__(
        self,
        workdir: str = ".",
        system_prompt: str = SYSTEM_PROMPT,
        max_tool_rounds: int = 20,
        max_context_tokens: int = 30000,
    ):
        self.llm = LLM()
        self.tools = self._create_registry(workdir)
        self.system_prompt = system_prompt
        self.max_tool_rounds = max_tool_rounds

        # Skills（从 .codebuddy/skills/ 加载）
        self.skills = Skills()

        # 记忆系统（持久化到 workdir/.memory/）
        memory_dir = os.path.join(workdir, ".memory")
        self.memory = Memory(storage_dir=memory_dir)

        # ContextBuilder 统一管理所有消息（模式 B）
        self.context = ContextBuilder(
            system_prompt=self._build_system_prompt(),
            config=ContextConfig(
                max_tokens=max_context_tokens,
                reserve_ratio=0.1,
                keep_recent=10,
            ),
        )

    def _build_system_prompt(self) -> str:
        """构建 system prompt，注入 skills 索引和记忆。"""
        prompt = self.system_prompt

        # Level 1: 注入 skill 索引（name + description）
        index_prompt = self.skills.to_index_prompt()
        if index_prompt:
            prompt += f"\n{index_prompt}"

        # Level 2: 注入已激活的 skill 完整内容
        active_prompt = self.skills.to_active_prompt()
        if active_prompt:
            prompt += f"\n{active_prompt}"

        # 注入持久化记忆摘要
        memory_context = self.memory.get_context(limit=8)
        if memory_context:
            prompt += f"\n\n{memory_context}"

        return prompt

    @staticmethod
    def _create_registry(workdir: str) -> ToolRegistry:
        """注册所有工具。"""
        registry = ToolRegistry()
        for ToolClass in ALL_TOOLS:
            if ToolClass.__name__ == "BashTool":
                registry.register_tool(ToolClass(workdir=workdir))
            else:
                registry.register_tool(ToolClass())
        return registry

    def chat(self, user_input: str) -> str:
        """处理一轮用户输入，返回最终回答。

        流程:
        1. 根据用户问题匹配并按需加载相关 skill
        2. 用户消息追加到 context
        3. context.get_messages() 获取消息列表（自动压缩如果超预算）
        4. 调用 LLM（带 tools schema）
        5. 如果 LLM 要求调用工具 → 执行 → 结果追加到 context → 再次调用
        6. 循环直到 LLM 给出文本回答
        """
        # 自动匹配最相关的 skill 并加载（只取最佳匹配的 1 个）
        matched = self.skills.match(user_input)
        if matched:
            best = matched[0]  # 取最相关的
            meta = self.skills.get_meta(best)
            if meta and not meta.loaded:
                self.skills.load(best)
                ui.print_info(f"📚 已激活 skill: {best}")
                # 更新 system prompt，让 LLM 看到 skill 内容
                self.context._messages[0] = {
                    "role": "system",
                    "content": self._build_system_prompt(),
                }

        # 用户消息追加到 context
        self.context.append({"role": "user", "content": user_input})

        tools_schema = self.tools.to_openai_schema()
        tool_actions = []  # 记录本轮执行的工具动作

        for _ in range(self.max_tool_rounds):
            # 从 context 获取消息（自动处理压缩）
            messages = self.context.get_messages()

            response = self.llm.chat(messages, tools=tools_schema)

            if response is None:
                return "❌ 调用 LLM 失败"

            # 检查是否有工具调用
            if response.tool_calls:
                # 显示 LLM 的思考过程（如果有）
                if response.content:
                    ui.print_thinking(response.content)

                # assistant 消息（含 tool_calls）追加到 context
                self.context.append(self._message_to_dict(response))

                # 逐个执行工具，结果追加到 context
                for tool_call in response.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    self.context.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                    # 用 UI 面板展示工具调用
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                    ui.print_tool_call(tool_call.function.name, result, args)
                    # 记录动作摘要
                    tool_actions.append((tool_call.function.name, args))

                continue  # 继续让 LLM 处理

            # 无工具调用，LLM 给出了最终回答
            content = response.content or ""
            self.context.append({"role": "assistant", "content": content})

            # 将本轮操作自动记录到记忆
            self._remember_actions(user_input, tool_actions)

            return content

        return "⚠️ 达到最大工具调用轮次，已停止。"

    def _remember_actions(self, user_input: str, tool_actions: list):
        """将本轮重要操作记录到记忆系统。"""
        ui.print_info(f"[记忆] 本轮工具调用 {len(tool_actions)} 次: {[a[0] for a in tool_actions]}")

        if not tool_actions:
            ui.print_info("[记忆] 无工具调用，跳过记忆写入")
            return

        # 记录用户意图（工作记忆）
        self.memory.add(
            f"用户请求: {user_input[:100]}",
            memory_type="working",
            importance=0.5,
        )
        ui.print_info(f"[记忆] 已写入工作记忆: 用户请求")

        # 记录文件修改操作（情景记忆，持久化）
        for name, args in tool_actions:
            if name in ("write", "edit"):
                path = args.get("path", "?")
                self.memory.add(
                    f"修改了文件 {path}",
                    memory_type="episodic",
                    importance=0.7,
                    tags=[path, name],
                )
                ui.print_info(f"[记忆] 已写入情景记忆: 修改了 {path}")
            elif name == "bash":
                cmd = args.get("command", "")
                if any(kw in cmd for kw in ("install", "pip", "npm", "apt")):
                    self.memory.add(
                        f"执行了安装命令: {cmd[:80]}",
                        memory_type="episodic",
                        importance=0.6,
                        tags=["install"],
                    )

    def _execute_tool_call(self, tool_call) -> str:
        """执行单个工具调用。"""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return f"❌ 参数解析失败: {tool_call.function.arguments}"

        return self.tools.execute(name, **args)

    @staticmethod
    def _message_to_dict(message) -> dict:
        """将 OpenAI message 对象转为 dict。"""
        msg = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        return msg

    def reset(self):
        """重置对话历史和上下文（保留持久化记忆）。"""
        self.memory.forget(strategy="working")  # 只清工作记忆
        self.context = ContextBuilder(
            system_prompt=self._build_system_prompt(),
            config=self.context.config,
        )


def _handle_skill_command(agent: CodingAgent, command: str):
    """处理 /skill 命令。"""
    parts = command.split(maxsplit=2)
    sub = parts[1] if len(parts) > 1 else ""

    if sub == "list" or not sub:
        all_skills = agent.skills.list()
        loaded = agent.skills.list_loaded()
        if all_skills:
            ui.console.print(f"[bold]Skills（{len(all_skills)} 个）:[/bold]")
            for name in all_skills:
                meta = agent.skills.get_meta(name)
                desc = f" — {meta.description}" if meta and meta.description else ""
                status = "[green]●[/green]" if name in loaded else "[dim]○[/dim]"
                ui.console.print(f"  {status} {name}{desc}")
        else:
            ui.print_info(f"无可用 skills（目录: {agent.skills.skills_dir}）")
    elif sub == "load" and len(parts) > 2:
        result = agent.skills.load(parts[2])
        ui.console.print(result)
    elif sub == "unload" and len(parts) > 2:
        result = agent.skills.unload(parts[2])
        ui.console.print(result)
    elif sub == "show" and len(parts) > 2:
        content = agent.skills.get(parts[2])
        if content:
            ui.console.print(f"[bold]{parts[2]}:[/bold]\n{content}")
        else:
            ui.print_info(f"Skill 未加载: {parts[2]}")
    else:
        ui.console.print("[dim]用法: /skill [list|load|unload|show] [name][/dim]")

    ui.console.print()


def _print_help():
    """打印命令行帮助信息（Rich 渲染）。"""
    # 用原始字符串，方便写 Rich 的 \[ 转义（字面方括号）
    help_text = r"""[bold cyan]CodingAgent[/bold cyan] —— 极简版 Claude Code 编程助手

[bold]用法:[/bold]
  [green]python main.py[/green] [dim]\[选项] \[WORKDIR][/dim]
      启动交互式 REPL 模式

  [green]python main.py --solo exec[/green] [yellow]"任务描述"[/yellow] [dim]\[选项][/dim]
      Solo 模式：执行一次性任务后退出（适合脚本/CI/CD）

[bold]通用选项:[/bold]
  [cyan]-h, --help[/cyan]               显示本帮助信息并退出
  [cyan]-w, --workdir DIR[/cyan]        工作目录（默认当前目录）

[bold]Solo 模式选项:[/bold]
  [cyan]-o, --output FILE[/cyan]        将最终结果写入文件
  [cyan]-o, --output -[/cyan]           将最终结果写入 stdout（纯文本，CI/CD 友好）
                           过程信息（思考、工具调用）走 stderr，避免污染

[bold]REPL 内置命令:[/bold]
  [magenta]/quit[/magenta]                    退出
  [magenta]/reset[/magenta]                   重置对话与工作记忆
  [magenta]/skill[/magenta] \[list|load|unload|show] \[name]
                           管理 skills

[bold]示例:[/bold]
  [dim]# 在当前目录启动 REPL[/dim]
  python main.py

  [dim]# 指定工作目录启动 REPL[/dim]
  python main.py -w ~/projects/foo

  [dim]# Solo 模式：执行一次任务[/dim]
  python main.py --solo exec "在 src/ 下找出所有 TODO 注释"

  [dim]# Solo 模式：结果写入文件[/dim]
  python main.py --solo exec "总结 README" -o summary.md

  [dim]# Solo 模式：通过管道捕获结果[/dim]
  python main.py --solo exec "列出依赖" -o - | tee deps.txt
"""
    ui.console.print(help_text)


def _run_solo_exec(workdir: str, query: str, output_file: Optional[str] = None):
    """Solo 模式：执行一次性任务后退出。

    不进入 REPL 循环，适合脚本化调用或 CI/CD 集成。

    思考过程和工具调用始终打印到 stderr（Rich 渲染），
    最终结果通过以下方式获取：
      - --output <file>: 结果写入指定文件
      - --output -:     结果写入 stdout（纯文本，无 Rich 格式）
      - 不指定:         结果通过 Rich 渲染输出（与 REPL 一致）
    """
    import sys
    from rich.console import Console

    # 如果需要将结果输出到 stdout，则 UI 过程信息走 stderr，避免污染
    if output_file == "-":
        ui.console = Console(stderr=True)

    agent = CodingAgent(workdir=workdir)

    ui.console.print(f"[bold cyan]🚀 Solo 模式[/bold cyan] | 工作目录: {workdir}")
    ui.console.print(f"[dim]任务: {query}[/dim]\n")

    try:
        with ui.console.status("[dim]思考中...[/dim]", spinner="dots"):
            answer = agent.chat(query)

        if answer:
            # 始终在终端渲染完整过程输出（走 stderr 或 stdout 取决于上面的设置）
            ui.print_response(answer)

            # 如果指定了 --output，额外将纯文本结果写到目标
            if output_file == "-":
                # 输出到 stdout（纯文本，方便管道/CI 捕获）
                sys.stdout.write(answer)
                if not answer.endswith("\n"):
                    sys.stdout.write("\n")
            elif output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(answer)
                ui.print_info(f"✅ 结果已写入: {output_file}")
    except KeyboardInterrupt:
        ui.print_info("\n⏹ 任务已中断。")
        raise SystemExit(1)


def _run_repl(workdir: str):
    """交互式 REPL 模式。"""
    try:
        import readline  # noqa: F401 — 启用行编辑，修复中文删除问题
    except ImportError:
        pass

    agent = CodingAgent(workdir=workdir)

    memory_stats = agent.memory.stats()
    skills_loaded = agent.skills.list()
    ui.print_welcome(
        workdir, len(agent.tools.get_tool_names()), agent.llm.model,
        memory_stats["total"], len(skills_loaded),
    )

    while True:
        try:
            user_input = input("▶ ").strip()
        except EOFError:
            ui.print_bye()
            break
        except KeyboardInterrupt:
            # 输入时按 Ctrl+C，换行继续
            print()
            continue

        if not user_input:
            continue
        if user_input == "/quit":
            ui.print_bye()
            break
        if user_input == "/reset":
            agent.reset()
            ui.print_reset()
            continue
        if user_input.startswith("/skill"):
            _handle_skill_command(agent, user_input)
            continue

        # 执行任务，Ctrl+C 可中断当前任务
        try:
            with ui.console.status("[dim]思考中...[/dim]", spinner="dots"):
                answer = agent.chat(user_input)
            if answer:
                ui.print_response(answer)
        except KeyboardInterrupt:
            ui.print_info("\n⏹ 任务已中断，回到待输入状态。\n")


def main():
    """主入口：根据命令行参数分发到不同模式。

    用法:
      查看帮助:  python main.py --help
      交互模式:  python main.py [-w WORKDIR] [WORKDIR]
      Solo 模式: python main.py --solo exec "任务描述" [-o FILE]

    --output 选项（仅 solo 模式）:
      --output result.txt   将最终结果写入文件
      --output -            将最终结果写入 stdout（纯文本，CI/CD 友好）
    """
    import sys

    # 优先处理 --help / -h，无论出现在哪个位置
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        _print_help()
        return

    workdir = "."
    query = None
    output_file = None
    is_solo = False

    # 手动解析参数以兼容 `--solo exec "query"` 的调用形式
    args = sys.argv[1:]

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--workdir", "-w") and i + 1 < len(args):
            workdir = args[i + 1]
            i += 2
        elif arg in ("--output", "-o") and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif arg == "--solo":
            is_solo = True
            i += 1
        elif arg == "exec" and is_solo:
            if i + 1 < len(args):
                query = args[i + 1]
                i += 2
            else:
                ui.console.print("[red]错误: exec 后需要提供任务描述[/red]")
                ui.console.print("用法: python main.py --solo exec \"你的任务\"")
                raise SystemExit(1)
        else:
            # 向后兼容：第一个位置参数作为 workdir
            if not is_solo and workdir == ".":
                workdir = arg
            i += 1

    workdir = os.path.abspath(workdir)

    if is_solo:
        if not query:
            ui.console.print("[red]错误: solo 模式需要 exec 子命令和任务描述[/red]")
            ui.console.print("用法: python main.py --solo exec \"你的任务\"")
            raise SystemExit(1)
        _run_solo_exec(workdir, query, output_file=output_file)
    else:
        _run_repl(workdir)


if __name__ == "__main__":
    main()
