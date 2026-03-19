#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Long-Term Memory System - 长期记忆系统

功能:
1. 跨会话持久化记忆
2. 记忆检索和关联
3. 记忆分类和标签
4. 记忆压缩和蒸馏
5. 记忆查询 API

Usage:
    py long_term_memory.py --add "记忆内容" --tags "标签 1,标签 2"
    py long_term_memory.py --search "关键词"
    py long_term_memory.py --list [--category 类别]
    py long_term_memory.py --stats
    py long_term_memory.py --compress
    py long_term_memory.py --associate "记忆 ID"
"""

import sys
import io
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
MEMORY_DIR = WORKSPACE / "13-memory"
MEMORY_DB = MEMORY_DIR / "memory-db.json"
MEMORY_CONFIG = MEMORY_DIR / "memory-config.json"
MEMORY_INDEX = MEMORY_DIR / "memory-index.json"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

def init_memory():
    """初始化记忆系统"""
    MEMORY_DIR.mkdir(exist_ok=True)
    
    if not MEMORY_DB.exists():
        save_memory_db({
            "memories": [],
            "next_id": 1
        })
    
    if not MEMORY_CONFIG.exists():
        save_config({
            "auto_compress": True,
            "compress_threshold": 10,  # 超过 10 条同类记忆自动压缩
            "max_memories_per_category": 100,
            "enable_associations": True,
            "enable_tags": True
        })
    
    if not MEMORY_INDEX.exists():
        save_index({
            "by_category": {},
            "by_tag": {},
            "by_date": {}
        })

def load_memory_db():
    """加载记忆数据库"""
    if not MEMORY_DB.exists():
        return {"memories": [], "next_id": 1}
    
    with open(MEMORY_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_memory_db(db):
    """保存记忆数据库"""
    with open(MEMORY_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_config():
    """加载配置"""
    if not MEMORY_CONFIG.exists():
        return {
            "auto_compress": True,
            "compress_threshold": 10,
            "max_memories_per_category": 100,
            "enable_associations": True,
            "enable_tags": True
        }
    
    with open(MEMORY_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置"""
    with open(MEMORY_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_index():
    """加载索引"""
    if not MEMORY_INDEX.exists():
        return {
            "by_category": {},
            "by_tag": {},
            "by_date": {}
        }
    
    with open(MEMORY_INDEX, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_index(index):
    """保存索引"""
    with open(MEMORY_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

def generate_memory_id():
    """生成记忆 ID"""
    db = load_memory_db()
    memory_id = db["next_id"]
    db["next_id"] += 1
    save_memory_db(db)
    return f"MEM-{memory_id:04d}"

def add_memory(content: str, category: str = "general", tags: List[str] = None, 
               importance: int = 3, source: str = None):
    """添加记忆
    
    Args:
        content: 记忆内容
        category: 类别 (general/workflow/research/tool/personal)
        tags: 标签列表
        importance: 重要性 (1-5, 5 最重要)
        source: 来源 (会话 ID/文件名)
    """
    init_memory()
    config = load_config()
    
    if not config.get("enable_tags", True):
        tags = []
    
    memory_id = generate_memory_id()
    
    memory = {
        "id": memory_id,
        "content": content,
        "category": category,
        "tags": tags or [],
        "importance": importance,
        "source": source,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "access_count": 0,
        "associations": [],
        "compressed": False,
        "compressed_from": []
    }
    
    db = load_memory_db()
    db["memories"].append(memory)
    save_memory_db(db)
    
    # 更新索引
    update_index(memory, "add")
    
    print(f"{Colors.GREEN}✅ 记忆已添加{Colors.RESET}")
    print(f"   ID: {memory_id}")
    print(f"   类别：{category}")
    print(f"   标签：{', '.join(tags) if tags else '无'}")
    print(f"   重要性：{'⭐' * importance}")
    
    # 自动压缩检查
    if config.get("auto_compress", True):
        check_auto_compress(category)
    
    return memory_id

def update_index(memory: Dict, action: str):
    """更新索引"""
    index = load_index()
    
    # 按类别索引
    category = memory["category"]
    if category not in index["by_category"]:
        index["by_category"][category] = []
    
    if action == "add":
        if memory["id"] not in index["by_category"][category]:
            index["by_category"][category].append(memory["id"])
    elif action == "remove":
        if memory["id"] in index["by_category"][category]:
            index["by_category"][category].remove(memory["id"])
    
    # 按标签索引
    for tag in memory.get("tags", []):
        if tag not in index["by_tag"]:
            index["by_tag"][tag] = []
        
        if action == "add":
            if memory["id"] not in index["by_tag"][tag]:
                index["by_tag"][tag].append(memory["id"])
        elif action == "remove":
            if memory["id"] in index["by_tag"][tag]:
                index["by_tag"][tag].remove(memory["id"])
    
    # 按日期索引
    date = memory["created_at"][:10]  # YYYY-MM-DD
    if date not in index["by_date"]:
        index["by_date"][date] = []
    
    if action == "add":
        if memory["id"] not in index["by_date"][date]:
            index["by_date"][date].append(memory["id"])
    
    save_index(index)

def search_memories(query: str, category: str = None, limit: int = 10) -> List[Dict]:
    """搜索记忆
    
    Args:
        query: 搜索关键词
        category: 类别过滤
        limit: 返回数量限制
    
    Returns:
        匹配的记忆列表
    """
    init_memory()
    db = load_memory_db()
    
    results = []
    query_lower = query.lower()
    
    for memory in db["memories"]:
        # 类别过滤
        if category and memory["category"] != category:
            continue
        
        # 搜索内容、标签
        content_match = query_lower in memory["content"].lower()
        tag_match = any(query_lower in tag.lower() for tag in memory.get("tags", []))
        
        if content_match or tag_match:
            # 增加访问计数
            memory["access_count"] += 1
            results.append(memory)
    
    # 按重要性和访问次数排序
    results.sort(key=lambda x: (x["importance"], x["access_count"]), reverse=True)
    
    # 保存更新
    save_memory_db(db)
    
    return results[:limit]

def get_memory(memory_id: str) -> Optional[Dict]:
    """获取单条记忆"""
    init_memory()
    db = load_memory_db()
    
    for memory in db["memories"]:
        if memory["id"] == memory_id:
            memory["access_count"] += 1
            save_memory_db(db)
            return memory
    
    return None

def list_memories(category: str = None, limit: int = 20) -> List[Dict]:
    """列出记忆
    
    Args:
        category: 类别过滤
        limit: 返回数量限制
    
    Returns:
        记忆列表
    """
    init_memory()
    db = load_memory_db()
    
    memories = db["memories"]
    
    if category:
        memories = [m for m in memories if m["category"] == category]
    
    # 按创建时间倒序
    memories.sort(key=lambda x: x["created_at"], reverse=True)
    
    return memories[:limit]

def delete_memory(memory_id: str) -> bool:
    """删除记忆"""
    init_memory()
    db = load_memory_db()
    
    for i, memory in enumerate(db["memories"]):
        if memory["id"] == memory_id:
            # 更新索引
            update_index(memory, "remove")
            
            # 删除
            del db["memories"][i]
            save_memory_db(db)
            
            print(f"{Colors.GREEN}✅ 记忆已删除：{memory_id}{Colors.RESET}")
            return True
    
    print(f"{Colors.RED}❌ 未找到记忆：{memory_id}{Colors.RESET}")
    return False

def associate_memories(memory_id_1: str, memory_id_2: str, relation: str = "related"):
    """关联两条记忆"""
    init_memory()
    config = load_config()
    
    if not config.get("enable_associations", True):
        print(f"{Colors.YELLOW}⚠️ 关联功能已禁用{Colors.RESET}")
        return False
    
    db = load_memory_db()
    
    memory1 = None
    memory2 = None
    
    for memory in db["memories"]:
        if memory["id"] == memory_id_1:
            memory1 = memory
        if memory["id"] == memory_id_2:
            memory2 = memory
    
    if not memory1 or not memory2:
        print(f"{Colors.RED}❌ 未找到记忆{Colors.RESET}")
        return False
    
    # 添加关联
    association = {
        "target_id": memory_id_2,
        "relation": relation,
        "created_at": datetime.now().isoformat()
    }
    
    if memory_id_2 not in memory1["associations"]:
        memory1["associations"].append(association)
    
    # 反向关联
    reverse_association = {
        "target_id": memory_id_1,
        "relation": relation,
        "created_at": datetime.now().isoformat()
    }
    
    if memory_id_1 not in memory2["associations"]:
        memory2["associations"].append(reverse_association)
    
    save_memory_db(db)
    
    print(f"{Colors.GREEN}✅ 记忆已关联：{memory_id_1} ↔ {memory_id_2}{Colors.RESET}")
    print(f"   关系：{relation}")
    
    return True

def compress_memories(category: str = None) -> Dict:
    """压缩记忆
    
    将同类多条记忆压缩为一条摘要记忆
    
    Args:
        category: 类别，None 表示所有类别
    
    Returns:
        压缩统计
    """
    init_memory()
    db = load_memory_db()
    
    stats = {
        "compressed_count": 0,
        "new_memories": 0
    }
    
    # 按类别分组
    categories = {}
    for memory in db["memories"]:
        if memory["compressed"]:
            continue
        
        cat = memory["category"]
        if category and cat != category:
            continue
        
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(memory)
    
    # 压缩每个类别
    for cat, memories in categories.items():
        if len(memories) < 3:  # 至少 3 条才压缩
            continue
        
        # 按重要性排序
        memories.sort(key=lambda x: x["importance"], reverse=True)
        
        # 取前 5 条最重要的
        top_memories = memories[:5]
        
        # 创建压缩记忆
        compressed_content = f"【{cat} 类别记忆摘要】\n\n"
        compressed_content += f"包含 {len(memories)} 条记忆，以下是核心内容:\n\n"
        
        for i, m in enumerate(top_memories, 1):
            compressed_content += f"{i}. {m['content'][:200]}...\n"
        
        compressed_id = generate_memory_id()
        compressed_memory = {
            "id": compressed_id,
            "content": compressed_content,
            "category": cat,
            "tags": list(set(tag for m in memories for tag in m.get("tags", []))),
            "importance": 5,
            "source": "auto-compress",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0,
            "associations": [],
            "compressed": True,
            "compressed_from": [m["id"] for m in memories],
            "compression_summary": f"从{len(memories)}条记忆压缩"
        }
        
        db["memories"].append(compressed_memory)
        update_index(compressed_memory, "add")
        
        # 标记原记忆为已压缩
        for m in memories:
            m["compressed"] = True
        
        stats["compressed_count"] += len(memories)
        stats["new_memories"] += 1
        
        print(f"{Colors.GREEN}✅ 类别 '{cat}' 已压缩：{len(memories)}条 → 1 条摘要{Colors.RESET}")
    
    save_memory_db(db)
    
    return stats

def check_auto_compress(category: str):
    """检查是否需要自动压缩"""
    config = load_config()
    
    if not config.get("auto_compress", True):
        return
    
    db = load_memory_db()
    
    # 统计同类别记忆数量
    count = sum(1 for m in db["memories"] 
                if m["category"] == category and not m["compressed"])
    
    if count >= config.get("compress_threshold", 10):
        print(f"\n{Colors.YELLOW}⚠️ 类别 '{category}' 记忆过多 ({count}条)，建议压缩{Colors.RESET}")
        print(f"   运行：py long_term_memory.py --compress --category {category}")

def show_stats():
    """显示统计"""
    init_memory()
    db = load_memory_db()
    index = load_index()
    
    memories = db["memories"]
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}长期记忆系统统计{Colors.RESET}")
    print("=" * 70)
    
    # 总体统计
    total = len(memories)
    active = sum(1 for m in memories if not m["compressed"])
    compressed = sum(1 for m in memories if m["compressed"])
    
    print(f"总记忆数：{total}")
    print(f"活跃记忆：{Colors.GREEN}{active}{Colors.RESET}")
    print(f"已压缩：{Colors.YELLOW}{compressed}{Colors.RESET}")
    
    # 按类别统计
    print(f"\n按类别:")
    for category, ids in index["by_category"].items():
        count = len(ids)
        bar = "█" * min(count, 50)
        print(f"  {category:15} {count:3}条 {bar}")
    
    # 按标签统计
    print(f"\n热门标签:")
    sorted_tags = sorted(index["by_tag"].items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for tag, ids in sorted_tags:
        print(f"  #{tag:20} {len(ids)}条")
    
    # 访问统计
    print(f"\n最常访问:")
    sorted_by_access = sorted(memories, key=lambda x: x["access_count"], reverse=True)[:5]
    for m in sorted_by_access:
        print(f"  {m['id']}: {m['content'][:50]}... ({m['access_count']}次)")
    
    print("=" * 70)

def show_memory_detail(memory_id: str):
    """显示记忆详情"""
    memory = get_memory(memory_id)
    
    if not memory:
        print(f"{Colors.RED}❌ 未找到记忆：{memory_id}{Colors.RESET}")
        return
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}记忆详情：{memory_id}{Colors.RESET}")
    print("=" * 70)
    print(f"内容：{memory['content']}")
    print(f"类别：{memory['category']}")
    print(f"标签：{', '.join(memory.get('tags', []))}")
    print(f"重要性：{'⭐' * memory.get('importance', 3)}")
    print(f"创建时间：{memory['created_at'][:19]}")
    print(f"访问次数：{memory.get('access_count', 0)}")
    
    if memory.get('associations'):
        print(f"\n关联记忆:")
        for assoc in memory['associations']:
            print(f"  → {assoc['target_id']} ({assoc['relation']})")
    
    if memory.get('compressed_from'):
        print(f"\n压缩来源:")
        for mid in memory['compressed_from'][:5]:
            print(f"  ← {mid}")
        if len(memory['compressed_from']) > 5:
            print(f"  ... 还有{len(memory['compressed_from']) - 5}条")
    
    print("=" * 70)

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}长期记忆系统菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 添加记忆")
        print("2. 搜索记忆")
        print("3. 列出记忆")
        print("4. 查看记忆详情")
        print("5. 删除记忆")
        print("6. 关联记忆")
        print("7. 压缩记忆")
        print("8. 查看统计")
        print("9. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-9): ").strip()
        
        if choice == '1':
            content = input("记忆内容：").strip()
            category = input("类别 (general): ").strip() or "general"
            tags_str = input("标签 (逗号分隔): ").strip()
            tags = [t.strip() for t in tags_str.split(',')] if tags_str else []
            importance = int(input("重要性 (1-5, 默认 3): ").strip() or "3")
            
            add_memory(content, category, tags, importance)
        
        elif choice == '2':
            query = input("搜索关键词：").strip()
            results = search_memories(query)
            
            if results:
                print(f"\n找到 {len(results)} 条记忆:")
                for m in results:
                    print(f"  {m['id']}: {m['content'][:80]}...")
            else:
                print(f"{Colors.YELLOW}⚠️ 未找到匹配的记忆{Colors.RESET}")
        
        elif choice == '3':
            category = input("类别 (回车显示全部): ").strip() or None
            memories = list_memories(category)
            
            for m in memories:
                print(f"  {m['id']} [{m['category']}] {m['content'][:60]}...")
        
        elif choice == '4':
            memory_id = input("记忆 ID: ").strip()
            show_memory_detail(memory_id)
        
        elif choice == '5':
            memory_id = input("要删除的记忆 ID: ").strip()
            if input("确定删除？(y/n): ").strip().lower() == 'y':
                delete_memory(memory_id)
        
        elif choice == '6':
            id1 = input("记忆 ID 1: ").strip()
            id2 = input("记忆 ID 2: ").strip()
            relation = input("关系 (related): ").strip() or "related"
            associate_memories(id1, id2, relation)
        
        elif choice == '7':
            category = input("类别 (回车压缩所有): ").strip() or None
            stats = compress_memories(category)
            print(f"\n压缩完成:")
            print(f"  压缩记忆数：{stats['compressed_count']}")
            print(f"  生成摘要数：{stats['new_memories']}")
        
        elif choice == '8':
            show_stats()
        
        elif choice == '9':
            print("退出")
            break
        
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Long-Term Memory System - 长期记忆系统')
    parser.add_argument('--add', type=str, help='添加记忆内容')
    parser.add_argument('--tags', type=str, help='标签 (逗号分隔)')
    parser.add_argument('--category', type=str, default='general', help='类别')
    parser.add_argument('--importance', type=int, default=3, help='重要性 (1-5)')
    parser.add_argument('--search', type=str, help='搜索记忆')
    parser.add_argument('--list', action='store_true', help='列出记忆')
    parser.add_argument('--detail', type=str, help='查看记忆详情')
    parser.add_argument('--delete', type=str, help='删除记忆')
    parser.add_argument('--associate', type=str, nargs=2, help='关联记忆 (ID1 ID2)')
    parser.add_argument('--compress', action='store_true', help='压缩记忆')
    parser.add_argument('--stats', action='store_true', help='查看统计')
    
    args = parser.parse_args()
    
    init_memory()
    
    if args.add:
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
        add_memory(args.add, args.category, tags, args.importance)
    elif args.search:
        results = search_memories(args.search)
        if results:
            print(f"\n找到 {len(results)} 条记忆:")
            for m in results:
                print(f"  {m['id']}: {m['content'][:80]}...")
        else:
            print(f"{Colors.YELLOW}⚠️ 未找到匹配的记忆{Colors.RESET}")
    elif args.list:
        memories = list_memories(args.category if args.category != 'general' else None)
        for m in memories:
            print(f"  {m['id']} [{m['category']}] {m['content'][:60]}...")
    elif args.detail:
        show_memory_detail(args.detail)
    elif args.delete:
        delete_memory(args.delete)
    elif args.associate:
        associate_memories(args.associate[0], args.associate[1])
    elif args.compress:
        stats = compress_memories(args.category if args.category != 'general' else None)
        print(f"\n压缩完成：{stats['compressed_count']}条 → {stats['new_memories']}条摘要")
    elif args.stats:
        show_stats()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
