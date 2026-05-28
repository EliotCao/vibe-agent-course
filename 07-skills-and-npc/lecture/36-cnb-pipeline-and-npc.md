# 第 36 节 · CNB Pipeline + NPC 配置

## 一句话回答

> **两个 YAML 文件把"评论 @ → 自动回复"的链路串起来。** `.cnb.yml` 定义流水线（什么时候用什么镜像跑什么命令），`.cnb/settings.yml` 定义 NPC 角色。

## 完整链路回顾

```
评论 @owner/repo(my-agent) 帮我看看 bug
         ↓
CNB 检测到 NPC 被 @ → 触发 .cnb.yml 里定义的 NPC 事件流水线
         ↓
流水线启动 Docker 容器（你的镜像）
         ↓
容器里 npc-entrypoint.sh 读 CNB 环境变量、调 my-agent
         ↓
my-agent 输出答案 → git-cnb 以 NPC 身份回写评论
```

## .cnb/settings.yml —— 定义 NPC 角色

```yaml
# .cnb/settings.yml
settings:
  npc:
    - name: my-agent
      description: "仓库 Coding Agent，可以帮你看代码、修 bug、跑测试"
```

| 字段 | 含义 |
|---|---|
| `name` | NPC 名字（@ 时用这个名字触发） |
| `description` | NPC 自我介绍（hover 时显示） |

## .cnb.yml —— 定义 NPC 事件流水线

```yaml
# .cnb.yml
main:
  push:
    - docker:
        image: docker.cnb.cool/${{ cnb.repo_slug }}/my-agent:latest
        stages:
          - name: build-npc
            script: echo "NPC 镜像构建"

npc:
  issue.comment@npc:
    - docker:
        image: docker.cnb.cool/${{ cnb.repo_slug }}/my-agent:latest
        stages:
          - name: npc-reply
            env:
              HUNYUAN_API_KEY: ${{ secrets.HUNYUAN_API_KEY }}
              HUNYUAN_BASE_URL: ${{ secrets.HUNYUAN_BASE_URL }}
            script: npc-entrypoint

  pull_request.comment@npc:
    - docker:
        image: docker.cnb.cool/${{ cnb.repo_slug }}/my-agent:latest
        stages:
          - name: npc-reply
            env:
              HUNYUAN_API_KEY: ${{ secrets.HUNYUAN_API_KEY }}
              HUNYUAN_BASE_URL: ${{ secrets.HUNYUAN_BASE_URL }}
            script: npc-entrypoint
```

### 关键点

| 配置 | 含义 |
|---|---|
| `npc:` 顶层 key | 声明这是 NPC 事件流水线 |
| `issue.comment@npc` | 触发条件：有人在 Issue 评论里 @ 了 NPC |
| `pull_request.comment@npc` | 触发条件：有人在 PR 评论里 @ 了 NPC |
| `image:` | 你构建好的 Docker 镜像地址 |
| `env:` | 从仓库 Secrets 注入 API Key |
| `script: npc-entrypoint` | 跑 npc-entrypoint.sh |

## npc-entrypoint.sh —— 容器里的粘合脚本

做 3 件事：
1. 从 `CNB_NPC_TRIGGER_CONTENT` 提取任务文本（去掉 @ mention）
2. 调 `my-agent --solo exec "$task"` 执行
3. 用 `git-cnb` 把答案以 NPC 身份回写评论

## 动手试试

1. 把提供的 `.cnb.yml` 和 `.cnb/settings.yml` 模板复制到你的仓库根
2. 改 NPC 名字为你想要的（比如 "coding-buddy"）
3. 在仓库 Settings → Secrets 里加两个：`HUNYUAN_API_KEY` + `HUNYUAN_BASE_URL`
4. git push 一次让流水线构建镜像
5. 在 Issue 里评论 `@你的用户名/仓库名(coding-buddy) 介绍下这个项目` → 等 NPC 回复

## 常见问题排查

| 症状 | 原因 | 解法 |
|---|---|---|
| NPC 没反应 | `.cnb/settings.yml` 里 name 跟 @ 的不一致 | 检查拼写，大小写敏感 |
| 流水线报"镜像不存在" | 还没推过镜像 / 镜像地址写错 | 先 push 一次触发 build |
| "GLIBC_2.38 not found" | builder 和 runtime glibc 版本不对齐 | Dockerfile 两阶段用同一 Debian 版本 |
| NPC 回复为空 | my-agent 执行失败 | 看流水线日志的 stderr |
| "permission denied" | Secrets 没配或名字错 | 检查仓库 Secrets |

## 小结

- `.cnb/settings.yml` 定义 NPC 角色（name + description）
- `.cnb.yml` 定义 NPC 事件流水线（什么事件 → 跑什么镜像 → 跑什么脚本）
- `npc-entrypoint.sh` 是容器内的粘合脚本（读事件 → 调 Agent → 回写评论）
- 只需要：改名字 + 加 Secrets + push + 在 Issue 里 @ 就完成了
