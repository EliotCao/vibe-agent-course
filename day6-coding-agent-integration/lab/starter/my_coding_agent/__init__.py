# my_coding_agent 包顶层 __init__
# 用户直接 cd 进来跑 python main.py 即可，这个 __init__ 只是让 demo 脚本能 import 单个零件

from .agent import CodingAgent

__all__ = ["CodingAgent"]
