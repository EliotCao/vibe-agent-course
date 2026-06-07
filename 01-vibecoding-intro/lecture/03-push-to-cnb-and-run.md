# 第 03 节 · 推到 CNB，用云原生开发环境跑起来

> 目标：把上一节 vibe 出来的游戏推送到 CNB 仓库，并用**云原生开发环境**一键运行，
> 拿到一个能分享给别人的预览链接。

## 一、为什么要推到 CNB

本地跑只有你自己能玩。推到 CNB 后：

- 代码有了**云端备份**和版本历史
- 用**云原生开发环境**，不用在本地配环境，浏览器即可写代码、运行
- Web 项目可以拿到**公网预览链接**，发给同学/老师直接体验
- 后面几章的 NPC、流水线都依赖这个仓库

## 二、第一步：把代码推到 CNB

### 2.1 新建仓库

在 CNB 上新建一个仓库（比如 `my-first-game`）。

### 2.2 推送本地代码

在你的游戏目录里：

```bash
git init
git add .
git commit -m "我的第一个 vibe 游戏"
git remote add origin https://cnb.cool/你的组织/my-first-game.git
git push -u origin main
```

> 不熟悉 git？可以直接让 AI 帮你：把上面的需求贴给它，
> "帮我把当前目录的代码推送到这个 CNB 仓库地址：……"，它会一步步带你做。

## 三、第二步：用云原生开发环境跑起来

云原生开发（Cloud Native Development）让你**无需本地环境**，在云端直接运行项目。

### 3.1 进入云原生开发

在 CNB 仓库页面，点击右上角的「**云原生开发**」按钮，系统会自动拉起一个云端 VSCode（WebIDE）。

### 3.2 在云端运行你的游戏

打开云端 VSCode 的终端，直接运行：

```bash
python demo_01_guess_game.py
```

命令行游戏在终端里就能玩。如果你 vibe 的是一个 **Web 游戏**（比如用 HTML/JS 或 Flask 写的），就需要下面的预览功能。

## 四、进阶：Web 游戏的在线预览

如果你的游戏是网页版（监听某个端口），可以通过 CNB 拿到公网预览链接。

### 4.1 关键要求

- 服务必须监听 **`0.0.0.0`**，不能用 `127.0.0.1` 或 `localhost`
- 否则公网无法访问

```python
# 以一个简单的 Flask 网页游戏为例
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>我的网页游戏</h1>"

if __name__ == "__main__":
    # 关键：host 必须是 0.0.0.0
    app.run(host="0.0.0.0", port=8080)
```

### 4.2 拿到预览链接

启动服务后，在 WebIDE 的 **PORTS 面板**里添加你的端口（如 8080），
系统会自动生成一个公网 URL，点开就能玩，也能把链接发给别人。

## 五、一键预览模式（可选）

如果你只想**展示**而不需要在线改代码，可以用「仅预览模式」：

1. 在仓库根目录加一个 `.cnb.yml`
2. 让服务监听 **8686 端口**（仅预览模式固定用这个端口）
3. 推送后点「云原生开发」，系统直接启动服务并打开预览页

```yaml
# .cnb.yml —— 仅预览模式示例
$:
  vscode:
    - docker:
        image: python:3.11-slim
      services:
        - name: vscode
          options:
            onlyPreview: true        # 启用仅预览
            launch: python app.py    # 启动命令（须监听 8686）
            keepAliveTimeout: 30m
```

> 这块配置看不懂没关系，直接让 AI 帮你生成。后面第 8 章会专门讲 `.cnb.yml`。

## 六、本节小结

```
本地 vibe 出游戏
      ↓  git push
推到 CNB 仓库（云端备份 + 版本管理）
      ↓  点「云原生开发」
云端 VSCode 里运行（无需本地环境）
      ↓  端口映射 / 仅预览模式
拿到公网链接，谁都能玩 🎉
```

## 七、参考链接

- [CNB 云原生开发介绍](https://docs.cnb.cool/zh/workspaces/intro.md)
- [业务端口预览](https://docs.cnb.cool/zh/workspaces/business-preview.md)
- [仅预览模式](https://docs.cnb.cool/zh/workspaces/only-preview.md)

---

恭喜！你已经完整走过了"想法 → vibe → 上线"的全流程。
从下一章开始，我们回头揭开 AI 的面纱：**它到底是怎么听懂你、写出代码的？**
进入 [第 2 章 · 认识你的 AI](../../02-meet-your-ai/)。
