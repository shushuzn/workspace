#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流缓存 - 缓存上下文验证结果，加速重复任务
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

class WorkflowCache:
    """工作流缓存系统"""

    def __init__(self, cache_dir: str = "flow-archive/20260318-universal-workflow-001/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """加载缓存索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": {}, "total_hits": 0, "total_misses": 0}

    def _save_index(self):
        """保存缓存索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _compute_key(self, data: Any) -> str:
        """计算缓存键"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self.index['entries']:
            entry = self.index['entries'][key]

            # 检查是否过期 (默认 24 小时)
            cached_at = datetime.fromisoformat(entry['cached_at'])
            if datetime.now() - cached_at > timedelta(hours=24):
                # 过期，删除
                del self.index['entries'][key]
                self._save_index()
                self.index['total_misses'] += 1
                return None

            # 命中
            self.index['total_hits'] += 1
            entry['hits'] = entry.get('hits', 0) + 1
            self._save_index()

            # 读取缓存文件
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

        self.index['total_misses'] += 1
        self._save_index()
        return None

    def set(self, data: Any, key: str = None) -> str:
        """设置缓存"""
        if key is None:
            key = self._compute_key(data)

        # 保存缓存数据
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 更新索引
        self.index['entries'][key] = {
            'cached_at': datetime.now().isoformat(),
            'size_bytes': cache_file.stat().st_size,
            'hits': 0
        }
        self._save_index()

        return key

    def clear(self):
        """清空缓存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        self.index = {"entries": {}, "total_hits": 0, "total_misses": 0}
        self._save_index()

    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.index['total_hits'] + self.index['total_misses']
        hit_rate = (self.index['total_hits'] / total * 100) if total > 0 else 0

        return {
            "total_entries": len(self.index['entries']),
            "total_hits": self.index['total_hits'],
            "total_misses": self.index['total_misses'],
            "hit_rate": hit_rate,
            "cache_size_kb": sum(
                e.get('size_bytes', 0) for e in self.index['entries'].values()
            ) / 1024
        }

    def display_status(self) -> str:
        """显示缓存状态"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 60)
        output.append(" " * 20 + "Workflow Cache Status")
        output.append("=" * 60)

        output.append(f"\n[Cache Stats]")
        output.append(f"  Entries:     {stats['total_entries']}")
        output.append(f"  Total Hits:  {stats['total_hits']}")
        output.append(f"  Total Misses:{stats['total_misses']}")
        output.append(f"  Hit Rate:    {stats['hit_rate']:.1f}%")
        output.append(f"  Cache Size:  {stats['cache_size_kb']:.1f} KB")

        if stats['hit_rate'] > 50:
            output.append(f"\n[OK] Cache is effective!")
        else:
            output.append(f"\n[INFO] Cache warming up...")

        output.append("=" * 60)

        return "\n".join(output)

    def run(self) -> Dict:
        """运行缓存"""
        return {
            "stats": self.get_stats(),
            "success": True
        }

def main():
    """测试入口"""
    cache = WorkflowCache()

    print("Workflow Cache Test")
    print("=" * 60)

    # 测试：设置缓存
    test_data = {"context_loaded": True, "files": ["SOUL.md", "USER.md"]}
    key = cache.set(test_data)
    print(f"\n[OK] Cached data with key: {key[:16]}...")

    # 测试：获取缓存
    result = cache.get(key)
    print(f"[OK] Cache hit: {result is not None}")

    # 测试：获取不存在的缓存
    result2 = cache.get("nonexistent_key")
    print(f"[OK] Cache miss: {result2 is None}")

    # 显示状态
    print(cache.display_status())

    print(f"\n[OK] Cache test completed")

if __name__ == "__main__":
    main()
