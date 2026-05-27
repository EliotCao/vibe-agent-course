"""Demo 30：整合 Walkthrough —— 把 6 个零件一步步组装起来。

本 demo 不走 main.py 的快捷路径，而是**手动实例化每个零件**，
让学生看到"组装过程"比"最终产物"更重要。

运行：python demo_30_integration_walkthrough.py
"""

import os
import sys

# 让 demo 能 import my_coding_agent 下的子模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "my_coding_agent"))

from llm import LLM, Message  # noqa: E402
from tools import build_registry  # noqa: E402
from context import ContextManager  # noqa: E402
from memory import Memory  # noqa: E402

# ====================================================================
# 第 1 步：实例化 LLM（Day1 的零件）
# ====================================================================
print("=" * 60)
print("第 1 步：实例化 LLM 客户端")
print("=" * 60)
llm = LLM()
resp = llm.chat(messages=[{"role": "user", "content": "说一句话证明你能工作"}])
print(f"LLM 回复: {resp.content}\n")

# ====================================================================
# 第 2 步：实例化 ToolRegistry（Day2+5 的零件）
# ====================================================================
print("=" * 60)
print("第 2 步：注册 6 个工具")
print("=" * 60)
workdir = os.path.dirname(os.path.abspath(__file__))
tools = build_registry(workdir=workdir)
print("已注册工具:")
print(tools.get_tools_description())
print()

# ====================================================================
# 第 3 步：实例化 ContextManager（Day4 的零件）
# ====================================================================
print("=" * 60)
print("第 3 步：ContextManager —— 30 条消息以上才压缩")
print("=" * 60)
ctx = ContextManager(keep_last=10, max_messages=30)
print(f"keep_last={ctx.keep_last}, max_messages={ctx.max_messages}")
print(f"当前 should_compress([1条]): {ctx.should_compress([{'role':'user','content':'hi'}])}")
print()

# ====================================================================
# 第 4 步：实例化 Memory（Day4 的零件）
# ====================================================================
print("=" * 60)
print("第 4 步：Memory —— 向量相似度检索")
print("=" * 60)
mem = Memory(min_score=0.5)
mem.add("用户喜欢用 pytest 写测试")
mem.add("项目使用 Python 3.12")
hits = mem.search("怎么跑测试", k=2)
print(f"查询 '怎么跑测试' 的结果: {[(round(s,3), e.text) for s, e in hits]}")
print()

# ====================================================================
# 第 5 步：手动跑一轮 Agent Loop —— 最核心的粘合逻辑
# ====================================================================
print("=" * 60)
print("第 5 步：手动跑一轮 Agent Loop（不用 CodingAgent 类）")
print("=" * 60)
messages = [
    {"role": "system", "content": f"你是 coding agent，工作目录: {workdir}"},
    {"role": "user", "content": "请列出当前目录下有哪些文件"},
]

for turn in range(1, 6):
    print(f"\n--- 轮次 {turn} ---")
    resp = llm.chat(messages=messages, tools=tools.to_schemas())
    if not resp.tool_calls:
        print(f"最终回答: {resp.content}")
        break
    # 有 tool_calls
    messages.append({
        "role": "assistant",
        "content": resp.content,
        "tool_calls": [tc.as_openai_dict() for tc in resp.tool_calls],
    })
    for tc in resp.tool_calls:
        import json
        args = json.loads(tc.arguments or "{}")
        print(f"  调用 {tc.name}({args})")
        result = tools.invoke(tc.name, args)
        print(f"  结果（前 100 字）: {result[:100]}")
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

print("\n\n✅ Walkthrough 完成！")
print("你看到了 6 个零件各自独立，Agent Loop 只是一层循环粘合。")
print("接下来用 CodingAgent 类就是把上面这些步骤封装起来。")
