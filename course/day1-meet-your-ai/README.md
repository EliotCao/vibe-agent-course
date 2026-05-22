# Day 1 · 认识你的 AI

> 今天结束时，每个学生能用 Python 流式对话，会估 token，知道幻觉为什么会出现，理解为什么 LLM 需要外部工具补强。

## 学习目标

- [ ] 能用一句话说清"LLM 为什么具备智能"（不是死记硬背的"概率模型"）
- [ ] 区分 system / user / assistant 三种角色的作用
- [ ] 知道 token 是什么，会估算文本的 token 数
- [ ] 能复现一次"诱发幻觉"的对话，并解释为什么会这样
- [ ] 能解释为什么需要给 LLM 配工具与上下文
- [ ] 能写出一个流式对话脚本

## 时间表（210 min）

| 节 | 时长 | 类型 | 内容 | 讲义 |
|----|------|------|------|------|
| 1 | 30min | 理论 | LLM 为什么具备智能：从概率预测到涌现 | [01-why-llm-is-smart.md](./lecture/01-why-llm-is-smart.md) |
| 2 | 30min | 理论 | 提示词与角色：System / User / Assistant | [02-prompts-and-roles.md](./lecture/02-prompts-and-roles.md) |
| 3 | 30min | 理论 | Token、上下文窗口、token 怎么算 | [03-tokens-and-context.md](./lecture/03-tokens-and-context.md) |
| 4 | 20min | 理论 | 大模型幻觉：从哪来、怎么识别、怎么缓解 | [04-hallucination.md](./lecture/04-hallucination.md) |
| 5 | 20min | 理论 | LLM 智能 + 外部支持：为什么需要工具与上下文 | [05-llm-needs-augmentation.md](./lecture/05-llm-needs-augmentation.md) |
| 6 | 80min | 实操 | 调用 LLM API + 流式输出 + token 计数 | [lab](./lab/README.md) |

## 当日产物

- `day1_llm.py` —— 流式对话脚本
- `count_tokens.py` —— token 计数小工具
- `hallucination_log.md` —— 一次主动诱发幻觉的对话记录

## Checkpoint

学生需提交：
1. 三个产物文件
2. 一次"用同一 prompt 测两个不同模型"的对比截图
3. 100-200 字反思

## 教师演示备用

- `ch02-hello-llm/main.py` —— 流式调用参考实现
- `ch04-my-agent/llm/llm.py` —— 工程级 LLM 客户端
