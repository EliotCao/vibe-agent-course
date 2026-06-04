#!/usr/bin/env bash
# course-ui/welcome.sh
# 进入 CNB WebIDE 后，cnbcool/cnb-welcome 插件会自动打开终端运行此脚本。
# 由 .cnb.yml 中 vscode 事件的 env.CNB_WELCOME_CMD 触发。

set -u

# 颜色（如果终端不支持就静默降级为空）
B="$(printf '\033[1m')";   D="$(printf '\033[0m')"
C="$(printf '\033[36m')";  G="$(printf '\033[32m')";  Y="$(printf '\033[33m')"
M="$(printf '\033[35m')";  W="$(printf '\033[97m')"

# 端口转发预览 URL（CNB 提供 CNB_VSCODE_WEB_URL，再拼端口前缀）
PORT="${PORT:-8765}"
PREVIEW_URL=""
if [ -n "${CNB_VSCODE_WEB_URL:-}" ]; then
  # CNB 端口转发地址形如 https://<workspace-host>/-/proxy/<port>/
  PREVIEW_URL="${CNB_VSCODE_WEB_URL%/}/-/proxy/${PORT}/"
fi

cat <<EOF

${C}${B}╔══════════════════════════════════════════════════════════════════════╗${D}
${C}${B}║${D}                                                                      ${C}${B}║${D}
${C}${B}║${D}    ${M}${B}🚀  Vibe Agent · 课程学习中心${D}                                  ${C}${B}║${D}
${C}${B}║${D}                                                                      ${C}${B}║${D}
${C}${B}║${D}    ${W}三栏阅读 + 一键运行 Demo + 可编辑代码 + 笔记同步${D}              ${C}${B}║${D}
${C}${B}║${D}                                                                      ${C}${B}║${D}
${C}${B}╚══════════════════════════════════════════════════════════════════════╝${D}

  ${G}${B}▶ 启动课程 UI（一行命令即可）${D}

      ${Y}bash course-ui/run.sh${D}

  ${G}${B}▶ 启动后访问${D}

EOF

if [ -n "$PREVIEW_URL" ]; then
  echo "      ${C}${B}${PREVIEW_URL}${D}"
  echo
  echo "      ${W}（CNB 已自动做端口转发，复制到浏览器或 Cmd/Ctrl+点击直接打开）${D}"
else
  echo "      ${W}- 在 VSCode 右下角弹窗里点 'Open in Browser'${D}"
  echo "      ${W}- 或在 PORTS / 端口转发面板找到 8765${D}"
fi

cat <<EOF

  ${G}${B}▶ 也可点击仓库分支页右上角的「📚 课程学习中心」按钮${D}
      ${W}（CNB 自定义按钮，免在 IDE 里手动启动）${D}

  ${G}${B}▶ 文档${D}
      ${W}- 总览：${D}course-ui/README.md
      ${W}- 课程：${D}README.md
      ${W}- 准备 .env：${D}cp .env.example .env  ${W}# 然后填 BASE_URL / API_KEY / MODEL_ID${D}

EOF
