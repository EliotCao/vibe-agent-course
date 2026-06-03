# CNB 平台实战指南

> 本文档涵盖三个实用主题：
> 1. CNB 大模型 API 的使用方法
> 2. CNB 云原生预览功能
> 3. 将 Agent Web 应用部署为云原生预览

---

## 一、CNB 大模型 API 使用方法

### 1.1 接口概述

CNB 平台内置了兼容 **OpenAI API** 协议的大模型接口，可直接在云原生开发环境和云原生构建流水线中使用，**无需额外申请 API Key**。

**接口地址格式：**

```
{CNB_API_ENDPOINT}/{CNB_REPO_SLUG}/-/ai-ide/v2
```

例如：`https://api.cnb.cool/my-org/my-repo/-/ai-ide/v2`

**认证方式：** 使用平台自动注入的 `CNB_TOKEN` 作为 Bearer Token（等同于 OpenAI 的 `api_key`）。

### 1.2 可用模型

| 模型 ID | 说明 |
|---------|------|
| `glm-5.0` | 默认模型，智谱 GLM 系列 |
| 其他模型 | 通过 `MODEL_ID` 环境变量切换 |

> 💡 在云端智能体（Happy CNB）中，还支持 GLM、Kimi、混元（HY）等模型，可在 Agent 设置中切换。

### 1.3 CNB 默认环境变量（与 AI 相关）

在云原生开发 / 云原生构建环境中，以下环境变量**自动注入**，无需手动配置：

| 环境变量 | 说明 |
|----------|------|
| `CNB_API_ENDPOINT` | API 完整地址（如 `https://api.cnb.cool`） |
| `CNB_REPO_SLUG` | 仓库路径（如 `my-org/my-repo`） |
| `CNB_TOKEN` | 流水线运行期临时令牌，可用作 API Key |
| `CNB_WEB_PROTOCOL` | Web 协议（`http` 或 `https`） |
| `CNB_WEB_HOST` | Web 使用的 HOST |
| `CNB_VSCODE_PROXY_URI` | 云原生开发中的端口代理 URI 模板 |

**NPC 场景额外变量：**

| 环境变量 | 说明 |
|----------|------|
| `CNB_NPC_PROMPT` | NPC 角色提示词（System Prompt） |
| `CNB_NPC_TRIGGER_CONTENT` | 触发 NPC 的用户输入内容 |
| `CNB_NPC_ENABLE_THINKING` | 是否开启思考模式 |
| `CNB_NPC_ENABLE_WORKMODE` | 是否开启工作模式（更高权限） |
| `CNB_NPC_NAME` | NPC 角色名 |

### 1.4 快速调用示例

