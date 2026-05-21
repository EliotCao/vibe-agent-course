# 把 my-agent 接成 CNB NPC

把第 4 章自己写的 [`ch04-my-agent/main.py`](../ch04-my-agent/main.py)（极简版 Claude Code）
打包成 Docker 镜像，作为本仓库的 CNB NPC 运行时。

镜像基础借用了 [`looc/git-cnb`](https://cnb.cool/looc/git-cnb)，
直接用它的 `git-cnb` CLI 来回写评论，省掉自己拼 OpenAPI 的活。

## 目录结构

```
.
├── .cnb.yml                  # 流水线：构建/推送镜像 + NPC 事件
├── .cnb/settings.yml         # NPC 角色定义（小光）
├── ch04-my-agent/
│   ├── Dockerfile            # PyInstaller 打 my-agent + 内置 git-cnb + npc-entrypoint
│   ├── npc-entrypoint.sh     # NPC 真正的执行脚本（被 .cnb.yml 一行调用）
│   ├── .dockerignore
│   └── main.py               # 入口，--solo exec "task" -o file
└── docs/cnb-npc-setup.md     # 本文
```

## 工作原理

```
评论 "@owner/repo(小光) 帮我总结 README"
        │
        ▼
CNB 触发 issue.comment@npc / pull_request.comment@npc
        │
        ▼
拉镜像 ${CNB_DOCKER_REGISTRY}/${CNB_NPC_SLUG_LOWERCASE}:latest
        │
        ▼
插件任务直接跑容器 ENTRYPOINT = /usr/local/bin/npc-entrypoint
  ① 取 CNB_EVENT_COMMENT_BODY，去掉 @mention → task
  ② my-agent --solo exec "$task" -o /tmp/answer.md
  ③ git-cnb {issues|pull} comment-create ... --workmode
     （--workmode 让评论以 NPC 身份发出）
```

`.cnb.yml` 里的 NPC stage 用的是 CNB 的「插件任务」写法——
**只声明 `image`，不写 `script`**，CNB 会直接跑镜像 ENTRYPOINT。
所有真正逻辑都在 `ch04-my-agent/npc-entrypoint.sh`，改它重新 build 镜像即可。

> 插件任务的限制：`env:` 自定义环境变量不会传给容器，但 `CNB_*` 系统变量
> （含 `CNB_API_ENDPOINT` / `CNB_TOKEN` / `CNB_EVENT_*` 等）会自动注入，
> 我们恰好只用这些，所以无副作用。如果以后要传自定义变量，改用 `settings:`
> 字段（会带 `PLUGIN_` 前缀注入）。

## 镜像组装

`Dockerfile` 三段式：

| 阶段 | 内容 |
|---|---|
| `builder` (`python:3.11-slim-bookworm`) | PyInstaller `--onefile` 打 `my-agent`（pin 到 bookworm，与 runtime 同 glibc） |
| `gitcnb` (`docker.cnb.cool/looc/git-cnb:latest`) | 仅作为复制源，从中拷出静态 `git-cnb` 二进制 |
| `runtime` (`debian:bookworm-slim`) | 装 `git/git-lfs/curl/jq/ca-certificates`，把上面两个二进制都丢进 `/usr/local/bin/` |

为什么 runtime 不直接用 `git-cnb` 镜像（alpine）作为底？  
因为 PyInstaller 在 Debian/glibc 上打的二进制**不能**在 Alpine/musl 上跑。要么 builder 也切 alpine（坑多），要么 runtime 切回 glibc 系——选了后者。`git-cnb` 自己是 `CGO_ENABLED=0` 的纯静态二进制，从 alpine 拷到 debian 完全没问题。

## 镜像构建

仓库 `main` push 时自动构建。本地手工：

```bash
cd ch04-my-agent
docker build -t my-agent:latest .

# 试跑
docker run --rm \
  -e BASE_URL -e API_KEY -e MODEL_ID \
  my-agent:latest --solo exec "你好" -o -

# 验证 git-cnb 也在
docker run --rm --entrypoint git-cnb my-agent:latest version
```

## NPC 调用方式

在**本仓库**任意 Issue / PR 的评论里：

```text
@<owner>/<repo>(小光) 帮我总结一下 README
```

`小光` = `.cnb/settings.yml` 里的角色名。流水线跑完后，
回复评论的提交者会显示为「小光」（靠 `git-cnb --workmode`）。

## 关键点

### 1. `git-cnb --workmode` 是 NPC 身份的关键
没有 `--workmode` 时评论提交者是 `CNB_TOKEN` 对应的人；带上 `--workmode`
评论会以 NPC 角色名提交，这就是要的"NPC 在回复"的效果。

### 2. flag 名居然不一样
| 子命令 | 评论内容 flag |
|---|---|
| `git-cnb issues comment-create` | `-c / --comment` |
| `git-cnb pull comment-create`   | `-b / --body` |

`.cnb.yml` 里按事件类型分开写了两路，别合并。

### 3. token 复用
`my-agent`（LLM 调用）和 `git-cnb`（OpenAPI 调用）都用同一个 `CNB_TOKEN`，
流水线注入的环境变量自动可见，不用额外配。

### 4. 不用 `npc:go`
CNB 内置的 `npc:go` 是平台自带的 NPC runtime（自己驱动模型 + Skills），
用了它就跑不到 `main.py`。这里走 `script:` 直接调 `my-agent`，
真正用第 4 章那套 Function Calling 循环。

## 关键环境变量

由 CNB 注入：

| 变量 | 用途 |
|---|---|
| `CNB_API_ENDPOINT` | LLM base_url 拼接 |
| `CNB_REPO_SLUG` | LLM base_url 拼接 + git-cnb `--repo` |
| `CNB_TOKEN` | LLM 鉴权 + git-cnb 鉴权 |
| `CNB_DOCKER_REGISTRY` | 镜像仓库地址 |
| `CNB_NPC_SLUG_LOWERCASE` | NPC 所在仓库 slug（事件里拉镜像用） |
| `CNB_REPO_SLUG_LOWERCASE` | 当前仓库 slug（push 时推镜像用） |
| `CNB_EVENT_COMMENT_BODY` | 触发 NPC 的评论原文 |
| `CNB_EVENT_ISSUE_NUMBER` / `CNB_EVENT_PULL_REQUEST_NUMBER` | 评论目标编号 |
| `CNB_EVENT` | 区分 issue/pr 评论 |
| `CNB_WORKSPACE` | 流水线工作目录 |

## 排错速查

| 现象 | 排查 |
|---|---|
| `pyinstaller` 阶段报缺包 | 项目用裸包名导入；如新增模块，在 Dockerfile 里加 `--collect-submodules <pkg>` |
| 启动报 `GLIBC_2.XX not found` | builder 和 runtime 必须同发行版；当前都是 bookworm（glibc 2.36），别把 builder 换成裸 `python:3.11-slim`（滚动 tag 已经跟到 trixie）|
| 镜像跑起来但 `git-cnb: not found` | 检查 builder 里 `COPY --from=gitcnb /app/git-cnb` 路径是否随上游变动 |
| my-agent 报 `请设置 BASE_URL...` | `CNB_API_ENDPOINT` / `CNB_REPO_SLUG` / `CNB_TOKEN` 是否注入到容器 |
| 评论发出去了但作者不是 NPC 角色 | 漏了 `--workmode` |
| 跨仓 fork PR 时 git-cnb 401 | NPC 流水线中 `CNB_TOKEN` 仅限当前仓 + 最大 Developer 角色，无法写入源仓库 |
| 不知道 `CNB_EVENT_*` 变量名是否拼对 | 在脚本开头加一句 `env | grep ^CNB_ | sort` 打印对照 |
