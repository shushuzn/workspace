#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Result Cache - 结果缓存

缓存工具执行结果以提高重复任务效率
"""

import os
import json
import hashlib
import gzip
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
CACHE_DIR = "cache\\results"
CACHE_DB = "cache\\result-cache.json"

class ResultCache:
    """结果缓存"""
    
    def __init__(self, default_ttl_hours=24):
        self.cache_dir = os.path.join(WORKSPACE, CACHE_DIR)
        self.cache_db_path = os.path.join(WORKSPACE, CACHE_DB)
        self.default_ttl = timedelta(hours=default_ttl_hours)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_key(self, tool_id, params):
        """生成缓存键"""
        key_data = f"{tool_id}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def _load_cache_db(self):
        """加载缓存数据库"""
        if os.path.exists(self.cache_db_path):
            with open(self.cache_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": {}, "stats": {"hits": 0, "misses": 0, "size": 0}}
    
    def _save_cache_db(self, db):
        """保存缓存数据库"""
        with open(self.cache_db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    
    def get(self, tool_id, params):
        """获取缓存结果"""
        key = self._generate_key(tool_id, params)
        db = self._load_cache_db()
        
        if key in db["entries"]:
            entry = db["entries"][key]
            
            # 检查是否过期
            created_at = datetime.fromisoformat(entry["created_at"])
            ttl = timedelta(hours=entry.get("ttl_hours", self.default_ttl.total_seconds() / 3600))
            
            if datetime.now() < created_at + ttl:
                # 缓存命中
                db["stats"]["hits"] = db.get("stats", {}).get("hits", 0) + 1
                
                # 读取缓存文件
                cache_file = os.path.join(self.cache_dir, f"{key}.json.gz")
                if os.path.exists(cache_file):
                    with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                        result = json.load(f)
                    
                    self._save_cache_db(db)
                    return {
                        "hit": True,
                        "result": result,
                        "age_seconds": (datetime.now() - created_at).total_seconds()
                    }
        
        # 缓存未命中
        db["stats"]["misses"] = db.get("stats", {}).get("misses", 0) + 1
        self._save_cache_db(db)
        
        return {"hit": False, "result": None}
    
    def set(self, tool_id, params, result, ttl_hours=None):
        """设置缓存结果"""
        key = self._generate_key(tool_id, params)
        db = self._load_cache_db()
        
        # 保存结果到文件 (gzip 压缩)
        cache_file = os.path.join(self.cache_dir, f"{key}.json.gz")
        
        with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)
        
        # 更新数据库
        db["entries"][key] = {
            "tool_id": tool_id,
            "params": params,
            "created_at": datetime.now().isoformat(),
            "ttl_hours": ttl_hours or self.default_ttl.total_seconds() / 3600,
            "size": os.path.getsize(cache_file),
            "file": cache_file
        }
        
        # 更新统计
        db["stats"]["size"] = db.get("stats", {}).get("size", 0) + 1
        self._save_cache_db(db)
        
        return {"key": key, "size": os.path.getsize(cache_file)}
    
    def clear_expired(self):
        """清理过期缓存"""
        db = self._load_cache_db()
        deleted = []
        
        now = datetime.now()
        keys_to_remove = []
        
        for key, entry in db["entries"].items():
            created_at = datetime.fromisoformat(entry["created_at"])
            ttl = timedelta(hours=entry.get("ttl_hours", self.default_ttl.total_seconds() / 3600))
            
            if now >= created_at + ttl:
                keys_to_remove.append(key)
                
                # 删除文件
                cache_file = entry.get("file", "")
                if cache_file and os.path.exists(cache_file):
                    os.remove(cache_file)
                
                deleted.append({
                    "key": key,
                    "tool_id": entry.get("tool_id", "unknown"),
                    "age_hours": (now - created_at).total_seconds() / 3600
                })
        
        # 从数据库移除
        for key in keys_to_remove:
            del db["entries"][key]
        
        db["stats"]["size"] = len(db["entries"])
        self._save_cache_db(db)
        
        return deleted
    
    def clear_all(self):
        """清空所有缓存"""
        db = self._load_cache_db()
        count = len(db["entries"])
        
        # 删除所有文件
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json.gz'):
                os.remove(os.path.join(self.cache_dir, file))
        
        # 重置数据库
        db["entries"] = {}
        db["stats"] = {"hits": 0, "misses": 0, "size": 0}
        self._save_cache_db(db)
        
        return count
    
    def get_stats(self):
        """获取缓存统计"""
        db = self._load_cache_db()
        stats = db.get("stats", {})
        
        total = stats.get("hits", 0) + stats.get("misses", 0)
        hit_rate = stats.get("hits", 0) / total * 100 if total > 0 else 0
        
        # 计算总大小
        total_size = sum(
            entry.get("size", 0) for entry in db.get("entries", {}).values()
        )
        
        return {
            "hits": stats.get("hits", 0),
            "misses": stats.get("misses", 0),
            "total_requests": total,
            "hit_rate": hit_rate,
            "cached_entries": len(db.get("entries", {})),
            "total_size_kb": total_size / 1024
        }

def generate_report(stats, deleted):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 💾 结果缓存报告

**生成时间:** {timestamp}

## 缓存统计

| 指标 | 值 |
|------|-----|
| 总请求数 | {stats['total_requests']} |
| 命中数 | {stats['hits']} |
| 未命中数 | {stats['misses']} |
| 命中率 | {stats['hit_rate']:.1f}% |
| 缓存条目数 | {stats['cached_entries']} |
| 总大小 | {stats['total_size_kb']:.1f}KB |

## 清理结果

"""
    
    if deleted:
        report += f"已删除 {len(deleted)} 个过期缓存:\n\n"
        report += "| 工具 ID | 缓存时间 | 年龄 (小时) |\n"
        report += "|--------|----------|-------------|\n"
        
        for item in deleted[:10]:
            tool_id = item.get('tool_id', 'unknown')
            age = item.get('age_hours', 0)
            report += f"| {tool_id} | {item['key'][:8]}... | {age:.1f} |\n"
        
        report += "\n"
    else:
        report += "没有需要清理的过期缓存。\n\n"
    
    report += f"""## 性能提升

"""
    
    hit_rate = stats['hit_rate']
    if hit_rate >= 80:
        report += "✅ **优秀!** 缓存命中率很高\n"
    elif hit_rate >= 50:
        report += "✅ **良好** 有明显的性能提升\n"
    elif hit_rate >= 20:
        report += "⚠️ **一般** 有一定的缓存效果\n"
    else:
        report += "⚠️ **待优化** 缓存命中率较低\n"
    
    report += f"""
## 使用说明

### 获取缓存
```bash
py result_cache.py --get --tool <tool_id> --params '{{"key": "value"}}'
```

### 设置缓存
```bash
py result_cache.py --set --tool <tool_id> --result '{{"output": "data"}}'
```

### 清理过期
```bash
py result_cache.py --clear-expired
```

### 清空所有
```bash
py result_cache.py --clear-all
```

### 查看统计
```bash
py result_cache.py --stats
```

---

*本报告由 result_cache.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Result Cache v1.0 - 结果缓存")
    print("=" * 60)
    
    cache = ResultCache(default_ttl_hours=24)
    
    # 演示缓存操作
    print(f"\n[1/5] 演示缓存设置...")
    
    # 设置一些缓存
    test_cases = [
        ("tool_a", {"param": "value1"}, {"result": "data1"}),
        ("tool_b", {"param": "value2"}, {"result": "data2"}),
        ("tool_a", {"param": "value3"}, {"result": "data3"}),
    ]
    
    for tool_id, params, result in test_cases:
        cache.set(tool_id, params, result, ttl_hours=24)
        print(f"  ✅ 缓存：{tool_id}")
    
    # 测试缓存命中
    print(f"\n[2/5] 测试缓存命中...")
    for tool_id, params, _ in test_cases[:2]:
        result = cache.get(tool_id, params)
        status = "命中" if result['hit'] else "未命中"
        print(f"  {status}: {tool_id}")
    
    # 获取统计
    print(f"\n[3/5] 获取缓存统计...")
    stats = cache.get_stats()
    print(f"✅ 命中率：{stats['hit_rate']:.1f}%, 条目数：{stats['cached_entries']}")
    
    # 清理过期
    print(f"\n[4/5] 清理过期缓存...")
    deleted = cache.clear_expired()
    print(f"✅ 删除了 {len(deleted)} 个过期缓存")
    
    # 生成报告
    print(f"\n[5/5] 生成报告...")
    report = generate_report(stats, deleted)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"result_cache_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    
    print("\n" + "=" * 60)
    print("✅ 结果缓存就绪!")
    print("=" * 60)

if __name__ == '__main__':
    main()
