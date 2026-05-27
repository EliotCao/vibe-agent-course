"""Skills 加载器（简化版，适配课程本地 skills/ 目录）。

跟 04-my-agent 的 skills.py 逻辑一致，但 skills_dir 改为传参。
"""

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SkillMeta:
    name: str
    description: str
    path: str
    body: str = ""
    loaded: bool = False


class Skills:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self._skills: Dict[str, SkillMeta] = {}
        self._scan()

    def _scan(self):
        self._skills.clear()
        if not os.path.isdir(self.skills_dir):
            return
        for entry in sorted(os.listdir(self.skills_dir)):
            full_path = os.path.join(self.skills_dir, entry)
            if os.path.isdir(full_path):
                skill_file = os.path.join(full_path, "SKILL.md")
                if os.path.isfile(skill_file):
                    meta = self._parse_frontmatter(skill_file)
                    if meta:
                        self._skills[meta.name] = meta
            elif entry.endswith(".md"):
                meta = self._parse_frontmatter(full_path)
                if meta:
                    self._skills[meta.name] = meta

    def _parse_frontmatter(self, path: str) -> Optional[SkillMeta]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, OSError):
            return None
        match = re.match(r'^---\s*\n(.+?)\n---\s*\n', content, re.DOTALL)
        if not match:
            name = os.path.basename(os.path.dirname(path))
            return SkillMeta(name=name, description="", path=path)
        yaml_str = match.group(1)
        name = self._extract(yaml_str, "name") or os.path.basename(os.path.dirname(path))
        desc = self._extract(yaml_str, "description") or ""
        return SkillMeta(name=name, description=desc, path=path)

    @staticmethod
    def _extract(yaml_str: str, field: str) -> str:
        m = re.search(rf'^{field}:\s*(.+)$', yaml_str, re.MULTILINE)
        return m.group(1).strip().strip('"').strip("'") if m else ""

    def load(self, name: str) -> str:
        if name not in self._skills:
            return f"❌ Skill 不存在: {name}"
        meta = self._skills[name]
        if meta.loaded:
            return f"✅ Skill 已加载: {name}"
        try:
            with open(meta.path, "r", encoding="utf-8") as f:
                content = f.read()
            body_match = re.match(r'^---\s*\n.+?\n---\s*\n(.*)$', content, re.DOTALL)
            meta.body = body_match.group(1).strip() if body_match else content.strip()
            meta.loaded = True
            return f"✅ 已加载 skill: {name}"
        except (IOError, OSError) as e:
            return f"❌ 加载失败: {e}"

    def match(self, query: str) -> List[str]:
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
            if score > 0.1:
                scored.append((name, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in scored]

    @staticmethod
    def _tokenize(text: str) -> set:
        text_lower = text.lower()
        tokens = set()
        tokens.update(re.findall(r'[a-z][a-z0-9\-]+', text_lower))
        cn_chars = re.findall(r'[\u4e00-\u9fff]+', text_lower)
        for segment in cn_chars:
            for i in range(len(segment) - 1):
                tokens.add(segment[i:i+2])
        return tokens

    def to_index_prompt(self) -> str:
        if not self._skills:
            return ""
        lines = ["\n## 可用 Skills"]
        for meta in self._skills.values():
            desc = f": {meta.description}" if meta.description else ""
            lines.append(f"- {meta.name}{desc}")
        return "\n".join(lines)

    def to_active_prompt(self) -> str:
        active = [m for m in self._skills.values() if m.loaded and m.body]
        if not active:
            return ""
        parts = ["\n## 已激活 Skills"]
        for m in active:
            parts.append(f"\n### {m.name}\n{m.body}")
        return "\n".join(parts)

    def list(self) -> List[str]:
        return list(self._skills.keys())

    def get_meta(self, name: str) -> Optional[SkillMeta]:
        return self._skills.get(name)

    def get(self, name: str) -> Optional[str]:
        meta = self._skills.get(name)
        return meta.body if meta and meta.loaded else None
