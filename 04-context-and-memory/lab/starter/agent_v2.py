"""
Day 4 Lab Part 3 · Agent v2 骨架 —— 学生填空

把 Day3 的 Agent 升级成 v2：接上 ContextManager + Memory。

参考：第 19/20 节 + demos/demo_21_agent_v2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from _env import get_model_id, make_client

# 复用你 Part1 / Part2 写的两个类
sys.path.insert(0, str(Path(__file__).parent))
from context_manager import ContextManager
from memory import Memory


class AgentV2:
    def __init__(
        self,
        system_prompt: str = "你是一个有用的助手。",
        memory: Memory | None = None,
        ctx: ContextManager | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.memory = memory or Memory()
        self.ctx = ctx or ContextManager()
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]

    # ----------------------------------------------------------------
    # TODO ① 每轮对话主流程
    # 步骤：
    #   1. 用 user_input 去 self.memory.search(k=3) 召回相关事实
    #   2. 如果有相似度 > 0.5 的事实，构造一个临时 system 消息插在前面
    #   3. 把当前 user_input 加进 messages
    #   4. 如果 self.ctx.should_compress() 返回 True，调用 self.ctx.compress() 压缩
    #   5. 调 LLM，拿到 reply
    #   6. 把 user_input 和 reply 写回 self.messages
    #   7. 返回 reply
    # ----------------------------------------------------------------
    def chat(self, user_input: str) -> str:
        client = make_client()
        # ← 你的代码（约 20 行）
        return "TODO"

    # ----------------------------------------------------------------
    # TODO ② 提炼记忆（对话结束后调用一次）
    # 用 LLM 从 self.messages 里提炼"值得长期记的事实"，写进 self.memory
    # 提示：让 LLM 输出每行一条事实，循环 self.memory.add(line)
    # ----------------------------------------------------------------
    def distill_to_memory(self) -> list[str]:
        return []  # ← 你的代码


# ============================================================
# 自测：跑一个 12 轮对话，观察 token 消耗与压缩触发情况
# ============================================================
if __name__ == "__main__":
    agent = AgentV2(system_prompt="你是旅行规划师，回答简洁。")

    # 预先存两条用户硬约束
    agent.memory.add("用户对花粉过敏，户外活动避开花期。")
    agent.memory.add("用户每日预算 500 元。")

    questions = [
        "我准备 6 月去北京玩 7 天。",
        "第 1 天有什么推荐？",
        "第 2 天呢？",
        "第 3 天去户外好不好？",   # 应该触发"过敏"召回
        "第 4 天就在城里逛吧。",
        "总结一下整体预算。",     # 应该触发"预算"召回
        "再给我推荐 2 个咖啡馆。",
        "总结所有 7 天行程。",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n--- 第 {i} 轮 ---")
        print(f"用户: {q}")
        reply = agent.chat(q)
        print(f"助手: {reply[:150]}")

    print("\n📝 提炼记忆 → Memory")
    new_facts = agent.distill_to_memory()
    for f in new_facts:
        print(f"  + {f}")
