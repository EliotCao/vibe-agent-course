#!/usr/bin/env bash
# 一键启动 Course UI 服务（纯 stdlib，无需安装额外依赖）
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

cd "$ROOT"

# 选择 Python：优先用仓库 .venv，其次系统 python3
if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

PORT="${PORT:-8765}"
HOST="${HOST:-0.0.0.0}"
# 启动前不再打印「启动 http://...」预告 —— server.py 起来后会直接输出一行
# 「🔗 预览链接：...」，那是真正可达的 URL，避免重复噪音。
PORT="$PORT" HOST="$HOST" "$PY" "$HERE/server.py"
