#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Cache System - 智能缓存机制

功能:
1. 工具执行结果缓存
2. 智能缓存失效策略
3. 缓存命中率统计
4. 缓存清理机制
5. 缓存压缩存储

Usage:
    py workflow_cache.py --enable              # 启用缓存
    py workflow_cache.py --disable             # 禁用缓存
    py workflow_cache.py --stats               # 查看统计
    py workflow_cache.py --clear               # 清空缓存
    py workflow_cache.py --clean               # 清理过期缓存
    py workflow_cache.py --status              # 查看状态
"""

import sys
import io
import json
import hashlib
import time
import gzip
import pickle
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
CACHE_DIR = WORKSPACE / "cache"
CACHE_DB = CACHE_DIR / "cache-db.json"
CACHE_CONFIG = CACHE_DIR / "cache-config.json"
CACHE_STATS = CACHE_DIR / "cache-stats.json"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def init_cache():
    """初始化缓存目录"""
    CACHE_DIR.mkdir(exist_ok=True)
    
    if not CACHE_DB.exists():
        save_cache_db({})
    
    if not CACHE_CONFIG.exists():
        default_config = {
            "enabled": True,
            "default_ttl": 3600,           # 默认 TTL: 1 小时
            "max_size_mb": 100,            # 最大缓存大小：100MB
            "compression_enabled": True,   # 启用压缩
            "auto_clean": True,            # 自动清理
            "compression_threshold": 1024  # 压缩阈值：1KB
        }
        save_config(default_config)
    
    if not CACHE_STATS.exists():
        save_stats({
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "cache_size_mb": 0,
            "entries_count": 0
        })

def load_cache_db():
    """加载缓存数据库"""
    if not CACHE_DB.exists():
        return {}
    
    with open(CACHE_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cache_db(db):
    """保存缓存数据库"""
    with open(CACHE_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_config():
    """加载配置"""
    if not CACHE_CONFIG.exists():
        return {
            "enabled": True,
            "default_ttl": 3600,
            "max_size_mb": 100,
            "compression_enabled": True,
            "auto_clean": True,
            "compression_threshold": 1024
        }
    
    with open(CACHE_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置"""
    with open(CACHE_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_stats():
    """加载统计"""
    if not CACHE_STATS.exists():
        return {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "cache_size_mb": 0,
            "entries_count": 0
        }
    
    with open(CACHE_STATS, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_stats(stats):
    """保存统计"""
    with open(CACHE_STATS, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

def generate_key(tool_id, params):
    """生成缓存键"""
    key_data = {
        "tool_id": tool_id,
        "params": params
    }
    key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(key_str.encode()).hexdigest()

def compress_data(data):
    """压缩数据"""
    config = load_config()
    if not config.get("compression_enabled", True):
        return data, False
    
    # 序列化
    serialized = pickle.dumps(data)
    
    # 检查是否需要压缩
    if len(serialized) < config.get("compression_threshold", 1024):
        return data, False
    
    # 压缩
    compressed = gzip.compress(serialized)
    return compressed, True

def decompress_data(data, is_compressed):
    """解压数据"""
    if not is_compressed:
        return data
    
    decompressed = gzip.decompress(data)
    return pickle.loads(decompressed)

def cache_get(tool_id, params):
    """从缓存获取"""
    config = load_config()
    
    if not config.get("enabled", True):
        return None, "cache_disabled"
    
    init_cache()
    
    key = generate_key(tool_id, params)
    db = load_cache_db()
    
    if key not in db:
        update_stats("miss")
        return None, "miss"
    
    entry = db[key]
    
    # 检查是否过期
    created_at = datetime.fromisoformat(entry["created_at"])
    ttl = entry.get("ttl", config.get("default_ttl", 3600))
    
    if datetime.now() - created_at > timedelta(seconds=ttl):
        # 过期，删除
        del db[key]
        save_cache_db(db)
        update_stats("miss")
        return None, "expired"
    
    # 解压数据
    data = decompress_data(entry["data"], entry.get("compressed", False))
    
    update_stats("hit")
    return data, "hit"

def cache_set(tool_id, params, result, ttl=None):
    """设置缓存"""
    config = load_config()
    
    if not config.get("enabled", True):
        return False, "cache_disabled"
    
    init_cache()
    
    key = generate_key(tool_id, params)
    db = load_cache_db()
    
    # 压缩数据
    compressed_data, is_compressed = compress_data(result)
    
    # 创建缓存条目
    entry = {
        "key": key,
        "tool_id": tool_id,
        "params": params,
        "data": compressed_data if is_compressed else result,
        "compressed": is_compressed,
        "created_at": datetime.now().isoformat(),
        "ttl": ttl or config.get("default_ttl", 3600),
        "size_bytes": len(compressed_data) if is_compressed else len(str(result))
    }
    
    db[key] = entry
    save_cache_db(db)
    
    # 更新统计
    update_stats("set", entry["size_bytes"])
    
    # 检查是否需要清理
    if config.get("auto_clean", True):
        clean_expired()
    
    return True, "cached"

def update_stats(event, size_bytes=0):
    """更新统计"""
    stats = load_stats()
    
    stats["total_requests"] = stats.get("total_requests", 0) + 1
    
    if event == "hit":
        stats["hits"] = stats.get("hits", 0) + 1
    elif event == "miss":
        stats["misses"] = stats.get("misses", 0) + 1
    elif event == "set":
        stats["cache_size_mb"] = stats.get("cache_size_mb", 0) + (size_bytes / 1024 / 1024)
        stats["entries_count"] = stats.get("entries_count", 0) + 1
    
    # 计算命中率
    if stats["total_requests"] > 0:
        stats["hit_rate"] = (stats["hits"] / stats["total_requests"]) * 100
    else:
        stats["hit_rate"] = 0
    
    save_stats(stats)

def cache_clear():
    """清空缓存"""
    save_cache_db({})
    save_stats({
        "hits": 0,
        "misses": 0,
        "total_requests": 0,
        "cache_size_mb": 0,
        "entries_count": 0
    })
    return True

def clean_expired():
    """清理过期缓存"""
    config = load_config()
    db = load_cache_db()
    
    expired_keys = []
    
    for key, entry in db.items():
        created_at = datetime.fromisoformat(entry["created_at"])
        ttl = entry.get("ttl", config.get("default_ttl", 3600))
        
        if datetime.now() - created_at > timedelta(seconds=ttl):
            expired_keys.append(key)
    
    for key in expired_keys:
        del db[key]
    
    if expired_keys:
        save_cache_db(db)
    
    return len(expired_keys)

def clean_old_entries():
    """清理旧条目（当缓存过大时）"""
    config = load_config()
    db = load_cache_db()
    
    max_size = config.get("max_size_mb", 100) * 1024 * 1024  # 转换为字节
    
    # 计算当前大小
    total_size = sum(entry.get("size_bytes", 0) for entry in db.values())
    
    if total_size <= max_size:
        return 0
    
    # 按创建时间排序，删除最旧的
    sorted_entries = sorted(db.items(), key=lambda x: x[1]["created_at"])
    
    removed = 0
    for key, entry in sorted_entries:
        if total_size <= max_size * 0.8:  # 清理到 80%
            break
        
        total_size -= entry.get("size_bytes", 0)
        del db[key]
        removed += 1
    
    save_cache_db(db)
    return removed

def show_stats():
    """显示统计"""
    stats = load_stats()
    config = load_config()
    db = load_cache_db()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}缓存统计{Colors.RESET}")
    print("=" * 70)
    
    print(f"缓存状态：{Colors.GREEN}启用{Colors.RESET}" if config.get("enabled") else f"缓存状态：{Colors.RED}禁用{Colors.RESET}")
    print(f"总请求数：{stats.get('total_requests', 0)}")
    print(f"命中数：{Colors.GREEN}{stats.get('hits', 0)}{Colors.RESET}")
    print(f"未命中数：{Colors.YELLOW}{stats.get('misses', 0)}{Colors.RESET}")
    print(f"命中率：{Colors.GREEN}{stats.get('hit_rate', 0):.2f}%{Colors.RESET}")
    print(f"缓存大小：{stats.get('cache_size_mb', 0):.2f} MB")
    print(f"条目数量：{len(db)}")
    print(f"最大大小：{config.get('max_size_mb', 100)} MB")
    print(f"默认 TTL: {config.get('default_ttl', 3600)}秒")
    print(f"压缩：{Colors.GREEN}启用{Colors.RESET}" if config.get('compression_enabled') else f"压缩：{Colors.YELLOW}禁用{Colors.RESET}")
    
    print("=" * 70)

def show_status():
    """显示状态"""
    config = load_config()
    db = load_cache_db()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}缓存状态{Colors.RESET}")
    print("=" * 70)
    
    print(f"缓存目录：{CACHE_DIR}")
    print(f"缓存启用：{config.get('enabled', True)}")
    print(f"默认 TTL: {config.get('default_ttl', 3600)}秒")
    print(f"最大大小：{config.get('max_size_mb', 100)} MB")
    print(f"压缩启用：{config.get('compression_enabled', True)}")
    print(f"自动清理：{config.get('auto_clean', True)}")
    print(f"当前条目：{len(db)}")
    
    # 显示最近 5 个缓存
    if db:
        print(f"\n最近缓存:")
        sorted_items = sorted(db.items(), key=lambda x: x[1]["created_at"], reverse=True)[:5]
        for key, entry in sorted_items:
            tool_id = entry.get("tool_id", "unknown")
            created = entry.get("created_at", "unknown")[:19]
            size = entry.get("size_bytes", 0) / 1024
            compressed = "🗜️" if entry.get("compressed") else ""
            print(f"  {compressed} [{tool_id}] {created} ({size:.2f} KB)")
    
    print("=" * 70)

def enable_cache():
    """启用缓存"""
    config = load_config()
    config["enabled"] = True
    save_config(config)
    print(f"{Colors.GREEN}✅ 缓存已启用{Colors.RESET}")

def disable_cache():
    """禁用缓存"""
    config = load_config()
    config["enabled"] = False
    save_config(config)
    print(f"{Colors.YELLOW}⚠️ 缓存已禁用{Colors.RESET}")

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}缓存管理菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 查看统计")
        print("2. 查看状态")
        print("3. 启用缓存")
        print("4. 禁用缓存")
        print("5. 清空缓存")
        print("6. 清理过期缓存")
        print("7. 配置参数")
        print("8. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-8): ").strip()
        
        if choice == '1':
            show_stats()
        elif choice == '2':
            show_status()
        elif choice == '3':
            enable_cache()
        elif choice == '4':
            disable_cache()
        elif choice == '5':
            if input("确定清空缓存？(y/n): ").strip().lower() == 'y':
                cache_clear()
                print(f"{Colors.GREEN}✅ 缓存已清空{Colors.RESET}")
        elif choice == '6':
            removed = clean_expired()
            print(f"{Colors.GREEN}✅ 清理了{removed}个过期条目{Colors.RESET}")
        elif choice == '7':
            config = load_config()
            print(f"\n当前配置:")
            print(f"  启用：{config['enabled']}")
            print(f"  默认 TTL: {config['default_ttl']}秒")
            print(f"  最大大小：{config['max_size_mb']} MB")
            print(f"  压缩：{config['compression_enabled']}")
            new_ttl = input("新的 TTL (秒，回车保持): ").strip()
            if new_ttl.isdigit():
                config['default_ttl'] = int(new_ttl)
                save_config(config)
                print(f"{Colors.GREEN}✅ 配置已更新{Colors.RESET}")
        elif choice == '8':
            print("退出")
            break
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Cache System - 智能缓存机制')
    parser.add_argument('--enable', action='store_true', help='启用缓存')
    parser.add_argument('--disable', action='store_true', help='禁用缓存')
    parser.add_argument('--stats', action='store_true', help='查看统计')
    parser.add_argument('--clear', action='store_true', help='清空缓存')
    parser.add_argument('--clean', action='store_true', help='清理过期缓存')
    parser.add_argument('--status', action='store_true', help='查看状态')
    
    args = parser.parse_args()
    
    init_cache()
    
    if args.enable:
        enable_cache()
    elif args.disable:
        disable_cache()
    elif args.stats:
        show_stats()
    elif args.clear:
        cache_clear()
        print(f"{Colors.GREEN}✅ 缓存已清空{Colors.RESET}")
    elif args.clean:
        removed = clean_expired()
        print(f"{Colors.GREEN}✅ 清理了{removed}个过期条目{Colors.RESET}")
    elif args.status:
        show_status()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
