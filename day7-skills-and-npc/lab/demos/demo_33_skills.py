"""Demo 33：Skills 系统演示 —— 扫描、匹配、加载。

运行：python demo_33_skills.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 复用 ch04 的 Skills 类（简化版，适配本地 skills/ 目录）
from skills_loader import Skills


def main():
    # 指向 demos/skills/ 目录（内含 add-docstring / commit-convention）
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    skills = Skills(skills_dir=skills_dir)

    print("=" * 50)
    print("已发现的 Skills:")
    print("=" * 50)
    for name in skills.list():
        meta = skills.get_meta(name)
        print(f"  - {name}: {meta.description}")

    print("\n" + "=" * 50)
    print("索引 Prompt（注入到 system prompt 里的）:")
    print("=" * 50)
    print(skills.to_index_prompt())

    print("\n" + "=" * 50)
    print("匹配测试：")
    print("=" * 50)
    queries = [
        "帮我给这个函数加 docstring",
        "写一个 commit message",
        "帮我优化性能",
    ]
    for q in queries:
        matches = skills.match(q)
        print(f"  '{q}' → {matches}")

    print("\n" + "=" * 50)
    print("加载 add-docstring:")
    print("=" * 50)
    result = skills.load("add-docstring")
    print(f"  {result}")
    print(f"  body 前 100 字: {skills.get('add-docstring')[:100]}...")

    print("\n✅ Skills 系统演示完成！")


if __name__ == "__main__":
    main()
