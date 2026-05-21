#!/usr/bin/env bash
# =====================================================================
# my-agent NPC entrypoint
#
# 仅在 CNB NPC 事件流水线里被调用，做三件事：
#   1) 从 CNB_NPC_TRIGGER_CONTENT 提取任务文本（去掉 @mention）
#   2) my-agent --solo exec "$task" -o /tmp/answer.md
#   3) 用 git-cnb 把答案以 --workmode 回写到对应 issue / pr 评论
#      （--workmode → 评论提交者显示为 NPC 角色名）
#
# 由 CNB 注入的环境变量 (摘自 docs.cnb.cool/zh/build/build-in-env.md):
#   CNB_API_ENDPOINT / CNB_REPO_SLUG / CNB_TOKEN  → my-agent + git-cnb 鉴权
#   CNB_WORKSPACE                                → 流水线工作目录
#   CNB_EVENT                                    → 事件名 (issue.comment@npc / pull_request.comment@npc)
#   CNB_NPC_TRIGGER_CONTENT                      → 触发 NPC 的内容（评论原文/issue/PR 描述等，统一入口）
#   CNB_ISSUE_IID                                → issue 仓库编号（issue 评论时有值）
#   CNB_PULL_REQUEST_IID                         → PR 仓库编号（PR 评论时有值）
# =====================================================================
set -eu

# debug：把所有 CNB_* 变量打到 stderr，方便确认变量名
echo "[npc] === CNB env ===" >&2
env | grep ^CNB_ | sort >&2 || true
echo "[npc] ================" >&2

# ---- 1. 取任务文本 ----
# CNB_NPC_TRIGGER_CONTENT 是文档推荐的统一入口，issue/PR 评论都自动等效到它
raw="${CNB_NPC_TRIGGER_CONTENT:-${CNB_COMMENT_BODY:-}}"
# 去掉 @xxx 或 @owner/repo(角色)
task="$(printf '%s' "$raw" | sed -E 's/@[A-Za-z0-9_./-]+(\([^)]*\))?//g' | sed -E 's/^[[:space:]]+//')"

if [ -z "$task" ]; then
  task="请总结当前仓库的 README，并指出可改进的点。"
fi

echo "[npc] task: $task" >&2

# ---- 2. 跑 my-agent ----
workdir="${CNB_WORKSPACE:-$PWD}"
my-agent --solo exec "$task" -w "$workdir" -o /tmp/answer.md

# ---- 3. 用 git-cnb 回写评论 ----
# 优先按 PR 处理；CNB_PULL_REQUEST_IID 有值就是 PR 评论，否则按 issue
# 注意 flag 不一致：
#   issues comment-create  用 --comment / -c
#   pull   comment-create  用 --body    / -b
# 都加 --workmode → 评论以 NPC 身份提交
if [ -n "${CNB_PULL_REQUEST_IID:-}" ]; then
  echo "[npc] reply to PR #$CNB_PULL_REQUEST_IID" >&2
  git-cnb --repo "$CNB_REPO_SLUG" pull comment-create \
    -n "$CNB_PULL_REQUEST_IID" -b "$(cat /tmp/answer.md)" --workmode
elif [ -n "${CNB_ISSUE_IID:-}" ]; then
  echo "[npc] reply to issue #$CNB_ISSUE_IID" >&2
  git-cnb --repo "$CNB_REPO_SLUG" issues comment-create \
    -n "$CNB_ISSUE_IID" -c "$(cat /tmp/answer.md)" --workmode
else
  echo "[npc] no issue/pr IID, skip comment" >&2
  exit 0
fi

echo "[npc] comment posted as NPC" >&2
