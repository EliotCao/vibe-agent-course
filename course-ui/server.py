"""Vibe Agent Course UI 后端服务（纯 stdlib，无外部依赖）

特性：
- 扫描 01-08 课程目录，提供课程结构索引
- 读取 markdown 讲义、Python 示例源码，渲染图片资源
- 一键运行 lab/demo_*.py，并通过 SSE 流式回传 stdout/stderr
- 支持向运行中进程注入 stdin（演示交互式 demo）
- 默认监听 127.0.0.1:8765
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import select
import signal
import subprocess
import sys
import threading
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qs, urlsplit

# ------------------------------------------------------------------
# 路径定位
# ------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # 仓库根目录
STATIC_DIR = HERE / "static"

COURSE_DIRS = sorted([p for p in ROOT.iterdir() if re.match(r"^0[1-8]-", p.name)])

COURSE_TITLES: dict[str, str] = {
    "01-meet-your-ai": "认识你的 AI",
    "02-tools-and-agent-loop": "Function Calling 与最小 Agent",
    "03-agent-patterns": "Agent 范式（ReAct / Plan / Reflection）",
    "04-context-and-memory": "上下文与记忆",
    "05-coding-agent-tools": "Coding Agent 工具集",
    "06-coding-agent-integration": "整合：完整 Coding Agent",
    "07-skills-and-npc": "Skills 扩展 + NPC 上线",
    "08-recap-and-final": "总结与大作业",
}
COURSE_SUBTITLES: dict[str, str] = {
    "01-meet-your-ai": "Next-token · Tokens · Roles · 幻觉",
    "02-tools-and-agent-loop": "Function Calling · ToolRegistry · Agent Loop",
    "03-agent-patterns": "ReAct · Plan-and-Solve · Reflection",
    "04-context-and-memory": "上下文管理 · 向量记忆 · Agent v2",
    "05-coding-agent-tools": "5 阶段工作流 · 5 个核心工具",
    "06-coding-agent-integration": "REPL · 端到端调试 · 真实任务闭环",
    "07-skills-and-npc": "SKILL.md · NPC · Docker · CNB Pipeline",
    "08-recap-and-final": "全链路复盘 · 大作业",
}

# ------------------------------------------------------------------
# 工具函数：扫描课程
# ------------------------------------------------------------------
def _safe_resolve(rel: str) -> Path:
    if not rel:
        raise ValueError("缺少 path 参数")
    target = (ROOT / rel).resolve()
    target.relative_to(ROOT)  # 越狱检查
    return target


def _sort_key(name: str) -> tuple:
    m = re.search(r"(\d+)", name)
    return (int(m.group(1)) if m else 9999, name)


def _md_title(path: Path, fallback: str = "") -> str:
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
                if line.startswith("## "):
                    return line[3:].strip()
                if line:
                    return line[:60]
    except OSError:
        pass
    return fallback or path.stem


def _py_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return path.name
    m = re.search(r'"""\s*(.+?)\s*\n', text, re.S)
    if m:
        return m.group(1).strip()[:80]
    return path.stem


def scan_course(course_dir: Path) -> dict[str, Any]:
    name = course_dir.name
    overview = course_dir / "README.md"

    lectures: list[dict[str, str]] = []
    lec_dir = course_dir / "lecture"
    if lec_dir.is_dir():
        for f in sorted(lec_dir.glob("*.md"), key=lambda p: _sort_key(p.name)):
            lectures.append(
                {
                    "title": _md_title(f, fallback=f.stem),
                    "path": f.relative_to(ROOT).as_posix(),
                    "filename": f.name,
                }
            )

    demos: list[dict[str, str]] = []
    lab_readme = None
    lab_dir = course_dir / "lab"
    if lab_dir.is_dir():
        readme = lab_dir / "README.md"
        if readme.exists():
            lab_readme = readme.relative_to(ROOT).as_posix()
        for f in sorted(lab_dir.glob("demo_*.py"), key=lambda p: _sort_key(p.name)):
            demos.append(
                {
                    "title": _py_title(f),
                    "path": f.relative_to(ROOT).as_posix(),
                    "filename": f.name,
                }
            )

    return {
        "id": name,
        "title": COURSE_TITLES.get(name, name),
        "subtitle": COURSE_SUBTITLES.get(name, ""),
        "readme": overview.relative_to(ROOT).as_posix() if overview.exists() else None,
        "lab_readme": lab_readme,
        "lectures": lectures,
        "demos": demos,
    }


