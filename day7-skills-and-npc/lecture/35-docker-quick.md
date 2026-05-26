# 第 35 节 · Docker 速通：运行容器 + 写 Dockerfile

## 一句话回答

> **Docker = 把你的 Agent + 依赖 + 运行环境打成一个"集装箱"，在任何地方都能一键跑起来。**

## 为什么需要 Docker

![为什么需要 Docker 打包](./images/35-why-docker.png)

你 Day6 的 Agent 在本地能跑，但：
- 队友的电脑上 Python 版本不一样 → 跑不起来
- CNB 流水线要启动你的 Agent → 不知道怎么装依赖
- 你重装系统后 → 环境没了

Docker 解法：**一切都打进镜像里，到哪儿都一样**。

## 5 个核心概念（大二够用）

| 概念 | 一句话 | 类比 |
|---|---|---|
| **镜像 Image** | 打包好的"模板" | 做好的蛋糕模具 |
| **容器 Container** | 镜像跑起来的一个实例 | 用模具做出来的一个蛋糕 |
| **Dockerfile** | 描述"怎么做这个模具"的说明书 | 蛋糕配方 |
| **Registry** | 存放镜像的仓库 | 蛋糕模具商店 |
| **Volume** | 容器里的持久化文件夹 | 蛋糕店的冷柜 |

## Dockerfile 速通

我们的 Dockerfile 用**两阶段构建**（生产级标准做法）：

```dockerfile
# ==== Stage 1: 构建 ====
FROM python:3.11-slim-bookworm AS builder
WORKDIR /build
COPY . /build
RUN pip install --no-cache-dir openai pyinstaller
RUN pyinstaller --onefile --name my-agent main.py

# ==== Stage 2: 运行 ====
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates git bash curl jq
COPY --from=builder /build/dist/my-agent /usr/local/bin/my-agent
COPY npc-entrypoint.sh /usr/local/bin/npc-entrypoint
ENTRYPOINT ["/usr/local/bin/npc-entrypoint"]
```

### 为什么两阶段

| 阶段 | 包含什么 | 大小 |
|---|---|---|
| builder | Python + pip + pyinstaller + 全部源码 | ~800MB |
| runtime | 只有编译好的二进制 + git + bash | ~150MB |

最终推送到 Registry 的只有 runtime 层——**小了 5 倍**。

### 关键坑：glibc 版本必须对齐

> builder 用 `python:3.11-slim-bookworm`，runtime 也必须用 `debian:bookworm`。
> 如果 builder 用了更新的 Debian（比如 trixie），编译出的二进制会依赖 glibc 2.38，
> 但 bookworm 只有 glibc 2.36 → 运行时报 `GLIBC_2.38 not found`。

## 跑一下试试

```bash
# 构建镜像（在包含 Dockerfile 的目录里执行）
docker build -t my-agent:latest .

# 跑一下看看 help
docker run --rm my-agent:latest --help

# 用交互模式进容器看看里面有什么
docker run --rm -it --entrypoint bash my-agent:latest
```

## 动手试试

1. 用老师发的 Dockerfile 模板，改一下 `COPY . /build` 路径（如果你的目录结构不同）
2. 本地 `docker build -t my-agent:latest .` 构建一次
3. `docker run --rm my-agent:latest --help` 确认二进制能跑

**不要从零写 Dockerfile**——今天重点是 Skills + NPC，Docker 只是"交通工具"。

## 小结

- Docker = 打包环境的"集装箱"
- Dockerfile = 构建说明书，两阶段构建让镜像小 5 倍
- 关键坑：builder 和 runtime 的 glibc 版本必须对齐
- 今天你只需要改模板里的路径，不需要从零写
