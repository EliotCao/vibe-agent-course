"""bash 工具：在工作区内执行 shell 命令。"""

import os
import subprocess
from tools import Tool, ToolParameter


class BashTool(Tool):
    """执行 shell 命令，带超时和输出大小限制。"""

    def __init__(self, workdir: str = None, timeout: int = 30, max_output: int = 50000):
        super().__init__("bash", "在工作区内执行 shell 命令")
        self.workdir = workdir or os.getcwd()
        self.timeout = timeout
        self.max_output = max_output

    def get_parameters(self):
        return [
            ToolParameter(name="command", type="string", description="要执行的 shell 命令"),
            ToolParameter(name="workdir", type="string", description="工作目录", required=False, default=None),
        ]

    def run(self, command: str, workdir: str = None, **kwargs) -> str:
        cwd = workdir or self.workdir

        if not os.path.isdir(cwd):
            return f"❌ 工作目录不存在: {cwd}"

        try:
            result = subprocess.run(
                ["/bin/sh", "-lc", command],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout[:self.max_output])
            if result.stderr:
                output_parts.append(f"[stderr]\n{result.stderr[:self.max_output]}")

            output = "\n".join(output_parts) if output_parts else "(无输出)"

            if result.returncode != 0:
                output = f"[exit code: {result.returncode}]\n{output}"

            return output

        except subprocess.TimeoutExpired:
            return f"❌ 命令超时（{self.timeout}s）: {command}"
        except Exception as e:
            return f"❌ 执行失败: {e}"