# ------------------------------------------------------------------
# 进程管理
# ------------------------------------------------------------------
class RunningProc:
    """封装一个运行中的 subprocess，把 stdout/stderr 推到队列中。"""

    def __init__(self, proc: subprocess.Popen) -> None:
        self.proc = proc
        self.events: list[tuple[str, Any]] = []
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.finished = False

        threading.Thread(target=self._reader, args=(proc.stdout, "stdout"), daemon=True).start()
        threading.Thread(target=self._reader, args=(proc.stderr, "stderr"), daemon=True).start()
        threading.Thread(target=self._waiter, daemon=True).start()

    def _push(self, kind: str, data: Any) -> None:
        with self.cond:
            self.events.append((kind, data))
            self.cond.notify_all()

    def _reader(self, stream, kind: str) -> None:
        try:
            for line in iter(stream.readline, b""):
                self._push(kind, line.decode("utf-8", errors="replace"))
        finally:
            stream.close()

    def _waiter(self) -> None:
        self.proc.wait()
        self._push("exit", {"code": self.proc.returncode})
        with self.cond:
            self.finished = True
            self.cond.notify_all()

    def poll_events(self, cursor: int, timeout: float = 0.6) -> tuple[list[tuple[str, Any]], int]:
        with self.cond:
            if cursor >= len(self.events) and not self.finished:
                self.cond.wait(timeout=timeout)
            new = self.events[cursor:]
            return new, len(self.events)

    def write_stdin(self, text: str) -> None:
        if self.proc.stdin and not self.proc.stdin.closed:
            self.proc.stdin.write(text.encode("utf-8"))
            self.proc.stdin.flush()

    def stop(self) -> None:
        if self.proc.poll() is None:
            try:
                self.proc.send_signal(signal.SIGTERM)
            except ProcessLookupError:
                pass


RUNNING: dict[str, RunningProc] = {}


