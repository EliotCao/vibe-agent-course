"""终端 UI 模块 —— 基于 Rich 的美化输出。

提供：
- Markdown 渲染（LLM 回答）
- 工具调用面板（带标题、折叠）
- Diff 高亮（编辑操作）
- Spinner（等待 LLM）
- 语法高亮（代码块）
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.rule import Rule


console = Console()


def print_welcome(workdir: str, tool_count: int):
    """打印欢迎信息。"""
    console.print()
    console.print(Rule("[bold blue]Coding Agent[/bold blue]"))
    console.print(f"  📁 工作目录: [cyan]{workdir}[/cyan]")
    console.print(f"  🔧 已加载 [green]{tool_count}[/green] 个工具")
    console.print(f"  💡 输入 [bold]/quit[/bold] 退出, [bold]/reset[/bold] 重置对话")
    console.print(Rule())
    console.print()


def print_user_input(text: str):
    """打印用户输入的提示。"""
    console.print()


def print_tool_call(tool_name: str, result: str, args: dict = None):
    """打印工具调用结果面板。"""
    # 标题
    title = f"🔧 {tool_name}"
    if args:
        # 显示关键参数
        key_args = _format_args(tool_name, args)
        if key_args:
            title += f"  [dim]{key_args}[/dim]"

    # 内容截断
    display_result = result
    if len(result) > 500:
        display_result = result[:500] + "\n... (内容已截断)"

    # 根据工具类型选择样式
    if tool_name in ("read", "grep", "glob", "list"):
        style = "blue"
    elif tool_name in ("write", "edit"):
        style = "green"
    elif tool_name == "bash":
        style = "yellow"
    else:
        style = "cyan"

    console.print(Panel(
        Text(display_result, overflow="fold"),
        title=title,
        title_align="left",
        border_style=style,
        padding=(0, 1),
    ))


def print_response(content: str):
    """打印 LLM 的最终回答（Markdown 渲染）。"""
    console.print()
    md = Markdown(content)
    console.print(md)
    console.print()


def print_error(message: str):
    """打印错误信息。"""
    console.print(f"[bold red]{message}[/bold red]")


def print_info(message: str):
    """打印提示信息。"""
    console.print(f"[dim]{message}[/dim]")


def print_reset():
    """打印重置提示。"""
    console.print("[yellow]🔄 对话已重置[/yellow]\n")


def print_bye():
    """打印退出提示。"""
    console.print("\n[dim]👋 再见！[/dim]")


def get_spinner():
    """获取一个 thinking spinner 用于 Live 显示。"""
    return Spinner("dots", text="[dim]思考中...[/dim]")


def get_user_prompt() -> str:
    """获取用户输入提示符。"""
    return "[bold green]▶[/bold green] "


def _format_args(tool_name: str, args: dict) -> str:
    """格式化工具参数用于显示。"""
    if tool_name == "read" and "path" in args:
        return args["path"]
    elif tool_name == "write" and "path" in args:
        return args["path"]
    elif tool_name == "edit" and "path" in args:
        return args["path"]
    elif tool_name == "grep" and "pattern" in args:
        return f'"{args["pattern"]}" in {args.get("path", ".")}'
    elif tool_name == "glob" and "pattern" in args:
        return args["pattern"]
    elif tool_name == "list" and "path" in args:
        return args["path"]
    elif tool_name == "bash" and "command" in args:
        cmd = args["command"]
        return cmd[:40] + ("..." if len(cmd) > 40 else "")
    elif tool_name == "webfetch" and "url" in args:
        return args["url"][:50]
    return ""
