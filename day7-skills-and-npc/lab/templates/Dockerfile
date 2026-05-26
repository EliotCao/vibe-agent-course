# my_coding_agent NPC 运行时镜像（学生模板）
#
# 使用方式：
#   1. 把 my_coding_agent/ 目录连同此文件一起放到仓库根
#   2. docker build -t my-agent:latest .
#   3. 推到 CNB Registry: docker.cnb.cool/<owner>/<repo>/my-agent:latest
#
# 两阶段构建：builder 编译二进制，runtime 只留运行环境。

# ============== Stage 1: build ==============
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils \
    && rm -rf /var/lib/apt/lists/*

# 复制项目源码
COPY . /build

# 安装依赖 + PyInstaller
RUN pip install --no-cache-dir \
        "openai>=1.0.0" \
        "numpy>=1.24.0" \
        "pyinstaller>=6.0"

# 打包成单文件二进制
RUN pyinstaller \
        --onefile \
        --name my-agent \
        --collect-submodules llm \
        --collect-submodules tools \
        --collect-submodules context \
        --collect-submodules memory \
        --collect-submodules skills \
        --collect-submodules agent \
        --collect-submodules ui \
        --paths /build \
        main.py \
    && /build/dist/my-agent --help >/dev/null

# ============== Stage 2: runtime ==============
FROM docker.cnb.cool/looc/git-cnb:latest AS gitcnb

FROM debian:bookworm-slim AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates git git-lfs curl jq bash \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

# git-cnb 二进制（跨发行版可用）
COPY --from=gitcnb /app/git-cnb /usr/local/bin/git-cnb
RUN chmod +x /usr/local/bin/git-cnb

# my-agent 二进制
COPY --from=builder /build/dist/my-agent /usr/local/bin/my-agent
RUN chmod +x /usr/local/bin/my-agent

# NPC 入口脚本
COPY npc-entrypoint.sh /usr/local/bin/npc-entrypoint
RUN chmod +x /usr/local/bin/npc-entrypoint

ENV PYTHONUNBUFFERED=1 TERM=xterm-256color

ENTRYPOINT ["/usr/local/bin/npc-entrypoint"]
