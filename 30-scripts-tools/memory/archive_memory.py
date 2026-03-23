# -*- coding: utf-8 -*-
"""
Archive Memory - 长期归档记忆
基于 SQLite 的持久化存储
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from .models import MemoryItem


class ArchiveMemory:
    """
    长期归档记忆
    
    存储:
    - SQLite 数据库
    - 向量相似度（可选，简化版用关键词）
    - 自动清理机制
    """

    def __init__(self, db_path: str = "13-memory/memory.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        """确保数据库和表存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archive (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                importance REAL NOT NULL,
                created_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                metadata TEXT,
                keywords TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance 
            ON archive(importance DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created 
            ON archive(created_at DESC)
        """)

        conn.commit()
        conn.close()

    def store(self, item: MemoryItem) -> None:
        """存储记忆单元"""
        # 提取关键词
        keywords = self._extract_keywords(item.content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO archive 
            (id, content, type, importance, created_at, access_count, 
             last_accessed, metadata, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.id,
            item.content,
            item.type,
            item.importance,
            item.created_at,
            item.access_count,
            item.last_accessed,
            json.dumps(item.metadata or {}, ensure_ascii=False),
            json.dumps(keywords)
        ))

        conn.commit()
        conn.close()

    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """按ID检索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM archive WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_item(row)
        return None

    def retrieve_recent(self, token_budget: int = 2000) -> List[MemoryItem]:
        """检索最近的记忆（按token预算）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM archive 
            ORDER BY created_at DESC 
            LIMIT 50
        """)

        items = []
        total_chars = 0

        for row in cursor.fetchall():
            item = self._row_to_item(row)
            item_size = len(item.content)

            if total_chars + item_size > token_budget * 4:
                break

            items.append(item)
            total_chars += item_size

        conn.close()
        return items

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """
        搜索记忆
        简化版: 关键词匹配 + 重要性排序
        """
        query_keywords = self._extract_keywords(query)

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 基础查询
        cursor.execute("""
            SELECT * FROM archive 
            ORDER BY importance DESC, created_at DESC
            LIMIT 100
        """)

        results = []
        for row in cursor.fetchall():
            item = self._row_to_item(row)

            # 计算相关性分数
            item_keywords = json.loads(row['keywords'] or '[]')
            relevance = self._calculate_relevance(query_keywords, item_keywords)

            if relevance > 0:
                results.append((item, relevance))

        conn.close()

        # 按相关性排序
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in results[:top_k]]

    def count(self) -> int:
        """记忆总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM archive")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def delete_old(self, days: int = 90, importance_threshold: float = 0.3) -> int:
        """删除旧记忆（可选自动清理）"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM archive 
            WHERE created_at < ? AND importance < ?
        """, (cutoff, importance_threshold))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted

    def get_stats(self) -> Dict:
        """获取归档统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM archive")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(importance) FROM archive")
        avg_importance = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT type, COUNT(*) as cnt 
            FROM archive 
            GROUP BY type
        """)
        type_dist = dict(cursor.fetchall())

        conn.close()

        return {
            "total": total,
            "avg_importance": round(avg_importance, 3),
            "type_distribution": type_dist
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版）"""
        # 简单分词：提取英文单词和中文词
        import re

        # 英文单词
        english = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # 中文词（2-4字）
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)

        # 合并并去重
        keywords = list(set(english + chinese))

        # 过滤停用词
        stopwords = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'they', 'been'}
        keywords = [k for k in keywords if k not in stopwords]

        return keywords[:20]  # 最多20个

    def _calculate_relevance(self, query_keywords: List[str],
                            item_keywords: List[str]) -> float:
        """计算相关性分数"""
        if not query_keywords or not item_keywords:
            return 0.0

        query_set = set(query_keywords)
        item_set = set(item_keywords)

        intersection = query_set & item_set
        union = query_set | item_set

        if not union:
            return 0.0

        # Jaccard 相似度
        return len(intersection) / len(union)

    def _row_to_item(self, row) -> MemoryItem:
        """SQL row 转 MemoryItem"""
        return MemoryItem(
            id=row['id'],
            content=row['content'],
            type=row['type'],
            importance=row['importance'],
            created_at=row['created_at'],
            access_count=row['access_count'],
            last_accessed=row['last_accessed'],
            metadata=json.loads(row['metadata'] or '{}')
        )


# 导出
__all__ = ['ArchiveMemory']