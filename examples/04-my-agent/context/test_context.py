"""
测试上下文构建器。

运行方式：

source .venv/bin/activate
cd examples/04-my-agent
python context/test_context.py
"""

import sys
from pathlib import Path

# 把 04-my-agent/ 加进 sys.path，让 from llm import LLM 能命中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from llm import LLM
from context.context_builder import ContextBuilder, Source


def main():
    llm = LLM()

    builder = ContextBuilder(
        system_prompt="你是一个 Python 编程专家，擅长解释技术概念。"
    )

    # 添加背景信息
    builder.add(
        "Agent 是一种利用 LLM 作为推理引擎，能自主规划、使用工具并完成任务的系统。",
        source=Source.MEMORY,
        relevance=0.9,
    )
    builder.add(
        "上下文工程关注如何在每次模型调用前拼装最优输入上下文，提升正确性与效率。",
        source=Source.TOOL,
        relevance=0.8,
    )

    # 构建 messages
    user_input = "请结合 Agent 的概念，解释上下文工程为什么重要？"
    messages = builder.build(user_input)

    # 打印构建结果
    print("=== 构建的上下文 ===")
    for msg in messages:
        print(f"  [{msg['role']}] {msg['content']}")
    print("=== end ===\n")

    # 调用 LLM
    print("--- 调用 LLM ---")
    stream = llm.chat(messages, stream=True)
    if stream:
        result = LLM.stream_print(stream)
        print("\n--- 完整响应 ---")
        print(result)


if __name__ == "__main__":
    main()
