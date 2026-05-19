"""Skills 模块 —— 可动态加载的知识/规范片段。

Skills 是 .codebuddy/skills/ 目录下的 .md 文件，
启动时自动加载，也可通过 /skill 命令动态管理。
"""

import os
from typing import Dict, List, Optional


class Skills:
    """Skills 管理器。

    使用方式：
        skills = Skills(workdir="/workspace/project")
        skills.load_all()           # 加载所有 skill
        prompt = skills.to_prompt() # 生成注入 system prompt 的文本
        skills.list()               # 列出已加载的 skill
    """

    def __init__(self):
        self.skills_dir = os.path.join(os.path.expanduser("~"), ".codebuddy", "skills")
        self._loaded: Dict[str, str] = {}  # name -> content
        self.load_all()

    def load_all(self) -> int:
        """扫描 skills 目录，加载所有 skill。

        支持两种格式：
        - 目录形式: skills/name/SKILL.md
        - 文件形式: skills/name.md
        """
        self._loaded.clear()
        if not os.path.isdir(self.skills_dir):
            return 0

        for entry in sorted(os.listdir(self.skills_dir)):
            full_path = os.path.join(self.skills_dir, entry)

            # 格式一：目录下的 SKILL.md
            if os.path.isdir(full_path):
                skill_file = os.path.join(full_path, "SKILL.md")
                if os.path.isfile(skill_file):
                    content = self._read_file(skill_file)
                    if content:
                        self._loaded[entry] = content

            # 格式二：直接的 .md 文件
            elif entry.endswith(".md"):
                content = self._read_file(full_path)
                if content:
                    name = entry[:-3]
                    self._loaded[name] = content

        return len(self._loaded)

    def load(self, name: str) -> str:
        """加载指定 skill。"""
        # 先找目录形式
        dir_path = os.path.join(self.skills_dir, name, "SKILL.md")
        # 再找文件形式
        file_path = os.path.join(self.skills_dir, f"{name}.md")

        path = None
        if os.path.isfile(dir_path):
            path = dir_path
        elif os.path.isfile(file_path):
            path = file_path

        if not path:
            return f"❌ Skill 不存在: {name}"
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            self._loaded[name] = content
            return f"✅ 已加载 skill: {name}"
        except (IOError, OSError) as e:
            return f"❌ 加载失败: {e}"

    def unload(self, name: str) -> str:
        """卸载指定 skill。"""
        if name in self._loaded:
            del self._loaded[name]
            return f"✅ 已卸载 skill: {name}"
        return f"❌ Skill 未加载: {name}"

    def list(self) -> List[str]:
        """列出已加载的 skill 名称。"""
        return list(self._loaded.keys())

    def list_available(self) -> List[str]:
        """列出目录中所有可用的 skill。"""
        if not os.path.isdir(self.skills_dir):
            return []
        result = []
        for entry in sorted(os.listdir(self.skills_dir)):
            full_path = os.path.join(self.skills_dir, entry)
            if os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "SKILL.md")):
                result.append(entry)
            elif entry.endswith(".md"):
                result.append(entry[:-3])
        return result

    def get(self, name: str) -> Optional[str]:
        """获取指定 skill 的内容。"""
        return self._loaded.get(name)

    def to_prompt(self) -> str:
        """将所有已加载的 skills 合并为可注入 system prompt 的文本。"""
        if not self._loaded:
            return ""

        parts = ["\n## Skills"]
        for name, content in self._loaded.items():
            parts.append(f"\n### {name}\n{content}")

        return "\n".join(parts)

    def create(self, name: str, content: str) -> str:
        """创建一个新 skill 文件。"""
        os.makedirs(self.skills_dir, exist_ok=True)
        path = os.path.join(self.skills_dir, f"{name}.md")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._loaded[name] = content
            return f"✅ 已创建 skill: {name} ({path})"
        except (IOError, OSError) as e:
            return f"❌ 创建失败: {e}"

    @staticmethod
    def _read_file(path: str) -> str:
        """读取文件内容，失败返回空字符串。"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except (IOError, OSError):
            return ""
