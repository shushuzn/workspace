# Quick Start - 双层记忆系统演示
# 运行: py memory/quickstart.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory import DualLayerMemory

def main():
    print("=" * 50)
    print("Dual-layer Memory Quick Start Demo")
    print("=" * 50)
    
    # 初始化
    memory = DualLayerMemory(token_budget=5000)
    
    # 1. 添加各种类型的记忆
    print("\n[1] Adding memories...")
    
    memories = [
        ("我更喜欢简洁的代码风格", "preference"),
        ("决定使用向量数据库方案", "decision"),
        ("今天天气不错", "conversation"),
        ("Python是一种解释型语言", "fact"),
        ("项目A正在进行中", "project"),
    ]
    
    for content, mtype in memories:
        item = memory.add(content, mtype)
        print(f"  - {mtype}: {content[:30]}... (importance: {item.importance:.2f})")
    
    # 2. 查看上下文
    print("\n[2] Current context:")
    context = memory.get_context()
    print(f"  Total items: {len(context)}")
    
    # 3. 查看统计
    print("\n[3] Statistics:")
    stats = memory.get_stats()
    print(f"  Working memory: {stats['working_count']} items")
    print(f"  Token budget: {stats['token_budget']}")
    
    # 4. 搜索
    print("\n[4] Search for '代码':")
    results = memory.search("代码")
    for r in results:
        print(f"  - {r.content[:40]}... (type: {r.type})")
    
    # 5. 跨Session桥接
    print("\n[5] Bridge to new session:")
    essential = memory.bridge_to("new_session_001")
    print(f"  Exported: {essential['stats']['total_exported']} items")
    print(f"  Preferences: {essential['stats']['preference_count']}")
    print(f"  Decisions: {essential['stats']['decision_count']}")
    
    # 6. 压缩
    print("\n[6] Compress:")
    result = memory.compress()
    print(f"  Result: {result}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()