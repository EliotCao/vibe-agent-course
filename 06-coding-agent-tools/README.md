# 第 5 章 · Coding Agent 工具集

> 本章目标：实现 Coding Agent 的 5 个核心工具。
> 产出：`my-agent/coding_tools/` — read / write / edit / list_dir / bash。

## 你将学到

- Coding Agent 的 5 阶段工作流（理解 → 定位 → 修改 → 验证 → 汇报）
- 工具设计哲学：唯一性约束、安全闸门、友好报错
- 每个工具的实现要点

## 内容结构

| 节 | 内容 | 讲义 | Demo |
|----|------|------|------|
| 24 | Coding Agent 工作流 | [24-coding-agent-workflow.md](./lecture/24-coding-agent-workflow.md) | `demo_24_five_stages.py` |
| 25 | 工具设计哲学 | [25-tool-design.md](./lecture/25-tool-design.md) | `demo_25_design_philosophy.py` |
| — | 端到端演示 | — | `demo_26_end_to_end.py` |

## 运行 Demo

```bash
cd 06-coding-agent-tools/lab
python demo_24_five_stages.py
python demo_25_design_philosophy.py
python demo_26_end_to_end.py
```

## 本章产出

补全 [`my-agent/coding_tools/`](../my-agent/coding_tools/) 下的 5 个工具文件，让测试通过：

```bash
cd my-agent
python tests/test_coding_tools.py
```

## 配套练习

[`exercises/06-coding-agent-tools/`](../exercises/06-coding-agent-tools/) — 3 道代码填空题
