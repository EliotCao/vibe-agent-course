# my_llm.py
import os
from typing import Optional
from openai import OpenAI
from hello_agents import HelloentsLLM

class MyLLM(HelloAgentsLLM):
    """
    一个自定义的LLM客户端，通过继承增加了对ModelScope的支持。
    """
    pass # 暂时留空