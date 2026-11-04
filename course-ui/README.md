# Course UI · 课程学习中心

把仓库中 `01 ~ 06` 节课的 Markdown 讲义渲染成更易读的网页，并支持
**一键运行 Python Demo**、实时回流标准输出/标准错误，可在终端面板里
向交互式 Demo 注入 stdin。

## 快速开始

**零依赖**：服务用 Python 标准库实现，不需要安装 FastAPI 等额外包。

```bash
# 在仓库根目录执行（任选其一）
python3 course-ui/server.py        # 直接跑
bash   course-ui/run.sh            # 启动脚本
```

> 默认监听 `0.0.0.0:8765`，可用环境变量 `PORT=9000 HOST=127.0.0.1` 覆盖。

打开浏览器访问 <http://localhost:8765>。

> **运行 LLM 相关 demo 之前**：参考 `.env.example` 在仓库根目录创建
> `.env`，填入 `BASE_URL` / `API_KEY` / `MODEL_ID`，否则 demo 会因
> 缺凭据而报 `EnvironmentError`。

## 功能

- 📚 **讲义美化**：左侧自动列出 6 节课的所有 lecture markdown，使用
  marked + highlight.js 渲染，支持代码块高亮、表格、引用、相对图片。
- 📊 **Mermaid 图表**：讲义里的 ```mermaid 代码块会渲染成 SVG 流程图
  （本地 `vendor/mermaid.min.js`，离线可用，仅在页面含图表时按需加载；
  渲染失败自动降级为原始代码块）。
- 🐍 **Demo 一键运行**：每节课的 `lab/demo_*.py` 渲染为可运行卡片，
  ▶ 按钮通过 SSE 流式回传 stdout/stderr，按行实时显示。
- ⌨️ **stdin 注入**：交互式 demo（如 `demo_00_chat.py`）可在终端面板
  下方的输入框打字 + 回车发送给运行中的 Python 进程。
- 🛑 **强制停止**：点 ■ 终止运行中的 demo。
- 🔍 **查看源码**：在卡片里展开任意 demo 的源码，便于一边看一边跑。

## Python 解释器选择

服务启动 demo 时按以下优先级挑选 Python：

1. 仓库根目录的 `.venv/bin/python`（推荐：在仓库根目录跑 `uv sync --all-packages` 即可生成）
2. 当前服务进程使用的 `sys.executable`

> 如果 demo 报 `ModuleNotFoundError: openai` 等，说明所选 Python 缺依赖。
> 解决方式：在仓库根目录执行 `uv sync --all-packages`，会创建一个
> 包含所有课程依赖的 `.venv`。

## 目录结构

```
course-ui/
├── server.py            # HTTP/SSE 服务（纯 stdlib）
├── run.sh               # 一键启动脚本
└── static/
    ├── index.html       # 单页应用入口
    ├── styles.css       # 暗色主题
    └── app.js           # 渲染 + 运行逻辑
```

## 安全限制

- `/api/file` 只允许读取 `.md / .py / .txt` 且必须位于仓库内。
- `/api/run` 只允许执行 `0X-*/lab/demo_*.py`，路径严格校验。
- `/api/asset` 只允许图片资源（png/jpg/jpeg/gif/webp/svg）。
- 服务默认监听 `0.0.0.0`，在云环境/容器内可被外部访问；
  本地开发如需仅限本机，可设置 `HOST=127.0.0.1`。
