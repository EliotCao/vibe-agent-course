"""
Demo 06 · Chatbot vs Agent：同一道题，循环不循环差别有多大
========================================================

配套：第 6 节《Agent vs Chatbot：为什么需要循环》

效果：让学生当堂看到——
  ① 朴素 Chatbot：单轮回答一个"需要外部信息 + 计算"的题，必然翻车
  ② 最小 Agent：同一道题，加一个 while 循环 + 工具，立刻能答对

故意做得很糙，只用一个 while 循环和两个最简单的工具，
让学生看清"Agent = LLM + Tools + Loop"这个等式具体是什么样子。

跑法：
    python demo_06_chatbot_vs_agent.py
"""

from __future__ import annotations

import json
import urllib.request

from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()

# ============================================================
# 同一道题：需要先抓网页拿到长度，再做除法
# ============================================================
QUESTION = "请帮我抓取 https://example.com 的网页内容，告诉我它有多少字节，并把这个字节数除以 7。"


# ============================================================
# 实验 ① · 朴素 Chatbot：一次性回答
# ============================================================
def naive_chatbot() -> None:
    print("=" * 60)
    print("【实验 ① · 朴素 Chatbot】")
    print("=" * 60)
    print(f"问题: {QUESTION}\n")

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": QUESTION}],
        max_tokens=400,
        temperature=0,
    )
    print("回答：")
    print(resp.choices[0].message.content)
    print()
    print("👆 注意观察：模型要么承认抓不到，要么编一个看起来很像的字节数。")


# ============================================================
# 实验 ② · 最小 Agent：while 循环 + 两个工具
# ============================================================
def fetch_url(url: str) -> str:
    """抓网页，返回长度信息（字节数）。"""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read()
        return f"成功抓取 {url}，body 长度 = {len(body)} 字节"
    except Exception as e:
        return f"抓取失败: {e}"


def calculator(expr: str) -> str:
    """安全计算一个表达式（只允许数字和基本运算符）。"""
    allowed = set("0123456789+-*/(). ")
    if not set(expr) <= allowed:
        return f"非法表达式: {expr}"
    try:
        return f"{expr} = {eval(expr)}"  # noqa: S307 demo 简化
    except Exception as e:
        return f"计算失败: {e}"


# 极简"工具表"：name -> (函数, 说明)
TOOLS = {
    "fetch_url": (fetch_url, "抓取一个 URL，返回其内容长度（参数: url）"),
    "calculator": (calculator, "计算一个数学表达式（参数: expr）"),
}


def tools_description() -> str:
    return "\n".join(f"- {name}({desc})" for name, (_, desc) in TOOLS.items())


SYSTEM_PROMPT = f"""你是一个会用工具的助手。

可用工具：
{tools_description()}

每次需要调工具时，**只输出一行 JSON**，格式：
  {{"tool": "工具名", "args": {{"参数名": "参数值"}}}}

如果你已经能直接回答用户问题（不需要再调工具），输出：
  {{"final": "你的最终回答"}}

不要输出任何 JSON 以外的文字。
"""


def parse_step(text: str):
    """从模型输出里抠出 JSON。容错：模型可能多写一点，取第一个 {...} 段。"""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"看不到 JSON: {text!r}")
    return json.loads(text[start : end + 1])


def mini_agent() -> None:
    print("\n\n" + "=" * 60)
    print("【实验 ② · 最小 Agent Loop】")
    print("=" * 60)
    print(f"问题: {QUESTION}\n")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": QUESTION},
    ]

    for turn in range(1, 6):  # 最多 5 轮，防止跑飞
        print(f"--- 第 {turn} 轮 ---")
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0,
        )
        raw = resp.choices[0].message.content
        print(f"模型输出: {raw}")

        step = parse_step(raw)

        # ① 模型给出最终答案
        if "final" in step:
            print(f"\n🎯 最终答案: {step['final']}")
            return

        # ② 模型要调工具
        tool_name = step["tool"]
        args = step.get("args", {})
        if tool_name not in TOOLS:
            obs = f"未知工具: {tool_name}"
        else:
            func, _ = TOOLS[tool_name]
            obs = func(**args)
        print(f"工具结果: {obs}\n")

        # 把"工具调用"和"工具结果"都拼回 messages，让模型看到下一步
        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {"role": "user", "content": f"上一步工具的结果：{obs}\n请继续。"}
        )

    print("⚠️ 达到最大轮次，仍未给出最终答案。")


if __name__ == "__main__":
    naive_chatbot()
    mini_agent()

    print("\n\n" + "=" * 60)
    print("🎯 关键观察")
    print()
    print("  Chatbot:  LLM(prompt) -> 一段话")
    print("            没法做 LLM 能力之外的事，遇到外部信息就编")
    print()
    print("  Agent:    while True:")
    print("              输出 = LLM(messages)")
    print("              if 输出说要调工具:")
    print("                  跑工具 -> 把结果拼回 messages")
    print("              else: break")
    print("            就这十行循环，让 LLM 有了'手脚'")
    print()
    print("  下一步：Day2 后面几节会把这个循环做得更工程化——")
    print("    07. 用 OpenAI 官方 tool_calls 协议替代手写 JSON")
    print("    08. 用 ToolRegistry 自动从函数生成 schema")
    print("    09. 把循环的边界条件、错误处理写规范")
    print("=" * 60)
