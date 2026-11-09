"""Vibe Agent Course UI 后端服务（纯 stdlib，无外部依赖）

特性：
- 扫描 01-06 课程目录，提供课程结构索引
- 读取 markdown 讲义、Python 示例源码，渲染图片资源
- 一键运行 lab/demo_*.py，并通过 SSE 流式回传 stdout/stderr
- 支持向运行中进程注入 stdin（演示交互式 demo）
- 默认监听 0.0.0.0:8765（可通过环境变量 HOST/PORT 覆盖）
"""

from __future__ import annotations

import gzip
import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

# ------------------------------------------------------------------
# 路径定位
# ------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # 仓库根目录
STATIC_DIR = HERE / "static"

COURSE_DIRS = sorted([p for p in ROOT.iterdir() if re.match(r"^0[1-6]-", p.name)])

COURSE_TITLES: dict[str, str] = {
    "01-meet-your-ai": "认识你的 AI",
    "02-tools-and-agent-loop": "Function Calling 与最小 Agent",
    "03-agent-patterns": "Agent 范式（ReAct / Plan / Reflection）",
    "04-context-and-memory": "上下文与记忆",
    "05-coding-agent-tools": "Coding Agent 工具集与整合",
    "06-skills-and-npc": "Skills 扩展 + NPC 上线",
}
COURSE_SUBTITLES: dict[str, str] = {
    "01-meet-your-ai": "Next-token · Tokens · Roles · 工具与上下文",
    "02-tools-and-agent-loop": "Function Calling · ToolRegistry · Agent Loop",
    "03-agent-patterns": "ReAct · Plan-and-Solve · Reflection",
    "04-context-and-memory": "上下文管理 · 向量记忆 · Agent v2",
    "05-coding-agent-tools": "5 阶段工作流 · 5 个核心工具 · REPL/Solo 整合",
    "06-skills-and-npc": "SKILL.md · Skills vs Tool · NPC · CNB 用法",
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


def _run_git(args: list[str], cwd: Path, timeout: float = 30) -> tuple[int, str]:
    """运行 git 子命令，返回 (returncode, combined_output)。

    - 关闭交互式凭据提示（GIT_TERMINAL_PROMPT=0）：服务端没有 TTY，一旦需要输入
      用户名/密码就会卡到超时，不如直接失败并把原因返回给前端。
    - push 这类网络操作由调用方传更大的 timeout。
    """
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env.setdefault("GIT_ASKPASS", "true")
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except FileNotFoundError:
        return 127, "git not found"
    except subprocess.TimeoutExpired:
        return 124, "git timeout"
    except Exception as e:  # noqa: BLE001
        return 1, f"git error: {e}"


def _git_error_line(output: str) -> str:
    """从 git 输出里挑一行最能说明问题的文本，用于前端提示。"""
    lines = [ln.strip() for ln in (output or "").splitlines() if ln.strip()]
    for ln in lines:
        low = ln.lower()
        if low.startswith(("fatal:", "error:", "remote:", "! [")) or "denied" in low:
            return ln
    return lines[-1] if lines else ""


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

    # 练习题：约定章节目录名 ↔ exercises/<同名子目录> 一一对应
    # （例如 03-agent-patterns 课对应 exercises/03-agent-patterns/）。
    # 现在前端有独立「📝 随堂练习」tab，所以这里要返回完整结构：
    #   - dir：练习目录的仓库相对路径，前端拼 CNB 云端 IDE 跳转 URL
    #   - readme：本章练习总览（题目说明），渲染在 tab 顶部
    #   - items：每题一项（filename + 从 docstring 抽出来的标题）
    # 某章没有对应练习目录则为 None，前端隐藏 tab。
    ex_dir = ROOT / "exercises" / name
    if ex_dir.is_dir():
        ex_readme = ex_dir / "README.md"
        ex_items: list[dict[str, str]] = []
        for f in sorted(ex_dir.glob("ex_*.py"), key=lambda p: _sort_key(p.name)):
            ex_items.append(
                {
                    "title": _py_title(f),
                    "path": f.relative_to(ROOT).as_posix(),
                    "filename": f.name,
                }
            )
        exercises = {
            "dir": ex_dir.relative_to(ROOT).as_posix(),
            "readme": ex_readme.relative_to(ROOT).as_posix() if ex_readme.exists() else None,
            "items": ex_items,
        }
    else:
        exercises = None

    return {
        "id": name,
        "title": COURSE_TITLES.get(name, name),
        "subtitle": COURSE_SUBTITLES.get(name, ""),
        "readme": overview.relative_to(ROOT).as_posix() if overview.exists() else None,
        "lab_readme": lab_readme,
        "lectures": lectures,
        "demos": demos,
        # 兼容字段：旧前端仍在用 exercise_dir 显示绿色 banner，保留几个版本后再删
        "exercise_dir": exercises["dir"] if exercises else None,
        "exercises": exercises,
    }


# ------------------------------------------------------------------
# 静态资源压缩（纯 stdlib gzip + 内存缓存）
# ------------------------------------------------------------------
# 前端 vendor 里挂着 3.5MB 的 mermaid.min.js，不压缩的话首次打开讲义要等
# 很久才能画出图。这里对文本类资源做 gzip：3.5MB → 约 660KB。
_GZIP_CACHE: dict[str, tuple[float, int, bytes]] = {}
_GZIP_LOCK = threading.Lock()


def _is_compressible(ctype: str) -> bool:
    ct = (ctype or "").split(";")[0].strip().lower()
    if ct.startswith("text/"):
        return True
    return ct in {
        "application/javascript",
        "application/json",
        "application/xml",
        "image/svg+xml",
    }


def _gzip_file(path: Path) -> bytes:
    """返回 path 的 gzip 字节；按 (mtime, size) 缓存，文件不变就不重复压缩。"""
    st = path.stat()
    key = str(path)
    with _GZIP_LOCK:
        hit = _GZIP_CACHE.get(key)
        if hit and hit[0] == st.st_mtime and hit[1] == st.st_size:
            return hit[2]
    packed = gzip.compress(path.read_bytes(), compresslevel=6)
    with _GZIP_LOCK:
        _GZIP_CACHE[key] = (st.st_mtime, st.st_size, packed)
    return packed


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
    if not re.match(r"^0[1-6]-.+/lab/demo_.+\.py$", rel):
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

    # HTTP access log：默认静默（避免在 CNB WebIDE 终端里被静态资源请求刷屏）。
    # 需要排查时设 DEBUG=1 即可看到完整请求日志；4xx/5xx 始终打印，方便发现问题。
    def log_message(self, format, *args):  # noqa: A002
        if os.environ.get("DEBUG") == "1":
            sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))
            return
        # args 形如 ('"GET / HTTP/1.1"', '200', '-')；第 2 个元素是 status code
        try:
            status = int(args[1]) if len(args) >= 2 else 0
        except (ValueError, TypeError):
            status = 0
        if status >= 400:
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

    def _send_file(self, path: Path, immutable: bool = False) -> None:
        """发送文件；文本类资源支持 gzip（结果按 mtime+size 缓存，避免重复压缩）。

        immutable=True 用于 vendor/ 下版本固定的第三方库（比如 3.5MB 的
        mermaid.min.js）：这类文件一旦发布就不会变，给长缓存可以让浏览器
        只下载一次；其它资源仍然 no-cache，保证改前端代码后立即生效。
        """
        ctype, _ = mimetypes.guess_type(str(path))
        ctype = ctype or "application/octet-stream"

        body: bytes | None = None
        encoding = None
        wants_gzip = "gzip" in (self.headers.get("Accept-Encoding") or "").lower()
        if wants_gzip and _is_compressible(ctype):
            try:
                body = _gzip_file(path)
                encoding = "gzip"
            except OSError:
                body = None

        size = len(body) if body is not None else path.stat().st_size
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(size))
        if encoding:
            self.send_header("Content-Encoding", encoding)
            self.send_header("Vary", "Accept-Encoding")
        if immutable:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        else:
            # 其余静态资源禁用缓存，避免改完前端旧代码还在生效
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        self.end_headers()
        if body is not None:
            self.wfile.write(body)
            return
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
                # env 块用于把容器侧只有 server 才能读到的运行时信息暴露给前端，
                # 目前包含：
                #   - cnb_web_url：CNB WebIDE 根 URL（形如 https://cnb-xxx-001.cnb.space）
                #     前端用它拼"打开云端 IDE"按钮的跳转地址 <root>/?folder=/workspace
                #     非 CNB 环境（本地 dev）则为空串，前端据此降级提示
                return self._send_json(
                    {
                        "courses": [scan_course(c) for c in COURSE_DIRS],
                        "env": {
                            "cnb_web_url": os.environ.get("CNB_VSCODE_WEB_URL", "").rstrip("/"),
                        },
                    }
                )
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

            if path == "/api/save":
                rel = body.get("path", "")
                content = body.get("content", "")
                if not isinstance(content, str):
                    return self._send_error_json(400, "content 必须是字符串")
                try:
                    target = _safe_resolve(rel)
                except ValueError as e:
                    return self._send_error_json(400, str(e))
                # 只允许保存各课 lab 下的 demo_*.py
                rel_norm = target.relative_to(ROOT).as_posix()
                if not re.match(r"^0[1-6]-.+/lab/demo_.+\.py$", rel_norm):
                    return self._send_error_json(400, "只允许编辑各课 lab 下的 demo_*.py")
                if len(content.encode("utf-8")) > 512 * 1024:
                    return self._send_error_json(413, "文件过大（>512KB）")
                target.write_text(content, encoding="utf-8")
                return self._send_json({"ok": True, "path": rel_norm, "size": len(content)})

            if path == "/api/notes/sync":
                # 把笔记批量写到 notes/<lecture-path>.md，并尝试 git commit (+push 由前端选择)
                items = body.get("notes", [])
                push = bool(body.get("push", False))
                if not isinstance(items, list):
                    return self._send_error_json(400, "notes 必须是数组")
                notes_root = ROOT / "notes"
                notes_root.mkdir(parents=True, exist_ok=True)

                written: list[str] = []
                for it in items:
                    p = (it or {}).get("path", "")
                    c = (it or {}).get("content", "")
                    if not isinstance(p, str) or not isinstance(c, str) or not p:
                        continue
                    # 安全：只允许把笔记写到当前仓库范围内的 notes/ 目录
                    safe_name = p.lstrip("/").replace("..", "_")
                    raw_name = safe_name
                    # 笔记路径本身常以 .md 结尾，别拼出 xxx.md.md
                    if safe_name.lower().endswith(".md"):
                        safe_name = safe_name[:-3]
                    out = (notes_root / (safe_name + ".md")).resolve()
                    try:
                        out.relative_to(notes_root.resolve())
                    except ValueError:
                        continue
                    out.parent.mkdir(parents=True, exist_ok=True)
                    header = (
                        f"# 笔记 · `{p}`\n\n"
                        f"> 同步时间：{time.strftime('%Y-%m-%d %H:%M:%S')}    "
                        f"来自 Course UI\n\n"
                    )
                    out.write_text(header + c.strip() + "\n", encoding="utf-8")
                    written.append(out.relative_to(ROOT).as_posix())
                    # 顺手清理旧版本拼出来的 xxx.md.md 重复文件
                    if safe_name != raw_name:
                        legacy = (notes_root / (raw_name + ".md")).resolve()
                        if legacy != out and legacy.is_file():
                            legacy.unlink()

                # 尝试 git add + commit；push 由前端勾选决定
                git_log: list[str] = []
                committed = False
                pushed = False
                commit_error = ""
                push_error = ""
                try:
                    if written:
                        rc, ot = _run_git(["add", "notes"], cwd=ROOT)
                        git_log.append(f"add: rc={rc} {ot.strip()[:200]}")
                        # 确认有变化才 commit
                        rc, status_out = _run_git(
                            ["status", "--porcelain", "notes"], cwd=ROOT
                        )
                        if status_out.strip():
                            msg = (
                                f"docs(notes): sync {len(written)} note(s) from Course UI"
                            )
                            # 身份沿用仓库/全局配置：CNB 环境里 commit 需要当前令牌用户签名，
                            # 写死一个假身份会被签名钩子拒绝（403），导致 commit 和 push 全部失败。
                            # 只有配置缺失时才用环境变量兜底。
                            _, cfg_name = _run_git(["config", "user.name"], cwd=ROOT)
                            _, cfg_mail = _run_git(["config", "user.email"], cwd=ROOT)
                            commit_args = ["commit", "-m", msg]
                            if not cfg_name.strip():
                                fallback = (
                                    os.environ.get("GIT_COMMITTER_NAME")
                                    or os.environ.get("CNB_TOKEN_USER_NAME")
                                    or "Course UI"
                                )
                                commit_args[:0] = ["-c", f"user.name={fallback}"]
                            if not cfg_mail.strip():
                                fallback = (
                                    os.environ.get("GIT_COMMITTER_EMAIL")
                                    or "course-ui@local"
                                )
                                commit_args[:0] = ["-c", f"user.email={fallback}"]
                            rc, ot = _run_git(commit_args, cwd=ROOT)
                            git_log.append(f"commit: rc={rc} {ot.strip()[:200]}")
                            committed = rc == 0
                            if not committed:
                                commit_error = _git_error_line(ot) or "git commit 失败"
                        else:
                            git_log.append("commit: skipped (no changes)")

                    # 只要用户勾了 push 就推：即使本次没有新 commit，
                    # 也可以把之前留在本地的提交送上去。
                    if push:
                        rc, br = _run_git(
                            ["rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT
                        )
                        branch = br.strip() if rc == 0 else ""
                        rc, _ = _run_git(
                            [
                                "rev-parse", "--abbrev-ref",
                                "--symbolic-full-name", "@{u}",
                            ],
                            cwd=ROOT,
                        )
                        has_upstream = rc == 0
                        if not has_upstream and branch and branch != "HEAD":
                            # 首次推送：绑定 origin/<branch>，下次直接 git push 即可
                            push_args = ["push", "-u", "origin", branch]
                        else:
                            push_args = ["push"]
                        rc, ot = _run_git(push_args, cwd=ROOT, timeout=120)
                        git_log.append(f"push: rc={rc} {ot.strip()[:300]}")
                        pushed = rc == 0
                        if not pushed:
                            push_error = _git_error_line(ot) or "git push 失败"
                except Exception as e:  # noqa: BLE001
                    git_log.append(f"git error: {e}")
                    push_error = push_error or f"git error: {e}"

                return self._send_json(
                    {
                        "ok": True,
                        "written": written,
                        "committed": committed,
                        "pushed": pushed,
                        "commit_error": commit_error,
                        "push_error": push_error,
                        "log": git_log,
                    }
                )

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
        # vendor/ 下是版本固定的第三方库（mermaid 等），给长缓存 + immutable，
        # 浏览器只需下载一次，之后打开讲义立刻就能画图。
        self._send_file(target, immutable=rel.startswith("vendor/"))

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
    addr = os.environ.get("HOST", "0.0.0.0")

    # 强制 IPv4，避免某些 Python 构建在 ::: 上监听导致 0.0.0.0 不可达
    import socket as _socket

    class _IPv4HTTPServer(ThreadingHTTPServer):
        address_family = _socket.AF_INET
        allow_reuse_address = True

    try:
        httpd = _IPv4HTTPServer((addr, port), Handler)
    except OSError as e:
        # 端口冲突最常见场景：
        #   1. 同一容器里 server.py 已经在跑（CNB only-preview 模式下 launch 被重试）
        #   2. 用户在另一个终端窗口已经跑了 run.sh
        # 这里给出明确指引，方便用户/讲师快速定位。
        if getattr(e, "errno", None) in (48, 98):  # macOS EADDRINUSE=48, Linux=98
            sys.stderr.write(
                f"\n[course-ui] ❌ 端口 {port} 已被占用，无法启动。\n"
                f"  · 排查：lsof -i :{port}    （或 fuser -v {port}/tcp）\n"
                f"  · 释放：fuser -k {port}/tcp 后重试\n"
                f"  · 或换端口：PORT=8765 bash course-ui/run.sh\n"
                f"  · 提示：CNB 预览容器固定使用 8686；本地/IDE 推荐 8765。\n\n"
            )
            sys.exit(2)
        raise

    # 启动日志只保留一行「预览链接」，避免讲师/学员被多行噪音淹没。
    # 优先用 CNB 官方推荐的独立子域名形态 —— 容器内注入了 CNB_VSCODE_PROXY_URI，
    # 值形如 "https://<workspace_id>-{{port}}.cnb.run"，把 {{port}} 替换成实际端口
    # 即得到外网可达的独立域名（如 https://jh5se5tst3-8765.cnb.run/）。
    # 老的 CNB_VSCODE_WEB_URL + /-/proxy/<port>/ 是 vscode-web 内嵌反代形态，
    # 链接又长又丑、且与 CNB 文档示例不一致，已弃用。
    # 本地/非 CNB 环境（两个变量都没有）则退化为 127.0.0.1:port，保证总有一行可见。
    proxy_tpl = os.environ.get("CNB_VSCODE_PROXY_URI", "").strip()
    if proxy_tpl and "{{port}}" in proxy_tpl:
        preview = proxy_tpl.replace("{{port}}", str(port)).rstrip("/") + "/"
    else:
        preview = f"http://127.0.0.1:{port}/"
    print(f"[course-ui] 🔗 预览链接：{preview}  (⌘/Ctrl + 点击打开)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[course-ui] 已退出")
        httpd.shutdown()


if __name__ == "__main__":
    main()
