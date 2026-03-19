#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Persistence - 记忆持久化

将重要记忆永久保存到 MEMORY.md
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
MEMORY_DB = "13-memory\\memory-db.json"
MEMORY_FILE = "13-memory\\MEMORY.md"

class MemoryPersistence:
    """记忆持久化"""
    
    def __init__(self):
        self.memory_db_path = os.path.join(WORKSPACE, MEMORY_DB)
        self.memory_file_path = os.path.join(WORKSPACE, MEMORY_FILE)
    
    def load_memories(self):
        """加载记忆数据库"""
        if os.path.exists(self.memory_db_path):
            with open(self.memory_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"memories": [], "updated_at": None}
    
    def save_memories(self, data):
        """保存记忆数据库"""
        data["updated_at"] = datetime.now().isoformat()
        with open(self.memory_db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def select_important_memories(self, min_importance=0.7):
        """选择重要记忆"""
        data = self.load_memories()
        memories = data.get("memories", [])
        
        important = []
        for memory in memories:
            importance = memory.get("importance", 0.5)
            if importance >= min_importance:
                important.append(memory)
        
        return important
    
    def persist_to_memory_md(self, memories):
        """持久化到 MEMORY.md"""
        if not os.path.exists(self.memory_file_path):
            # 创建新文件
            content = "# 🧠 MEMORY.md - 长期记忆\n\n"
        else:
            with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # 添加新记忆
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_section = f"\n## {timestamp} 新增\n\n"
        
        for memory in memories:
            category = memory.get("category", "General")
            content_text = memory.get("content", "")
            tags = memory.get("tags", [])
            importance = memory.get("importance", 0.5)
            
            new_section += f"### [{category}] ⭐{importance:.1f}\n\n"
            new_section += f"{content_text}\n\n"
            
            if tags:
                new_section += f"**标签:** {', '.join(tags)}\n\n"
            
            new_section += "---\n\n"
        
        # 插入到文件末尾
        content += new_section
        
        # 保存
        with open(self.memory_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return len(memories)
    
    def mark_as_persisted(self, memories):
        """标记为已持久化"""
        data = self.load_memories()
        
        for memory in memories:
            memory_id = memory.get("id")
            for db_memory in data.get("memories", []):
                if db_memory.get("id") == memory_id:
                    db_memory["persisted"] = True
                    db_memory["persisted_at"] = datetime.now().isoformat()
        
        self.save_memories(data)

def generate_report(memories, persisted_count):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 🧠 记忆持久化报告

**生成时间:** {timestamp}

## 持久化概览

- **选择记忆数:** {len(memories)}
- **持久化数:** {persisted_count}
- **持久化率:** {persisted_count/len(memories)*100 if memories else 0:.1f}%

## 持久化详情

"""
    
    if memories:
        report += "| 类别 | 内容摘要 | 重要性 | 标签 |\n"
        report += "|------|----------|--------|------|\n"
        
        for memory in memories:
            category = memory.get("category", "General")
            content = memory.get("content", "")[:50] + "..." if len(memory.get("content", "")) > 50 else memory.get("content", "")
            importance = memory.get("importance", 0.5)
            tags = ", ".join(memory.get("tags", []))
            
            report += f"| {category} | {content} | ⭐{importance:.1f} | {tags} |\n"
        
        report += "\n"
    else:
        report += "没有需要持久化的记忆。\n\n"
    
    report += f"""## 使用说明

### 自动持久化
```bash
py memory_persistence.py --auto
```

### 手动持久化
```bash
py memory_persistence.py --persist --min-importance 0.7
```

### 查看已持久化
```bash
py memory_persistence.py --list
```

---

*本报告由 memory_persistence.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Memory Persistence v1.0 - 记忆持久化")
    print("=" * 60)
    
    persistence = MemoryPersistence()
    
    # 加载记忆
    print(f"\n[1/4] 加载记忆数据库...")
    data = persistence.load_memories()
    total_memories = len(data.get("memories", []))
    print(f"✅ 加载到 {total_memories} 个记忆")
    
    # 选择重要记忆
    print(f"\n[2/4] 选择重要记忆 (重要性≥0.7)...")
    important_memories = persistence.select_important_memories(min_importance=0.7)
    print(f"✅ 选择到 {len(important_memories)} 个重要记忆")
    
    # 持久化到 MEMORY.md
    print(f"\n[3/4] 持久化到 MEMORY.md...")
    persisted_count = persistence.persist_to_memory_md(important_memories)
    print(f"✅ 持久化了 {persisted_count} 个记忆")
    
    # 标记为已持久化
    print(f"\n[4/4] 标记为已持久化...")
    persistence.mark_as_persisted(important_memories)
    print(f"✅ 标记完成")
    
    # 生成报告
    print(f"\n生成报告...")
    report = generate_report(important_memories, persisted_count)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"memory_persist_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    
    print("\n" + "=" * 60)
    print("✅ 记忆持久化完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
