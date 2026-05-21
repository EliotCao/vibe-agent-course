# 第 4 章 my-agent —— CNB NPC 运行时镜像
#
# 思路：
#   ① builder 阶段：用 PyInstaller 把 ch04-my-agent/main.py 打成单文件二进制 my-agent
#   ② runtime 阶段：基于 docker.cnb.cool/looc/git-cnb:latest
#      —— 自带 git-cnb / git / bash / curl / jq，正好用来回写评论
#      —— 只需把 my-agent 二进制丢到 PATH 里
#
# 产出二进制无需 Python 解释器（PyInstaller bootstrap 自解包到 /tmp）。

# ============== Stage 1: build my-agent ==============
# 关键：builder 必须 pin 到与 runtime 同一发行版 (bookworm)，否则
# PyInstaller 打出的二进制会依赖更高版本 glibc，runtime 上 GLIBC_2.38 not found。
# `python:3.11-slim` 是滚动 tag，会跟到 trixie (glibc 2.38)，不能用。
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# binutils: PyInstaller 在某些平台需要
RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils \
    && rm -rf /var/lib/apt/lists/*

COPY . /build

RUN pip install --no-cache-dir \
        "openai>=1.0.0" \
        "python-dotenv>=1.0.0" \
        "rich>=13.0.0" \
        "pyinstaller>=6.0"

# --collect-submodules: 项目用裸包名导入（from llm import LLM 等），显式声明更稳
RUN pyinstaller \
        --onefile \
        --name my-agent \
        --collect-all rich \
        --collect-submodules llm \
        --collect-submodules tools \
        --collect-submodules context \
        --collect-submodules memory \
        --collect-submodules skills \
        --collect-submodules ui \
        --paths /build \
        main.py \
    && /build/dist/my-agent --help >/dev/null

# ============== Stage 2: runtime ==============
# 直接用 git-cnb 官方镜像作为底，自带 git-cnb / git / curl / jq / bash
# 镜像基础是 alpine + glibc-free，PyInstaller 单文件二进制能跑
# 但需要确认 my-agent 能在 musl 环境运行 —— python:3.11-slim 是 glibc，
# 打出来的二进制依赖 glibc，所以 runtime 必须也是 glibc 系。
#
# 解决方案：runtime 用 git-cnb 镜像，从中拷出 git-cnb 二进制；
#          自身仍基于 debian-slim（glibc）以兼容 my-agent。
FROM docker.cnb.cool/looc/git-cnb:latest AS gitcnb

FROM debian:bookworm-slim AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates git git-lfs curl jq \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# 1) 从 git-cnb 镜像拷出二进制（就一个静态文件，跨发行版可用）
COPY --from=gitcnb /app/git-cnb /usr/local/bin/git-cnb
RUN chmod +x /usr/local/bin/git-cnb

# 2) 拷入 my-agent
COPY --from=builder /build/dist/my-agent /usr/local/bin/my-agent
RUN chmod +x /usr/local/bin/my-agent

ENV PYTHONUNBUFFERED=1 \
    TERM=xterm-256color

# 默认入口：以 solo 模式接收任务
ENTRYPOINT ["/usr/local/bin/my-agent"]
CMD ["--help"]
