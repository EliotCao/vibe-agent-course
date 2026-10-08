"""
第6章工具集 · edit：精确替换已有文件中的一段文本。

设计思路：为什么用 old_content/new_content 匹配而非行号？
  - LLM 看到的是文本内容，天然不感知行号。
  - 任何一次修改都会导致后续行号整体偏移，多步编辑时极易出错。
  - 基于 old_content/new_content 的内容替换是"按内容定位"，永远精确、不受行号漂移影响。

唯一性约束：
  - old_content 必须在文件中恰好出现一次，否则无法确定修改目标。
  - 出现 0 次 → 模型给的 old_content 与实际文件内容不匹配。
  - 出现多次 → 模型需要追加更多上下文，使 old_content 在文件中唯一。
"""

import os
import tempfile

# 10 MB，edit 工具不支持更大文件
MAX_FILE_SIZE = 10 * 1024 * 1024


def edit(path: str, old_content: str, new_content: str) -> str:
    """精确替换已有文件中指定的一段文本。

    通过 old_content 匹配文件中的目标内容并替换为 new_content。
    采用基于内容的定位策略（而非行号），避免了行号漂移导致的多步编辑错误，
    更贴近 LLM 对文本的感知方式——LLM 看到的是内容，不是行号。

    参数
    ----
    path : str
        目标文件的路径。必须是已存在的普通文件，否则返回错误。
    old_content : str
        待替换的原内容。必须在文件中恰好出现一次，否则无法确定修改目标：
        - 出现 0 次：old_content 与实际文件内容不匹配，请先用 read 工具确认文件当前内容。
        - 出现多次：需要追加更多上下文（前后多取几行），使 old_content 在文件中唯一。
    new_content : str
        替换后的新内容，将原样写入 old_content 所在位置。

    返回
    ----
    str
        操作结果消息，以 emoji 前缀区分状态：
        - `✅` 替换成功
        - `❌` 操作失败（含失败原因与修复提示）

    注意事项
    --------
    - old_content 必须与文件内容逐字符对得上，包括空格、缩进和换行符。
    - 替换仅作用于第一次匹配，不会多次替换。
    - 文件以 UTF-8 编码读写，不会追加末尾换行。
    - 本工具会将整个文件读入内存，不适合处理超大文件（>{MAX_FILE_SIZE // 1024 // 1024}MB）。
    """
    if not os.path.exists(path):
        return f"❌ 文件不存在: {path}"

    if not os.path.isfile(path):
        return f"❌ 路径不是文件（可能是目录）: {path}"

    file_size = os.path.getsize(path)
    if file_size > MAX_FILE_SIZE:
        return (
            f"❌ 文件过大（{file_size:,} 字节），edit 工具仅支持 "
            f"≤{MAX_FILE_SIZE // 1024 // 1024}MB 的文件\n"
            "   提示：超大文件请用 sed 或专门的大文件处理工具"
        )

    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
    except Exception as e:
        return f"❌ 读取失败: {e}"

    count = content.count(old_content)
    if count == 0:
        return (
            f"❌ 未找到匹配内容: {path}\n"
            "   提示：请用 read 工具确认文件当前内容，"
            "old_content 必须**逐字符**对得上（含空格、缩进、换行）"
        )
    if count > 1:
        return (
            f"❌ old_content 在文件中出现 {count} 次，无法确定改哪一处\n"
            "   提示：请把 old_content 加更多上下文（前后多取几行），"
            "让它在文件中唯一"
        )

    new_full = content.replace(old_content, new_content, 1)

    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(new_full)
        return f"✅ 已替换 {path} 中的内容"
    except Exception as e:
        return f"❌ 写入失败: {e}"


def print_file_content(path: str) -> None:
    print(f"查看文件 {path} 内容：")
    print()

    try:
        with open(path, "r", encoding="utf-8") as file:
            print(file.read())
    except Exception as e:
        print(e)


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    filepath = os.path.join(tmp, "code.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("""def say_hello() -> None:
    print("hi")

    if __name__ == "__main__":
        say_hello()
""")

    replace_list: list[dict[str, str]] = [
        {
            "old_content": "print(\"hi\")",
            "new_content": "print(\"howdy\")",
            "description": "预期匹配成功（且唯一），并完成替换",
        },
        {
            "old_content": "ʕ•̫͡•ʕ ʕ•͓͡•ʔ  ʕ•̫͡•ʔ ʔ-̫͡-ʔ ʕ•̫͡•ʕ ʕ•͓͡•ʔ",
            "new_content": " :)",
            "description": "编辑一个不存在的内容，预期失败",
        },
        {
            "old_content": "(",
            "new_content": "[",
            "description": "编辑一个存在多处匹配的内容，预期失败",
        }
    ]

    print_file_content(filepath)
    index = 1
    for replace_params in replace_list:
        print(f"编辑实验 {index}: {replace_params.get('description', '')}")
        edit(filepath, replace_params.get("old_content"), replace_params.get("new_content"))
        print("查看调用编辑功能后的文件内容：\n")
        print_file_content(filepath)
        index += 1
        print()
