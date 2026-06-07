# 第 1 章 · 实操：vibe 出你的第一个游戏

> 不需要 API Key，不需要配环境。这一章的 demo 是一个纯标准库的小游戏，直接就能跑。

## demo 一览

```
lab/
└── demo_01_guess_game.py   # "vibe 完"的猜数字游戏（参考实现）
```

## 怎么玩

```bash
cd 01-vibecoding-intro/lab
python demo_01_guess_game.py
```

随机生成 1-100 的数字，你有 7 次机会，每次告诉你"太大/太小"，猜中给评价。

## 本章任务

1. **先跑参考实现**：感受一个 vibe 完的成品长什么样
2. **再自己 vibe 一遍**：打开你的 AI 编程工具，从空文件开始，
   按 [02-vibe-a-game.md](../lecture/02-vibe-a-game.md) 的流程，让 AI 帮你写一个游戏
   （可以是猜数字，也可以挑战贪吃蛇 / 2048）
3. **推到 CNB 跑起来**：按 [03-push-to-cnb-and-run.md](../lecture/03-push-to-cnb-and-run.md)，
   把你的游戏推到 CNB，用云原生开发环境运行

## 提交清单

```
01-checkpoint/
├── game.py          # 你自己 vibe 出来的游戏
├── screenshot.png   # 跑起来的截图（本地或 CNB 云原生环境）
└── reflection.md    # 100 字：vibe 过程中 AI 哪里帮了你，哪里得你自己来
```

> 重点不是游戏多复杂，而是你**完整走通了"想法 → vibe → 运行"**这条路。
