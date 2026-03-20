#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMART-CACHE-001 Smart Cache Manager
【智能缓存管理器】

功能:
  - 缓存LLM响应避免重复调用
  - 基于内容hash的精确匹配
  - 缓存统计与分析
  - 自动过期清理
"""
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timedelta


CACHE_DIR = Path("60-DATA/smart_cache_001")
CACHE_FILE = CACHE_DIR / "cache_store.json"
CACHE_STATS = CACHE_DIR / "cache_stats.json"


class SmartCache:
    """智能缓存"""
    
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = CACHE_FILE
        self.stats_file = CACHE_STATS
        
        self._ensure_cache_file()
    
    def _ensure_cache_file(self):
        if not self.cache_file.exists():
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump({"entries": {}, "metadata": {"created": datetime.now().isoformat()}}, f)
    
    def _load_cache(self) -> dict:
        with open(self.cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_cache(self, data: dict):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def get(self, prompt: str) -> dict:
        """获取缓存"""
        cache = self._load_cache()
        key = self._hash_key(prompt)
        
        if key in cache["entries"]:
            entry = cache["entries"][key]
            
            # 检查过期
            created = datetime.fromisoformat(entry["created_at"])
            if datetime.now() - created > timedelta(hours=self.ttl_hours):
                del cache["entries"][key]
                self._save_cache(cache)
                return {"status": "expired", "data": None}
            
            return {
                "status": "hit",
                "data": entry["response"],
                "created_at": entry["created_at"],
                "hit_count": entry.get("hit_count", 1)
            }
        
        return {"status": "miss", "data": None}
    
    def set(self, prompt: str, response: str) -> bool:
        """设置缓存"""
        cache = self._load_cache()
        key = self._hash_key(prompt)
        
        cache["entries"][key] = {
            "prompt": prompt[:100] + "...",
            "response": response,
            "created_at": datetime.now().isoformat(),
            "hit_count": 0
        }
        
        self._save_cache(cache)
        return True
    
    def delete(self, prompt: str) -> bool:
        """删除缓存"""
        cache = self._load_cache()
        key = self._hash_key(prompt)
        
        if key in cache["entries"]:
            del cache["entries"][key]
            self._save_cache(cache)
            return True
        
        return False
    
    def clear(self) -> int:
        """清空缓存"""
        cache = self._load_cache()
        count = len(cache["entries"])
        
        cache["entries"] = {}
        self._save_cache(cache)
        
        return count
    
    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        cache = self._load_cache()
        expired_keys = []
        
        for key, entry in cache["entries"].items():
            created = datetime.fromisoformat(entry["created_at"])
            if datetime.now() - created > timedelta(hours=self.ttl_hours):
                expired_keys.append(key)
        
        for key in expired_keys:
            del cache["entries"][key]
        
        self._save_cache(cache)
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """获取统计"""
        cache = self._load_cache()
        
        total = len(cache["entries"])
        total_hits = sum(e.get("hit_count", 0) for e in cache["entries"].values())
        
        # 按时间分组
        now = datetime.now()
        last_hour = 0
        last_day = 0
        
        for entry in cache["entries"].values():
            created = datetime.fromisoformat(entry["created_at"])
            age = (now - created).total_seconds()
            
            if age < 3600:
                last_hour += 1
            if age < 86400:
                last_day += 1
        
        return {
            "total_entries": total,
            "total_hits": total_hits,
            "last_hour": last_hour,
            "last_day": last_day,
            "cache_size_kb": self.cache_file.stat().st_size / 1024 if self.cache_file.exists() else 0
        }
    
    def get_all(self, limit: int = 10) -> list:
        """获取所有缓存条目"""
        cache = self._load_cache()
        entries = []
        
        for key, entry in cache["entries"].items():
            entries.append({
                "key": key,
                "prompt": entry["prompt"],
                "created_at": entry["created_at"],
                "hit_count": entry.get("hit_count", 0)
            })
        
        entries.sort(key=lambda x: x["created_at"], reverse=True)
        return entries[:limit]


def main():
    cache = SmartCache()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--get":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            if not prompt:
                return 1
            
            result = cache.get(prompt)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--set":
            # --set "prompt" "response"
            if len(sys.argv) < 4:
                print("Usage: --set <prompt> <response>")
                return 1
            
            prompt = sys.argv[2]
            response = sys.argv[3]
            cache.set(prompt, response)
            print(json.dumps({"status": "saved", "key": cache._hash_key(prompt)}))
            return 0
        
        if sys.argv[1] == "--delete":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            result = cache.delete(prompt)
            print(json.dumps({"status": "deleted" if result else "not_found"}))
            return 0
        
        if sys.argv[1] == "--clear":
            count = cache.clear()
            print(json.dumps({"status": "cleared", "count": count}))
            return 0
        
        if sys.argv[1] == "--cleanup":
            count = cache.cleanup_expired()
            print(json.dumps({"status": "cleaned", "count": count}))
            return 0
        
        if sys.argv[1] == "--stats":
            stats = cache.get_stats()
            print(json.dumps(stats, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--list":
            entries = cache.get_all()
            print(json.dumps(entries, ensure_ascii=False, indent=2))
            return 0
    
    print("SMART-CACHE-001 Smart Cache Manager")
    print("Usage:")
    print("  py smart_cache_001.py --get <prompt>      # Get cached response")
    print("  py smart_cache_001.py --set <p> <r>       # Set cache entry")
    print("  py smart_cache_001.py --delete <prompt>   # Delete cache entry")
    print("  py smart_cache_001.py --clear             # Clear all cache")
    print("  py smart_cache_001.py --cleanup           # Clean expired entries")
    print("  py smart_cache_001.py --stats             # Show cache statistics")
    print("  py smart_cache_001.py --list              # List cache entries")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())