def start_demo(rel_path: str) -> tuple[str, RunningProc, str]:
    target = _safe_resolve(rel_path)
    if target.suffix != ".py" or not target.is_file():
        raise ValueError("目标必须是 .py 文件")
    rel = target.relative_to(ROOT).as_posix()
    if not re.match(r"^0[1-8]-.+/lab/demo_.+\.py$", rel):
        raise ValueError("只允许执行各课 lab 下的 demo_*.py")

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env["PYTHONUNBUFFERED"] = "1"

    py_candidates = [
        ROOT / ".venv" / "bin" / "python",
        Path(sys.executable),
    ]
    python_bin = next((str(p) for p in py_candidates if p.exists()), sys.executable)

    proc = subprocess.Popen(
        [python_bin, "-u", str(target)],
        cwd=str(target.parent),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    rp = RunningProc(proc)
    rid = uuid.uuid4().hex[:12]
    RUNNING[rid] = rp
    return rid, rp, python_bin


# ------------------------------------------------------------------
# HTTP 处理
# ------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "VibeAgentCourseUI/1.0"

    # 静默普通日志
    def log_message(self, format, *args):  # noqa: A002
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))

    # ---- 工具：发送 ----
    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, ctype: str = "text/plain", status: int = 200) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        ctype, _ = mimetypes.guess_type(str(path))
        ctype = ctype or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(path.stat().st_size))
        # 静态资源禁用缓存，避免改完前端旧代码还在生效
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(64 * 1024), b""):
                self.wfile.write(chunk)

    def _send_error_json(self, status: int, msg: str) -> None:
        self._send_json({"error": msg}, status=status)

    # ---- 路由 ----
    def do_GET(self) -> None:  # noqa: N802
        url = urlsplit(self.path)
        qs = {k: v[0] for k, v in parse_qs(url.query).items()}
        path = url.path

        try:
            if path == "/" or path == "":
                return self._send_static("index.html")
            if path == "/health":
                return self._send_text("ok")
            if path.startswith("/static/"):
                return self._send_static(path[len("/static/") :])
            if path == "/api/courses":
                return self._send_json({"courses": [scan_course(c) for c in COURSE_DIRS]})
            if path == "/api/file":
                return self._handle_file(qs.get("path", ""))
            if path == "/api/asset":
                return self._handle_asset(qs.get("path", ""))
            if path == "/api/run":
                return self._handle_run(qs.get("path", ""))
            return self._send_error_json(404, "not found")
        except ValueError as e:
            self._send_error_json(400, str(e))
        except Exception as e:  # noqa: BLE001
            self._send_error_json(500, f"server error: {e}")

    def do_POST(self) -> None:  # noqa: N802
        url = urlsplit(self.path)
        path = url.path
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length) if length > 0 else b""
            body: dict = {}
            if raw:
                try:
                    body = json.loads(raw.decode("utf-8"))
                except Exception:
                    body = {}

            m = re.match(r"^/api/stdin/([0-9a-f]+)$", path)
            if m:
                rid = m.group(1)
                rp = RUNNING.get(rid)
                if not rp:
                    return self._send_error_json(404, "进程不存在或已结束")
                text = body.get("text", "")
                if not text.endswith("\n"):
                    text += "\n"
                rp.write_stdin(text)
                return self._send_json({"ok": True})

            m = re.match(r"^/api/stop/([0-9a-f]+)$", path)
            if m:
                rid = m.group(1)
                rp = RUNNING.get(rid)
                if not rp:
                    return self._send_json({"ok": False, "reason": "not running"})
                rp.stop()
                return self._send_json({"ok": True})

            return self._send_error_json(404, "not found")
        except Exception as e:  # noqa: BLE001
            self._send_error_json(500, f"server error: {e}")

    # ---- 具体处理 ----
    def _send_static(self, rel: str) -> None:
        target = (STATIC_DIR / rel).resolve()
        try:
            target.relative_to(STATIC_DIR)
        except ValueError:
            return self._send_error_json(400, "非法路径")
        if not target.is_file():
            return self._send_error_json(404, "not found")
        self._send_file(target)

    def _handle_file(self, rel: str) -> None:
        try:
            target = _safe_resolve(rel)
        except ValueError as e:
            return self._send_error_json(400, str(e))
        if not target.is_file():
            return self._send_error_json(404, "文件不存在")
        if target.suffix not in {".md", ".py", ".txt"}:
            return self._send_error_json(400, "仅允许读取 md/py/txt")
        content = target.read_text(encoding="utf-8", errors="replace")
        self._send_json({"path": rel, "content": content})

    def _handle_asset(self, rel: str) -> None:
        try:
            target = _safe_resolve(rel)
        except ValueError as e:
            return self._send_error_json(400, str(e))
        if not target.is_file():
            return self._send_error_json(404, "资源不存在")
        if target.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            return self._send_error_json(400, "不支持的资源类型")
        self._send_file(target)

    # ---- SSE：运行 demo ----
    def _handle_run(self, rel: str) -> None:
        try:
            rid, rp, python_bin = start_demo(rel)
        except ValueError as e:
            return self._send_error_json(400, str(e))

        # SSE 头
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        def write_event(name: str, data: Any) -> bool:
            # 始终 JSON 编码，前端统一 JSON.parse；
            # 这样字符串里的 \n / 引号 / Unicode 都能安全穿越 SSE 协议。
            payload = json.dumps(data, ensure_ascii=False)
            try:
                self.wfile.write(f"event: {name}\ndata: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
                return True
            except (BrokenPipeError, ConnectionResetError):
                return False

        if not write_event(
            "start",
            {"run_id": rid, "python": python_bin, "path": rel},
        ):
            rp.stop()
            RUNNING.pop(rid, None)
            return

        cursor = 0
        last_keepalive = time.time()
        try:
            while True:
                events, cursor = rp.poll_events(cursor, timeout=0.6)
                for kind, data in events:
                    if not write_event(kind, data):
                        rp.stop()
                        return
                    if kind == "exit":
                        return
                # 客户端可能空闲，定期心跳
                if time.time() - last_keepalive > 15:
                    if not write_event("ping", "keep-alive"):
                        rp.stop()
                        return
                    last_keepalive = time.time()
                if rp.finished and not events:
                    return
        finally:
            RUNNING.pop(rid, None)
            if rp.proc.poll() is None:
                rp.stop()


def main() -> None:
    port = int(os.environ.get("PORT", "8765"))
    addr = os.environ.get("HOST", "127.0.0.1")

    # 强制 IPv4，避免某些 Python 构建在 ::: 上监听导致 127.0.0.1 不可达
    import socket as _socket

    class _IPv4HTTPServer(ThreadingHTTPServer):
        address_family = _socket.AF_INET
        allow_reuse_address = True

    httpd = _IPv4HTTPServer((addr, port), Handler)
    print(f"[course-ui] http://{addr}:{port}  (Ctrl+C 退出)")
    print(f"[course-ui] 仓库根目录：{ROOT}")
    print(f"[course-ui] 已扫描 {len(COURSE_DIRS)} 节课")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[course-ui] 已退出")
        httpd.shutdown()


if __name__ == "__main__":
    main()
