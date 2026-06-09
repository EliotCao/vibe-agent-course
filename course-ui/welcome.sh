#!/usr/bin/env bash
# course-ui/welcome.sh
# 进入 CNB WebIDE 后展示课程学习中心入口信息。
# 触发方式（按优先级）：
#   1. cnb-welcome 插件：读取 env.CNB_WELCOME_CMD，首次打开终端时自动执行
#   2. VSCode 终端 Profile：.vscode/settings.json 中配置默认终端启动时运行本脚本
# 通过 /tmp 锁文件避免重复输出。

set -u

# 避免同一容器会话内重复显示
LOCK="/tmp/.cnb_welcome_shown"
[ -f "$LOCK" ] && exit 0
touch "$LOCK"

# 颜色（如果终端不支持就静默降级为空）
B="$(printf '\033[1m')";   D="$(printf '\033[0m')"
C="$(printf '\033[36m')";  G="$(printf '\033[32m')";  Y="$(printf '\033[33m')"
M="$(printf '\033[35m')";  W="$(printf '\033[97m')"
# 反白高亮（用于"可复制命令"），降级时退化为加粗
INV="$(printf '\033[7m')"

cat <<EOF

${C}${B}╔══════════════════════════════════════════════════════════════════════╗${D}
${C}${B}║${D}                                                                      ${C}${B}║${D}
${C}${B}║${D}    ${M}${B}🚀  Vibe Agent · 课程学习中心${D}                                  ${C}${B}║${D}
${C}${B}║${D}                                                                      ${C}${B}║${D}
${C}${B}║${D}    ${W}三栏阅读 + 一键运行 Demo + 可编辑代码 + 笔记同步${D}              ${C}${B}║${D}
${C}${B}║${D}                                                                      ${C}${B}║${D}
${C}${B}╚══════════════════════════════════════════════════════════════════════╝${D}

  ${G}${B}▶ 第 1 步：在下方终端粘贴并回车，启动课程 UI${D}

      ${INV}${B} bash course-ui/run.sh ${D}

  ${G}${B}▶ 第 2 步：在 server 启动日志里拿到预览链接${D}

      ${W}启动后终端会打印一行 ${Y}🔗 预览链接：https://xxxx-8765.cnb.run/${D}
      ${W}该链接由 CNB 端口转发实时生成，⌘/Ctrl + 点击即可在浏览器打开${D}
      ${W}（链接随容器实例动态变化，不要从其它文档复制粘贴）${D}

  ${G}${B}▶ 文档${D}
      ${W}- 总览：${D}course-ui/README.md
      ${W}- 课程：${D}README.md
      ${W}- 准备 .env：${D}cp .env.example .env  ${W}# 然后填 BASE_URL / API_KEY / MODEL_ID${D}

EOF
