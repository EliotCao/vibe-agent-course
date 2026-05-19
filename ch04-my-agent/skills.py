"""Skills 模块 —— 渐进式加载的知识/规范片段。

行业标准格式（Anthropic Agent Skills 规范）：
- SKILL.md = YAML frontmatter（元数据）+ Markdown body（指令正文）
- 启动时只解析 frontmatter（name + description），不加载 body
- 根据用户问题匹配相关 skill，按需加载 body 到 prompt

渐进式披露：
  Level 1: 只将 name + description 注入 prompt（让 LLM 知道有哪些 skill 可用）
  Level 2: 用户问题匹配到 skill 时，加载完整 body 注入 prompt
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SkillMeta:
    """Skill 元数据（从 YAML frontmatter 解析）。"""

    name: str
    description: str
    path: str  # SKILL.md 的完整路径
    body: str = ""  # 完整指令正文（按需加载）
    loaded: bool = False  # body 是否已加载


class Skills:
    """Skills 管理器 —— 渐进式加载。

    启动时：扫描 ~/.codebuddy/skills/，只解析 frontmatter
    运行时：根据用户问题匹配 skill，按需加载 body
    """

    def __init__(self):
        self.skills_dir = os.path.join(os.path.expanduser("~"), ".codebuddy", "skills")
        self._skills: Dict[str, SkillMeta] = {}  # name -> SkillMeta
        self._scan()

    def _scan(self):
        """扫描 skills 目录，只解析 frontmatter（不加载 body）。"""
        self._skills.clear()
        if not os.path.isdir(self.skills_dir):
            return

        for entry in sorted(os.listdir(self.skills_dir)):
            full_path = os.path.join(self.skills_dir, entry)

            # 目录形式: skills/name/SKILL.md
            if os.path.isdir(full_path):
                skill_file = os.path.join(full_path, "SKILL.md")
                if os.path.isfile(skill_file):
                    meta = self._parse_frontmatter(skill_file)
                    if meta:
                        self._skills[meta.name] = meta

            # 文件形式: skills/name.md
            elif entry.endswith(".md"):
                skill_file = full_path
                meta = self._parse_frontmatter(skill_file)
                if meta:
                    self._skills[meta.name] = meta

    def _parse_frontmatter(self, path: str) -> Optional[SkillMeta]:
        """解析 SKILL.md 的 YAML frontmatter，只提取 name 和 description。"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, OSError):
            return None

        # 匹配 --- ... --- frontmatter
        match = re.match(r'^---\s*\n(.+?)\n---\s*\n', content, re.DOTALL)
        if not match:
            # 无 frontmatter，用文件名作为 name
            name = os.path.basename(os.path.dirname(path))
            if name == "skills":
                name = os.path.splitext(os.path.basename(path))[0]
            return SkillMeta(name=name, description="", path=path)

        yaml_str = match.group(1)
        name = self._extract_yaml_field(yaml_str, "name") or os.path.basename(os.path.dirname(path))
        description = self._extract_yaml_field(yaml_str, "description") or ""

        return SkillMeta(name=name, description=description, path=path)

    @staticmethod
    def _extract_yaml_field(yaml_str: str, field: str) -> str:
        """简易 YAML 字段提取（不依赖 pyyaml）。"""
        match = re.search(rf'^{field}:\s*(.+)$', yaml_str, re.MULTILINE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
        return ""

    # ========== 按需加载 ==========

    def load(self, name: str) -> str:
        """加载指定 skill 的完整 body。"""
        if name not in self._skills:
            return f"❌ Skill 不存在: {name}"

        meta = self._skills[name]
        if meta.loaded:
            return f"✅ Skill 已加载: {name}"

        try:
            with open(meta.path, "r", encoding="utf-8") as f:
                content = f.read()
            # 去掉 frontmatter，只保留 body
            body_match = re.match(r'^---\s*\n.+?\n---\s*\n(.*)$', content, re.DOTALL)
            meta.body = body_match.group(1).strip() if body_match else content.strip()
            meta.loaded = True
            return f"✅ 已加载 skill: {name}"
        except (IOError, OSError) as e:
            return f"❌ 加载失败: {e}"

    def unload(self, name: str) -> str:
        """卸载指定 skill（释放 body）。"""
        if name not in self._skills:
            return f"❌ Skill 不存在: {name}"
        self._skills[name].body = ""
        self._skills[name].loaded = False
        return f"✅ 已卸载 skill: {name}"

    def match(self, query: str) -> List[str]:
        """根据用户问题匹配相关 skills，按相关性排序返回。

        分词策略：英文用完整词，中文用 2-gram 滑动窗口。
        只返回得分 > 0.15 的 skill。
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scored = []
        for name, meta in self._skills.items():
            text = f"{meta.name} {meta.description}"
            skill_tokens = self._tokenize(text)
            if not skill_tokens:
                continue
            overlap = query_tokens & skill_tokens
            score = len(overlap) / len(query_tokens)
            if score > 0.15:
                scored.append((name, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scored]

    @staticmethod
    def _tokenize(text: str) -> set:
        """分词：英文用完整词，中文用 2-gram。"""
        text_lower = text.lower()
        tokens = set()

        # 英文词
        en_words = re.findall(r'[a-z][a-z0-9\-]+', text_lower)
        tokens.update(en_words)

        # 中文 2-gram
        cn_chars = re.findall(r'[\u4e00-\u9fff]+', text_lower)
        for segment in cn_chars:
            for i in range(len(segment) - 1):
                tokens.add(segment[i:i+2])

        return tokens

    # ========== 生成 prompt ==========

    def to_index_prompt(self) -> str:
        """生成 skill 索引（Level 1: 只有 name + description）。"""
        if not self._skills:
            return ""

        lines = ["\n## 可用 Skills"]
        for meta in self._skills.values():
            desc = f": {meta.description}" if meta.description else ""
            lines.append(f"- {meta.name}{desc}")
        lines.append("\n（当你认为某个 skill 与当前任务相关时，可以参考它的完整内容）")
        return "\n".join(lines)

    def to_active_prompt(self) -> str:
        """生成已加载 skill 的完整内容（Level 2）。"""
        active = [meta for meta in self._skills.values() if meta.loaded and meta.body]
        if not active:
            return ""

        parts = ["\n## 已激活 Skills"]
        for meta in active:
            parts.append(f"\n### {meta.name}\n{meta.body}")
        return "\n".join(parts)

    # ========== 查询接口 ==========

    def list(self) -> List[str]:
        """列出所有已发现的 skill 名称。"""
        return list(self._skills.keys())

    def list_loaded(self) -> List[str]:
        """列出已加载 body 的 skill。"""
        return [name for name, meta in self._skills.items() if meta.loaded]

    def get_meta(self, name: str) -> Optional[SkillMeta]:
        """获取 skill 元数据。"""
        return self._skills.get(name)

    def get(self, name: str) -> Optional[str]:
        """获取已加载 skill 的 body。"""
        meta = self._skills.get(name)
        if meta and meta.loaded:
            return meta.body
        return None
