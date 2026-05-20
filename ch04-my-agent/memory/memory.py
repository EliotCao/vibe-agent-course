"""极简记忆系统 —— 基于本地 JSON 文件。

提供三层记忆：
- 工作记忆（working）：会话级，程序退出即清除
- 情景记忆（episodic）：持久化，记录具体事件/操作
- 语义记忆（semantic）：持久化，存储抽象知识/结论

检索基于关键词匹配 + 时间衰减 + 重要性加权。
"""

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from math import exp
from typing import Dict, List, Optional


@dataclass
class MemoryItem:
    """单条记忆。"""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    content: str = ""
    memory_type: str = "working"  # working / episodic / semantic
    importance: float = 0.5  # 0.0 ~ 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


class Memory:
    """极简记忆系统，本地 JSON 文件持久化。

    使用方式：
        mem = Memory(storage_dir=".memory")
        mem.add("用户偏好 Python 风格的代码", memory_type="semantic", importance=0.8)
        mem.add("刚才修改了 main.py 的 main 函数", memory_type="episodic", importance=0.6)
        results = mem.search("main.py")
        mem.save()
    """

    def __init__(self, storage_dir: str = ".memory"):
        self.storage_dir = storage_dir
        self._working: List[MemoryItem] = []
        self._episodic: List[MemoryItem] = []
        self._semantic: List[MemoryItem] = []
        self._load()

    # ========== 核心操作 ==========

    def add(
        self,
        content: str,
        memory_type: str = "working",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> str:
        """添加一条记忆，返回记忆 ID。"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
        )
        self._get_store(memory_type).append(item)

        # 持久化记忆自动保存
        if memory_type != "working":
            self.save()

        return item.id

    def search(
        self,
        query: str,
        limit: int = 5,
        memory_types: Optional[List[str]] = None,
        min_importance: float = 0.0,
    ) -> List[MemoryItem]:
        """搜索记忆，按相关性排序返回。"""
        types = memory_types or ["working", "episodic", "semantic"]
        candidates = []
        for t in types:
            candidates.extend(self._get_store(t))

        # 过滤最低重要性
        candidates = [m for m in candidates if m.importance >= min_importance]

        # 打分排序
        scored = [(m, self._score(m, query)) for m in candidates]
        scored = [(m, s) for m, s in scored if s > 0]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [m for m, _ in scored[:limit]]

    def get_context(self, query: str = "", limit: int = 5) -> str:
        """获取与 query 相关的记忆，格式化为可注入 prompt 的文本。"""
        if not query:
            # 无 query 时返回最近的记忆
            all_items = self._working + self._episodic + self._semantic
            all_items.sort(key=lambda m: m.timestamp, reverse=True)
            items = all_items[:limit]
        else:
            items = self.search(query, limit=limit)

        if not items:
            return ""

        lines = ["[记忆]"]
        for item in items:
            type_label = {"working": "临时", "episodic": "事件", "semantic": "知识"}
            label = type_label.get(item.memory_type, item.memory_type)
            lines.append(f"- [{label}] {item.content}")
        return "\n".join(lines)

    def forget(
        self,
        strategy: str = "importance",
        threshold: float = 0.2,
        max_age_days: int = 30,
    ) -> int:
        """遗忘记忆。返回删除条数。"""
        count = 0
        now = datetime.now()

        for store in [self._episodic, self._semantic]:
            before = len(store)
            if strategy == "importance":
                store[:] = [m for m in store if m.importance >= threshold]
            elif strategy == "time":
                store[:] = [
                    m for m in store
                    if (now - datetime.fromisoformat(m.timestamp)).days <= max_age_days
                ]
            count += before - len(store)

        # 工作记忆全部清除
        if strategy == "working":
            count += len(self._working)
            self._working.clear()

        if count > 0:
            self.save()
        return count

    def stats(self) -> Dict[str, int]:
        """获取各类型记忆数量。"""
        return {
            "working": len(self._working),
            "episodic": len(self._episodic),
            "semantic": len(self._semantic),
            "total": len(self._working) + len(self._episodic) + len(self._semantic),
        }

    def clear(self):
        """清空所有记忆。"""
        self._working.clear()
        self._episodic.clear()
        self._semantic.clear()
        self.save()

    # ========== 持久化 ==========

    def save(self):
        """保存持久化记忆到文件。"""
        os.makedirs(self.storage_dir, exist_ok=True)
        data = {
            "episodic": [asdict(m) for m in self._episodic],
            "semantic": [asdict(m) for m in self._semantic],
        }
        path = os.path.join(self.storage_dir, "memory.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load(self):
        """从文件加载持久化记忆。"""
        path = os.path.join(self.storage_dir, "memory.json")
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._episodic = [MemoryItem(**m) for m in data.get("episodic", [])]
            self._semantic = [MemoryItem(**m) for m in data.get("semantic", [])]
        except (json.JSONDecodeError, TypeError):
            pass

    # ========== 内部方法 ==========

    def _get_store(self, memory_type: str) -> List[MemoryItem]:
        """获取对应类型的存储列表。"""
        if memory_type == "working":
            return self._working
        elif memory_type == "episodic":
            return self._episodic
        elif memory_type == "semantic":
            return self._semantic
        else:
            return self._working

    def _score(self, item: MemoryItem, query: str) -> float:
        """计算记忆与 query 的匹配分数。

        公式: 关键词匹配 × 时间衰减 × (0.8 + importance × 0.4)
        """
        # 关键词匹配
        keyword_score = self._keyword_match(item.content, query)
        # tags 匹配加分
        for tag in item.tags:
            if tag.lower() in query.lower():
                keyword_score = min(1.0, keyword_score + 0.3)

        if keyword_score == 0:
            return 0

        # 时间衰减（24h 半衰期）
        age_hours = (
            datetime.now() - datetime.fromisoformat(item.timestamp)
        ).total_seconds() / 3600
        time_decay = exp(-age_hours / 24)
        # 工作记忆衰减更快
        if item.memory_type == "working":
            time_decay = exp(-age_hours / 4)

        # 重要性权重
        importance_weight = 0.8 + item.importance * 0.4

        return keyword_score * time_decay * importance_weight

    @staticmethod
    def _keyword_match(text: str, query: str) -> float:
        """简单关键词匹配分数。"""
        if not query:
            return 0.5  # 无 query 时给基础分

        text_lower = text.lower()
        query_tokens = query.lower().split()
        if not query_tokens:
            return 0

        matches = sum(1 for t in query_tokens if t in text_lower)
        return matches / len(query_tokens)
