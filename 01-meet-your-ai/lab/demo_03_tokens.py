"""
Demo 03 · Token 计算与上下文窗口
================================

配套：第 3 节《Token、上下文窗口、token 怎么算》

效果：
  1) 直观展示任意文本被切成什么样的 token（中英文对比）
  2) 估算一段代码 / 文档值多少 token、多少钱
  3) 故意构造一个超出窗口的输入，看 API 报错（体感"窗口"是真实约束）

跑法：
    pip install tiktoken
    python demo_03_tokens.py
"""

from __future__ import annotations

import tiktoken

from _env import get_model_id, make_client, chat as llm_chat

# tiktoken 支持的编码器；不同模型用不同 BPE，cl100k_base 适用于 GPT-3.5/4
ENC = tiktoken.get_encoding("cl100k_base")

client = make_client()
MODEL = get_model_id()


def show_tokens(text: str, label: str = "") -> None:
    ids = ENC.encode(text)
    pieces = [ENC.decode([i]) for i in ids]

    print(f"\n[{label}]")
    print(f"原文 ({len(text)} 字符): {text}")
    print(f"切分成 {len(ids)} 个 token：")
    print("  " + " | ".join(repr(p) for p in pieces))


def estimate_cost(token_count: int, price_per_1m: float = 5.0) -> float:
    """假设 1M token = ¥5（你可以换成实际价格）"""
    return token_count / 1_000_000 * price_per_1m


def trigger_context_overflow() -> None:
    """构造一个超长输入，看 API 怎么反应"""
    # 默认窗口算 32K token，发 100K 必爆
    huge = "你好。" * 100_000_0
    print(f"\n构造超长输入：{len(huge)} 字符 ≈ {len(ENC.encode(huge)):,} token")
    print("尝试调用 API ...")
    try:
        msg = llm_chat(
            [{"role": "user", "content": huge}],
            temperature=0,
        )
        print(f"✅ 居然没爆？模型可能有超长窗口。回答：{msg.content}")
    except Exception as e:
        print(f"❌ 报错（这就是上下文窗口的物理限制）：")
        print(f"   {type(e).__name__}: {str(e)[:200]}")


if __name__ == "__main__":
    print("=" * 60)
    print("【实验 1】英文 vs 中文 vs 代码：tokenization 大不同")
    print("=" * 60)
    show_tokens("Hello, world!", "英文短句")
    show_tokens("你好，世界！", "中文短句")
    show_tokens("def foo(x): return x + 1", "Python 代码")
    show_tokens("こんにちは", "日文")
    show_tokens("🤖 AI", "emoji")

    print("\n" + "=" * 60)
    print("【实验 2】估算成本：以一份 README 为例")
    print("=" * 60)
    sample_doc = """
# Hello Agents 项目

一个循序渐进的 AI Agent 入门项目。每一章都是一个独立可运行的 Python 项目，
聚焦一个核心概念。从 LLM 流式调用，到 ReAct 范式，到工具系统、记忆系统、
上下文管理，最后做一个完整的 Coding Agent，并挂到云端做成 NPC。
""" * 10
    n = len(ENC.encode(sample_doc))
    print(f"文档长度: {len(sample_doc)} 字符 → {n} token")
    print(f"按 ¥5/1M token 计算：单次输入约 ¥{estimate_cost(n):.4f}")
    print(f"  跑 1000 次：¥{estimate_cost(n) * 1000:.2f}")
    print(f"  跑 10 万次：¥{estimate_cost(n) * 100_000:.2f}")

    print("\n" + "=" * 60)
    print("【实验 3】故意撑爆上下文窗口")
    print("=" * 60)
    trigger_context_overflow()

    print("\n" + "=" * 60)
    print("👀 观察：")
    print("  - 中文 1 字 ≈ 1-2 token，英文 1 词 ≈ 1.3 token")
    print("  - 代码里的标点 / 缩进单独成 token，所以代码很贵")
    print("  - 上下文窗口是物理硬约束，不能突破，只能管理")
    print("    （这是 第4章 上下文工程的伏笔）")
    print("=" * 60)
