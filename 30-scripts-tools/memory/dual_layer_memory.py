# -*- coding: utf-8 -*-
"""
Dual Layer Memory - 主控制器
协调 Working Memory 和 Archive Memory
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .models import MemoryItem
from .working_memory import WorkingMemory
from .archive_memory import ArchiveMemory
from .importance_scorer import ImportanceScorer
from .forgetting_mechanism import ForgettingMechanism
from .session_bridge import SessionBridge


class DualLayerMemory:
    """
    双层记忆系统主控制器
    
    架构:
    ┌─────────────────────────────────────┐
    │         Working Memory              │
    │    (短期上下文 - 当前任务相关)       │
    │    - Token: <5000                   │
    │    - 生命周期: 当前会话             │
    └─────────────────────────────────────┘
                    ↓ 遗忘/归档
    ┌─────────────────────────────────────┐
    │         Archive Memory              │
    │    (长期记忆 - 重要信息)            │
    │    - SQLite 存储                    │
    │    - 向量检索 (可选)                │
    └─────────────────────────────────────┘
    """
    
    def __init__(self, token_budget: int = 5000, db_path: str = None):
        self.token_budget = token_budget
        self.db_path = db_path or "13-memory/memory.db"
        
        # 初始化子模块
        self.working = WorkingMemory(token_budget)
        self.archive = ArchiveMemory(self.db_path)
        self.scorer = ImportanceScorer()
        self.forgetting = ForgettingMechanism()
        self.bridge = SessionBridge()
        
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add(self, content: str, memory_type: str = 'conversation', 
            metadata: Dict = None) -> MemoryItem:
        """添加记忆，自动判断存入哪层"""
        item = MemoryItem(
            id=f"{self._session_id}_{datetime.now().timestamp()}",
            content=content,
            type=memory_type,
            importance=self.scorer.calculate(content, memory_type, metadata or {}),
            created_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # 重要性 >= 0.7 → 直接归档
        # 否则 → 工作记忆
        if item.importance >= 0.7:
            self.archive.store(item)
        else:
            self.working.add(item)
        
        return item
    
    def get_context(self, max_tokens: int = None) -> List[MemoryItem]:
        """获取当前上下文（合并两层）"""
        max_tokens = max_tokens or self.token_budget
        
        # 1. 获取工作记忆
        working_items = self.working.get_all()
        
        # 2. 不足时从归档补充
        if self.working.estimate_tokens(working_items) < max_tokens * 0.6:
            needed = max_tokens - self.working.estimate_tokens(working_items)
            archive_items = self.archive.retrieve_recent(needed)
            working_items.extend(archive_items)
        
        return working_items
    
    def compress(self) -> Dict:
        """压缩工作记忆，将低优先级移到归档"""
        results = {
            "compressed": 0,
            "archived": 0,
            "forgotten": 0
        }
        
        # 1. 压缩工作记忆
        compressed_items = self.working.compress()
        results["compressed"] = compressed_items
        
        # 2. 归档低优先级
        low_priority = self.working.get_low_priority()
        for item in low_priority:
            self.archive.store(item)
            self.working.remove(item.id)
            results["archived"] += 1
        
        # 3. 触发遗忘机制
        forgotten = self.forgetting.apply(self.archive)
        results["forgotten"] = forgotten
        
        return results
    
    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """跨层检索"""
        return self.archive.search(query, top_k)
    
    def bridge_to(self, new_session_id: str) -> Dict:
        """跨Session继承"""
        essential = self.bridge.export_essential(
            self.working, 
            self.archive, 
            new_session_id
        )
        return essential
    
    def get_stats(self) -> Dict:
        """获取记忆系统统计"""
        return {
            "working_count": self.working.count(),
            "working_tokens": self.working.estimate_tokens(self.working.get_all()),
            "archive_count": self.archive.count(),
            "session_id": self._session_id,
            "token_budget": self.token_budget
        }
    
    def save_state(self, path: str = None) -> str:
        """保存状态到文件"""
        path = path or f"13-memory/memory_state_{self._session_id}.json"
        
        state = {
            "session_id": self._session_id,
            "token_budget": self.token_budget,
            "working_items": [item.to_dict() for item in self.working.get_all()],
            "saved_at": datetime.now().isoformat()
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return path


def load_memory(state_path: str) -> DualLayerMemory:
    """从保存的状态恢复"""
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    memory = DualLayerMemory(
        token_budget=state.get('token_budget', 5000)
    )
    memory._session_id = state.get('session_id', 'restored')
    
    # 恢复工作记忆
    for item_dict in state.get('working_items', []):
        item = MemoryItem(**item_dict)
        memory.working.add(item)
    
    return memory


# CLI 入口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Dual-layer Memory System")
    parser.add_argument("action", choices=["add", "compress", "search", "stats", "bridge"])
    parser.add_argument("--content", "-c", help="Content to add")
    parser.add_argument("--type", "-t", default="conversation", help="Memory type")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--session", "-s", help="New session ID for bridge")
    
    args = parser.parse_args()
    
    memory = DualLayerMemory()
    
    if args.action == "add":
        item = memory.add(args.content, args.type)
        print(f"Added: {item.id} (importance: {item.importance:.2f})")
    
    elif args.action == "compress":
        result = memory.compress()
        print(f"Compressed: {result}")
    
    elif args.action == "search":
        results = memory.search(args.query or "")
        for r in results:
            print(f"- {r.content[:80]}...")
    
    elif args.action == "stats":
        stats = memory.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.action == "bridge":
        result = memory.bridge_to(args.session or "new_session")
        print(json.dumps(result, indent=2, ensure_ascii=False))