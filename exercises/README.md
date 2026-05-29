# 练习题

> 所有练习都是代码填空题。补全 `TODO` 部分，运行脚本看到 `✅ PASSED` 即为完成。

## 目录

| 章节 | 目录 | 题目 |
|-----|------|------|
| 1 | [01-meet-your-ai](./01-meet-your-ai/) | Token 计数 · System Prompt · 幻觉检测 · 流式输出 |
| 2 | [02-tools-and-agent-loop](./02-tools-and-agent-loop/) | Function Calling 消息流 · ToolRegistry · Agent Loop |
| 3 | [03-agent-patterns](./03-agent-patterns/) | ReAct 解析 · Plan-and-Solve · Reflection 循环 |
| 4 | [04-context-and-memory](./04-context-and-memory/) | 上下文压缩 · 向量记忆 · 压缩决策器 |
| 5 | [05-coding-agent-tools](./05-coding-agent-tools/) | read_file · write_file · bash 安全闸门 |
| 6 | [06-coding-agent-integration](./06-coding-agent-integration/) | 整合（待更新） |
| 7 | [07-skills-and-npc](./07-skills-and-npc/) | Skills + NPC（待更新） |
| 8 | [08-recap-and-final](./08-recap-and-final/) | 结课大作业 |

## 运行方式

```bash
# 确保在项目根目录激活了环境
cd exercises/01-meet-your-ai
python ex_1_1.py
```

## CI 验证

每个脚本退出码 0 = 通过，非 0 = 失败。可直接用于自动化测试：

```bash
for f in exercises/*/ex_*.py; do
    python "$f" || echo "FAILED: $f"
done
```
