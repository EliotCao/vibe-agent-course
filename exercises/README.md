# 练习题

> 所有练习都是代码填空题。补全 `TODO` 部分，运行脚本看到 `✅ PASSED` 即为完成。

## 目录

| 章节 | 目录 | 题目 |
|-----|------|------|
| 1 | （无填空题）| VibeCoding 入门：动手 vibe 一个游戏，见 [`01-vibecoding-intro/lab`](../01-vibecoding-intro/lab/) |
| 2 | [02-meet-your-ai](./02-meet-your-ai/) | Token 计数 · System Prompt · 幻觉检测 · 流式输出 |
| 3 | [03-tools-and-agent-loop](./03-tools-and-agent-loop/) | Function Calling 消息流 · ToolRegistry · Agent Loop |
| 4 | [04-agent-patterns](./04-agent-patterns/) | ReAct 解析 · Plan-and-Solve · Reflection 循环 |
| 5 | [05-context-and-memory](./05-context-and-memory/) | 上下文压缩 · 向量记忆 · 压缩决策器 |
| 6 | [06-coding-agent-tools](./06-coding-agent-tools/) | read_file · write_file · bash 安全闸门 |
| 7 | [07-coding-agent-integration](./07-coding-agent-integration/) | 整合（待更新） |
| 8 | [08-skills-and-npc](./08-skills-and-npc/) | Skills + NPC + 大作业（待更新） |

## 运行方式

```bash
# 确保在项目根目录激活了环境
cd exercises/02-meet-your-ai
python ex_1_1.py
```

## CI 验证

每个脚本退出码 0 = 通过，非 0 = 失败。可直接用于自动化测试：

```bash
for f in exercises/*/ex_*.py; do
    python "$f" || echo "FAILED: $f"
done
```
