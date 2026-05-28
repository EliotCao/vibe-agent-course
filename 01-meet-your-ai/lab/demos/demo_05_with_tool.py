"""
Demo 05 · LLM + 外部支持：从"不知道"到"知道"
=============================================

配套：第 5 节《LLM 智能 + 外部支持：为什么需要工具与上下文》

效果：同一个问题，分两次问：
  ① 纯 LLM    →   答错或编造
  ② 给一个简单工具  →  答对

直观感受"为什么需要 Day2 的工具系统"。

跑法：
    python demo_05_with_tool.py
"""

from __future__ import annotations

import datetime

from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


# ---------- 一个"工具"：返回当前时间 ----------
def get_current_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------- 一个"工具"：查文件内容（mock 一个 LLM 不知道的事实） ----------
SECRET_FILE = """\
[内部公告]
项目交付截止时间：2026-06-30 23:59:59
联系人：王经理
紧急联系电话：13800138000
"""

def read_internal_doc() -> str:
    return SECRET_FILE


# ---------- 实验 1：当前时间 ----------
def exp_current_time() -> None:
    print("=" * 60)
    print("【实验 1：现在几点了？】")
    print("=" * 60)

    question = "现在是北京时间几点几分？请精确到分钟。"

    print("\n--- ① 纯 LLM 回答 ---")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=100,
        temperature=0,
    )
    print(resp.choices[0].message.content)

    print("\n--- ② 把工具结果塞进 prompt 再问 ---")
    now = get_current_time()
    enriched = f"""\
我现在要回答用户的问题。我有一个外部工具的结果可以用：
- 工具：get_current_time()
- 结果：{now}

用户问题：{question}

请基于工具结果回答。
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": enriched}],
        max_tokens=100,
        temperature=0,
    )
    print(resp.choices[0].message.content)

    print("\n💡 看：仅仅是把'工具结果'拼进 prompt，模型立刻能答对了。")


# ---------- 实验 2：内部知识 ----------
def exp_internal_knowledge() -> None:
    print("\n\n" + "=" * 60)
    print("【实验 2：项目截止时间是什么时候？】")
    print("=" * 60)

    question = "Hello-Agents 项目的交付截止时间是什么时候？联系人电话多少？"

    print("\n--- ① 纯 LLM 回答 ---")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=200,
        temperature=0,
    )
    print(resp.choices[0].message.content)
    print("👆 模型不可能知道，要么承认不知道，要么编一个。")

    print("\n--- ② 把'内部文档'塞进 prompt ---")
    enriched = f"""\
请基于下面提供的内部文档回答用户问题。

【内部文档】
{read_internal_doc()}

【用户问题】
{question}
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": enriched}],
        max_tokens=200,
        temperature=0,
    )
    print(resp.choices[0].message.content)

    print("\n💡 看：把'外部知识'喂进去，模型立刻能精准回答。")
    print("   这就是 RAG（Retrieval-Augmented Generation）的最朴素版本。")


if __name__ == "__main__":
    exp_current_time()
    exp_internal_knowledge()

    print("\n\n" + "=" * 60)
    print("🎯 今天的关键认识：")
    print()
    print("  LLM 本身 = 一个基于训练数据的'静态'函数")
    print("            → 不知实时、不知私域、不知工具结果")
    print()
    print("  LLM + 上下文 + 工具 = Agent")
    print("            → 可以查实时、可以读私域、可以执行动作")
    print()
    print("  今天的 demo 把'工具结果'手动拼进 prompt 就能起作用。")
    print("  Day2 会把这个过程自动化：让 LLM 自己决定调哪个工具。")
    print("=" * 60)
