"""
Demo 21 · Agent v2：Day3 的 Agent 接上 ContextManager + Memory
==============================================================

把 Day2 / Day3 的最小 Agent Loop 升级成 v2：
  ① 每轮调 LLM 前，用 ContextManager 把 messages 压缩到合理长度
  ② 把 Memory 召回的相关长期事实注入到 system
  ③ 对话结束时，用 LLM 提炼"值得记住的事实"写进 Memory

跑一个 30 轮的真实任务，对比：
  - Day3 朴素 Agent vs Day4 v2 Agent 的 token 消耗
  - 关键事实（早期透露的过敏 / 预算）有没有保住

跑法：
    python demo_21_agent_v2.py
"""

from __future__ import annotations

import json

import numpy as np

from _env import get_model_id, make_client
from demo_19_context_strategies import (
    extract_key_facts,
    strategy_hierarchical,
)
from demo_20_memory import Memory


# ============================================================
# ContextManager：把 demo_19 的策略包成一个类
# ============================================================
class ContextManager:
    """简易 ContextManager：分层策略 + 关键事实注入。

    策略：
      - 永远保留 system
      - 关键事实（用户硬约束）单独抽出来，前置注入
      - 早期对话用 LLM 摘要
      - 最近 N 轮保留原文
    """

    def __init__(self, keep_last: int = 6, max_messages: int = 20):
        self.keep_last = keep_last
        self.max_messages = max_messages

    def should_compress(self, messages: list[dict]) -> bool:
        return len(messages) > self.max_messages

    def compress(self, messages: list[dict]) -> list[dict]:
        return strategy_hierarchical(messages, keep_last=self.keep_last)


# ============================================================
# Memory 提炼：用 LLM 从对话里提炼"值得长期记的事实"
# ============================================================
DISTILL_PROMPT = """阅读下面的对话，提炼出**值得长期记住的用户偏好、约束、关键事实**，
每条一行，不要把一次性的问答内容也存进去。
如果没有可记的事实，输出空。

对话：
{transcript}

# 输出格式
每行一条事实，纯文本，无序号
"""


def distill_to_memory(messages: list[dict], memory: Memory) -> list[str]:
    """从对话中提炼事实写入 Memory，返回新增的事实列表。"""
    client = make_client()
    transcript = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages if m["role"] != "system"
    )
    resp = client.chat.completions.create(
        model=get_model_id(),
        messages=[
            {"role": "user", "content": DISTILL_PROMPT.format(transcript=transcript)}
        ],
        temperature=0,
        max_tokens=300,
    )
    raw = resp.choices[0].message.content or ""
    facts = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]
    for f in facts:
        memory.add(f)
    return facts


# ============================================================
# Agent v2：组合 ContextManager + Memory
# ============================================================
class AgentV2:
    def __init__(
        self,
        system_prompt: str = "你是一个有用的助手。",
        memory: Memory | None = None,
        ctx_manager: ContextManager | None = None,
    ):
        self.system_prompt = system_prompt
        self.memory = memory or Memory()
        self.ctx = ctx_manager or ContextManager()
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]

    def chat(self, user_input: str) -> str:
        client = make_client()

        # 1. 用 user_input 去 Memory 召回相关长期事实
        relevant = self.memory.search(user_input, k=3) if self.memory.entries else []
        if relevant:
            facts_block = "\n".join(f"- {e.text}" for _, e in relevant if _ > 0.5)
            if facts_block:
                # 临时插入一条 system，仅本轮使用
                injected = [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "system", "content": f"[相关长期事实]\n{facts_block}"},
                ] + [m for m in self.messages if m["role"] != "system"]
            else:
                injected = self.messages
        else:
            injected = self.messages

        # 2. 加上当前用户输入
        injected = injected + [{"role": "user", "content": user_input}]

        # 3. 检查是否需要压缩
        if self.ctx.should_compress(injected):
            print(f"  ⚙️  消息超过 {self.ctx.max_messages} 条，触发压缩")
            injected = self.ctx.compress(injected)

        # 4. 调 LLM
        resp = client.chat.completions.create(
            model=get_model_id(),
            messages=injected,
            temperature=0.3,
            max_tokens=400,
        )
        reply = resp.choices[0].message.content or ""
        usage = resp.usage

        # 5. 写回 messages（不含临时注入的那一条）
        self.messages.append({"role": "user", "content": user_input})
        self.messages.append({"role": "assistant", "content": reply})

        return reply, usage.prompt_tokens, usage.total_tokens


# ============================================================
# 跑一个 12 轮对话，把 Day1 vs Day4 的 token 消耗对比一下
# ============================================================
def run_comparison() -> None:
    print("=" * 60)
    print("【对比测试】30 轮对话 v2 Agent 各轮 token 消耗")
    print("=" * 60)

    agent = AgentV2(
        system_prompt="你是旅行规划师。回答简洁、可执行。",
    )

    # 第 1 轮先存 2 个用户硬约束（模拟用户告诉过 Agent 的事）
    agent.memory.add("用户对花粉过敏，户外活动避开花期。")
    agent.memory.add("用户每日预算 500 元。")

    questions = [
        "我准备 6 月去北京玩 7 天。",
        "第 1 天有什么推荐？",
        "第 2 天呢？",
        "第 3 天去户外好不好？",  # ⭐ 应该触发"过敏"事实召回
        "第 4 天就在城里逛吧。",
        "第 5 天有没有什么文化体验？",
        "第 6 天我想体验下夜景。",
        "总结一下整体预算。",  # ⭐ 应该触发"预算"事实召回
        "改一下，第 3 天换室内景点。",
        "再给我推荐 2 个咖啡馆。",
        "夜场票好买吗？",
        "总结所有 7 天的行程，按天列出。",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n--- 第 {i} 轮 ---")
        print(f"用户: {q}")
        reply, prompt_tk, total_tk = agent.chat(q)
        print(f"助手: {reply[:150]}{'...' if len(reply) > 150 else ''}")
        print(f"      [prompt={prompt_tk} total={total_tk} messages={len(agent.messages)}]")

    print("\n\n" + "=" * 60)
    print("📝 对话结束，提炼记忆 → Memory")
    print("=" * 60)
    new_facts = distill_to_memory(agent.messages, agent.memory)
    print("新增长期事实：")
    for f in new_facts:
        print(f"  - {f}")

    print(f"\n💾 Memory 现在有 {len(agent.memory.entries)} 条事实，")
    print("   下次会话时这些事实会自动召回，跨会话也'记得'用户。")


if __name__ == "__main__":
    run_comparison()

    print("\n\n" + "=" * 60)
    print("🎯 v2 Agent 跟 Day3 朴素版的区别")
    print("=" * 60)
    print("  ① ContextManager：messages 超过阈值时主动压缩（截断/摘要/分层）")
    print("  ② Memory 召回：每轮用 user_input 检索相关长期事实，注入到 system")
    print("  ③ Memory 提炼：对话结束时用 LLM 提炼新事实，写回 Memory")
    print()
    print("  这三件事加在一起，让你的 Agent 第一次有了'跨会话的记忆'。")
    print("  下一步（Day5/6）要做的：把这些组件接进真实的 Coding Agent。")