```python
"""在 CNB 云原生开发环境中调用大模型"""
import os
from openai import OpenAI

# 自动从 CNB 环境变量拼接
endpoint = os.environ["CNB_API_ENDPOINT"]
repo_slug = os.environ["CNB_REPO_SLUG"]
base_url = f"{endpoint}/{repo_slug}/-/ai-ide/v2"

client = OpenAI(
    base_url=base_url,
    api_key=os.environ["CNB_TOKEN"],
)

response = client.chat.completions.create(
    model="glm-5.0",
    messages=[
        {"role": "system", "content": "你是一个编程助手"},
        {"role": "user", "content": "用 Python 写一个快速排序"},
    ],
    stream=True,
)

for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 1.5 本地开发时的配置

如果在本地开发（非 CNB 环境），通过 `.env` 文件手动配置：

```bash
# .env
BASE_URL=https://api.cnb.cool/my-org/my-repo/-/ai-ide/v2
API_KEY=your_cnb_access_token
MODEL_ID=glm-5.0
```

优先级逻辑：
1. `BASE_URL` 存在 → 直接使用
2. `BASE_URL` 不存在 → 从 `CNB_API_ENDPOINT` + `CNB_REPO_SLUG` 拼接
3. `API_KEY` 存在 → 使用 `API_KEY`；否则使用 `CNB_TOKEN`

### 1.6 云端智能体自定义模型

如需在云端智能体（Happy CNB）中使用自建或第三方模型：

| 环境变量 | 说明 |
|----------|------|
| `CODEBUDDY_BASE_URL` | 模型服务的 API Base URL（兼容 OpenAI 协议） |
| `CODEBUDDY_API_KEY` | 调用该服务所需的 API Key |
| `CODEBUDDY_MODEL` | 模型名称（如 `gpt-4o`、`deepseek-chat`） |

> ⚠️ 三个变量需**同时配置**才会生效，否则回退到默认模型。

配置方式：`个人设置` → `云原生开发` → `环境变量` 中配置密钥仓库文件。

---

## 二、CNB 云原生预览功能

### 2.1 什么是云原生预览

云原生预览允许你在**云端开发环境**中运行 Web 服务，并通过公网 URL 直接预览效果。无需本地安装任何环境，浏览器即可查看。

### 2.2 两种预览方式

#### 方式一：WebIDE 端口映射

在 WebIDE 的 **PORTS 面板** 中添加端口映射，系统自动生成公网可访问的 URL。

**获取预览 URL 的方法：**

1. **PORTS 面板**：直接在 WebIDE 控制台查看
2. **环境变量**：读取 `CNB_VSCODE_PROXY_URI`，格式为：
   ```
   https://fjisdofi21-{{port}}.cnb.run
   ```
   将 `{{port}}` 替换为你的业务端口号。

**⚠️ 重要限制：** 服务必须监听在 `0.0.0.0`，监听 `localhost` 或 `127.0.0.1` 无法通过此方式访问。

#### 方式二：VSCode/Cursor 端口转发

通过 VSCode 或 Cursor 客户端的 **Port Forward** 功能，将远程端口转发到本地：

1. 通过 SSH 连接到云原生开发环境
2. 在 VSCode 的 PORTS 面板中添加转发端口
3. 本地浏览器访问 `http://localhost:<port>`

#### 对比

| 对比项 | 端口映射 | 端口转发 |
|--------|---------|---------|
| 工具 | WebIDE | VSCode/Cursor 客户端 |
| 访问方式 | 公网 URL | 本地 localhost |
| 监听要求 | 必须 `0.0.0.0` | 无限制 |
| 适用场景 | 分享预览链接、远程演示 | 本地开发调试 |

### 2.3 仅预览模式（Beta）

仅预览模式是一种轻量化方案——点击「云原生开发」按钮后**不打开 WebIDE**，而是直接启动服务并打开预览页面。

**核心特点：**
- 不加载 WebIDE，启动更快
- 业务服务必须监听在 **8686 端口**
- 适合纯展示/演示场景

---

## 三、将 Agent Web 应用部署为云原生预览

### 3.1 整体思路

将你的 Agent Web 应用（比如基于 Flask/FastAPI/Streamlit 的 AI 聊天应用）打包为 Docker 镜像，通过 CNB 的「仅预览模式」实现一键部署和预览。

**关键要求：** 应用必须监听 `0.0.0.0:8686` 端口。

### 3.2 步骤一：准备应用代码

以一个 FastAPI Agent 应用为例：

```python
# app.py
import os
import uvicorn
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()

# 在 CNB 环境中自动获取配置
endpoint = os.environ.get("CNB_API_ENDPOINT", "")
repo_slug = os.environ.get("CNB_REPO_SLUG", "")
base_url = os.environ.get("BASE_URL") or f"{endpoint}/{repo_slug}/-/ai-ide/v2"
api_key = os.environ.get("API_KEY") or os.environ.get("CNB_TOKEN", "")

client = OpenAI(base_url=base_url, api_key=api_key)

@app.post("/chat")
async def chat(message: dict):
    response = client.chat.completions.create(
        model=os.environ.get("MODEL_ID", "glm-5.0"),
        messages=[{"role": "user", "content": message["content"]}],
        stream=False,
    )
    return {"reply": response.choices[0].message.content}

if __name__ == "__main__":
    # 关键：监听 0.0.0.0:8686
    uvicorn.run(app, host="0.0.0.0", port=8686)
```

