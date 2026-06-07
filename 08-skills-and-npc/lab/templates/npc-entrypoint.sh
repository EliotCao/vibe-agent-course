#!/usr/bin/env bash
# NPC entrypoint（学生模板）
# 做三件事：提取任务 → 跑 Agent → 回写评论
set -eu

echo "[npc] === CNB env ===" >&2
env | grep ^CNB_ | sort >&2 || true

# 1. 取任务文本（去掉 @mention）
raw="${CNB_NPC_TRIGGER_CONTENT:-}"
task="$(printf '%s' "$raw" | sed -E 's/@[A-Za-z0-9_./-]+(\([^)]*\))?//g' | sed -E 's/^[[:space:]]+//')"

if [ -z "$task" ]; then
  task="请总结当前仓库的 README，并指出可改进的点。"
fi

echo "[npc] task: $task" >&2

# 2. 跑 Agent
workdir="${CNB_WORKSPACE:-$PWD}"
my-agent --solo exec "$task" -w "$workdir" -o /tmp/answer.md

# 3. 回写评论（NPC 身份）
if [ -n "${CNB_PULL_REQUEST_IID:-}" ]; then
  echo "[npc] reply to PR #$CNB_PULL_REQUEST_IID" >&2
  git-cnb --repo "$CNB_REPO_SLUG" pull comment-create \
    -n "$CNB_PULL_REQUEST_IID" -b "$(cat /tmp/answer.md)" --workmode
elif [ -n "${CNB_ISSUE_IID:-}" ]; then
  echo "[npc] reply to issue #$CNB_ISSUE_IID" >&2
  git-cnb --repo "$CNB_REPO_SLUG" issues comment-create \
    -n "$CNB_ISSUE_IID" -c "$(cat /tmp/answer.md)" --workmode
else
  echo "[npc] no issue/pr IID, skip" >&2
fi

echo "[npc] done" >&2
