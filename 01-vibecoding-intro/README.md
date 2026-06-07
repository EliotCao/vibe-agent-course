# 第 1 章 · VibeCoding 入门：先玩起来

> 本章目标：不讲原理、先上手。用 AI 把一个能玩的小游戏"vibe"出来，亲手体验"动嘴写代码"的爽感；
> 然后把代码推到 CNB，用云原生开发环境一键跑起来——让你的成果立刻能在浏览器里被别人玩到。
> 产出：一个你自己 vibe 出来的小游戏 + 跑在 CNB 云原生环境里的在线 Demo。

## 你将学到

- VibeCoding 是什么：用自然语言驱动 AI 写代码的新姿势
- 怎么跟 AI 协作：从一句话需求到能跑的程序
- 如何把本地 vibe 出来的代码推送到 CNB 仓库
- 如何用 CNB 云原生开发环境把项目跑起来 / 在线预览

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 01 | 什么是 VibeCoding | [01-what-is-vibecoding.md](./lecture/01-what-is-vibecoding.md) | — |
| 02 | 动手：vibe 一个小游戏 | [02-vibe-a-game.md](./lecture/02-vibe-a-game.md) | `demo_01_guess_game.py` |
| 03 | 推到 CNB + 云原生跑起来 | [03-push-to-cnb-and-run.md](./lecture/03-push-to-cnb-and-run.md) | — |

## 运行 Demo

```bash
cd 01-vibecoding-intro/lab
python demo_01_guess_game.py
```

## 本章产出

1. 用 AI vibe 出一个能玩的小游戏（猜数字 / 贪吃蛇 / 2048 任选）
2. 把代码推送到你的 CNB 仓库
3. 用 CNB 云原生开发环境把它跑起来，拿到一个能分享的预览链接

## 为什么把这一章放在最前面

先体验"我也能造出东西"的成就感，再回头学背后的原理（LLM、Agent、工具……），
学习动力会完全不一样。这一章不需要任何前置知识，跟着做就行。

## 衔接

玩爽了之后，你一定会好奇：AI 到底是怎么"听懂"我的话并写出代码的？
带着这个问题进入 [第 2 章 · 认识你的 AI](../02-meet-your-ai/)。