### 3.3 步骤二：编写 Dockerfile

```dockerfile
# .ide/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 安装 SSH（可选，支持客户端连接）
RUN apt-get update && apt-get install -y openssh-server && rm -rf /var/lib/apt/lists/*

# 指定字符集
ENV LANG=C.UTF-8
ENV LANGUAGE=C.UTF-8

# 暴露端口
EXPOSE 8686

CMD ["python", "app.py"]
```

### 3.4 步骤三：配置 .cnb.yml

```yaml
# .cnb.yml
$:
  vscode:
    - docker:
        build: .ide/Dockerfile
      services:
        - docker
        - name: vscode
          options:
            # 启用仅预览模式
            onlyPreview: true
            # 启动命令（服务必须监听 8686 端口）
            launch: python app.py
            # 离线保活 30 分钟
            keepAliveTimeout: 30m
            # 非守护进程模式，可以看到启动日志
            daemon: false
            # 备份用户数据
            backup: true
```

### 3.5 步骤四：推送并预览

1. 将代码推送到 CNB 仓库
2. 在仓库分支页面点击右上角「**云原生开发**」按钮
3. 系统自动构建镜像 → 启动服务 → 打开预览页面
4. 你的 Agent 应用即可通过公网 URL 访问

### 3.6 完整目录结构示例

```
my-agent-app/
├── .cnb.yml              # CNB 配置
├── .ide/
│   └── Dockerfile        # 开发环境镜像定义
├── app.py                # Agent Web 应用
├── requirements.txt      # Python 依赖
├── static/               # 前端静态文件（可选）
│   └── index.html
└── README.md
```

### 3.7 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `onlyPreview` | Boolean | `false` | 设为 `true` 启用仅预览模式 |
| `launch` | String | - | 启动业务服务的命令，**必须监听 8686** |
| `keepAliveTimeout` | String | `10m` | 离线保活时间（支持 `ms/s/m/h`） |
| `daemon` | Boolean | `false` | 是否后台运行 |
| `backup` | Boolean | `false` | 是否备份/恢复用户数据 |

### 3.8 注意事项

1. **端口必须是 8686** —— 仅预览模式硬编码了这个端口
2. **监听 `0.0.0.0`** —— 不要用 `127.0.0.1` 或 `localhost`
3. **仅预览模式不支持代理** —— `CNB_VSCODE_PROXY_URI` 在此模式下无效
4. **CNB_TOKEN 自动注入** —— 无需手动配置 API Key，应用可直接调用大模型
5. **该功能为 Beta** —— 配置方式未来可能变更

### 3.9 进阶：标准云原生开发模式

如果你需要同时开发和预览（而非纯展示），推荐使用标准云原生开发模式：

```yaml
# .cnb.yml
$:
  vscode:
    - docker:
        build: .ide/Dockerfile
      services:
        - vscode
        - docker
      stages:
        - name: install deps
          script: pip install -r requirements.txt
        - name: start server
          script: nohup python app.py &
```

然后在 WebIDE 的 PORTS 面板中手动添加 8686 端口映射即可预览。

---

## 参考链接

- [CNB 云原生开发介绍](https://docs.cnb.cool/zh/workspaces/intro.md)
- [业务端口预览](https://docs.cnb.cool/zh/workspaces/business-preview.md)
- [仅预览模式](https://docs.cnb.cool/zh/workspaces/only-preview.md)
- [自定义开发环境](https://docs.cnb.cool/zh/workspaces/custom-dev-env.md)
- [云端智能体 (Happy CNB)](https://docs.cnb.cool/zh/workspaces/web-agent.md)
- [默认环境变量](https://docs.cnb.cool/zh/build/build-in-env.md)
- [NPC 事件](https://docs.cnb.cool/zh/build/npc.md)
- [外部系统接入 NPC](https://docs.cnb.cool/zh/build/npc-integration.md)
