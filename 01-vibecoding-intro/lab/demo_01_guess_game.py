"""一个 vibe 出来的猜数字游戏

演示 VibeCoding 的成果：从"帮我写个猜数字游戏"这一句话，
经过几轮迭代，得到的参考实现。纯 Python 标准库，直接运行即可。

    python demo_01_guess_game.py

迭代历程（对应讲义 02-vibe-a-game.md）：
  1. 基础版：随机数 + 太大/太小提示
  2. 加次数限制（7 次）
  3. 输入容错（不是数字不崩溃）
  4. 按次数给评价
  5. 再玩一局
"""

import random


MAX_TRIES = 7
LOW, HIGH = 1, 100


def rate(tries: int) -> str:
    """根据猜中所用次数给个评价。"""
    if tries <= 3:
        return "🏆 神乎其技！"
    if tries <= 5:
        return "👍 稳健发挥！"
    return "😅 险胜，下次加油！"


def play_once() -> None:
    """玩一局。"""
    answer = random.randint(LOW, HIGH)
    print(f"\n我想好了一个 {LOW} 到 {HIGH} 之间的数字，你有 {MAX_TRIES} 次机会。")

    for attempt in range(1, MAX_TRIES + 1):
        remaining = MAX_TRIES - attempt + 1
        raw = input(f"第 {attempt} 次猜（还剩 {remaining} 次）: ").strip()

        # 输入容错：不是整数就友好提示，不浪费次数
        if not raw.lstrip("-").isdigit():
            print("  请输入一个整数哦~")
            continue

        guess = int(raw)
        if guess < answer:
            print("  太小了 ⬆️")
        elif guess > answer:
            print("  太大了 ⬇️")
        else:
            print(f"\n🎉 猜对了！答案就是 {answer}，你用了 {attempt} 次。{rate(attempt)}")
            return

    print(f"\n💔 机会用完啦，答案是 {answer}。")


def main() -> None:
    print("=" * 40)
    print("  猜数字游戏 · 我的第一个 vibe 作品")
    print("=" * 40)

    while True:
        play_once()
        again = input("\n再来一局？(y/n): ").strip().lower()
        if again not in ("y", "yes", "是"):
            print("拜拜，下次再玩！👋")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n游戏中断，下次见！")
