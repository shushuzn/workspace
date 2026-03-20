#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动记忆蒸馏器 - 定期自动提炼 MEMORY.md
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class AutoMemoryDistiller:
    """自动记忆蒸馏器"""
    
    def __init__(self):
        self.memory_file = Path("13-memory/MEMORY.md")
        self.daily_dir = Path("13-memory")
        self.distill_log = Path("13-memory/distillation-log.json")
    
    def load_daily_notes(self, days: int = 7) -> List[Dict]:
        """加载最近 N 天的日常笔记"""
        notes = []
        
        for i in range(days):
            date = datetime.now()
            date_str = date.strftime("%Y-%m-%d")
            
            daily_file = self.daily_dir / f"{date_str}.md"
            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    notes.append({
                        "date": date_str,
                        "content": content,
                        "file": str(daily_file)
                    })
        
        return notes
    
    def extract_key_events(self, content: str) -> List[str]:
        """提取关键事件"""
        events = []
        
        # 简单启发式：提取包含关键词的行
        keywords = ["Completed", "Created", "Fixed", "Implemented", "Achieved", "Git:", "Tool"]
        
        for line in content.split('\n'):
            line = line.strip()
            if any(kw in line for kw in keywords) and len(line) > 20:
                events.append(line)
        
        return events[:10]  # 最多 10 个事件
    
    def distill_to_memory(self, daily_notes: List[Dict]) -> Dict:
        """蒸馏到 MEMORY.md"""
        
        all_events = []
        for note in daily_notes:
            events = self.extract_key_events(note['content'])
            for event in events:
                all_events.append({
                    "date": note['date'],
                    "event": event
                })
        
        # 去重
        seen = set()
        unique_events = []
        for event in all_events:
            key = f"{event['date']}:{event['event']}"
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return {
            "distilled_at": datetime.now().isoformat(),
            "source_days": len(daily_notes),
            "total_events": len(all_events),
            "unique_events": len(unique_events),
            "events": unique_events
        }
    
    def update_memory_md(self, distilled: Dict) -> bool:
        """更新 MEMORY.md"""
        
        # 读取现有 MEMORY.md
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        else:
            existing_content = "# MEMORY.md - Long-term Memory\n\n"
        
        # 生成新内容
        new_section = f"\n## {distilled['distilled_at'].split('T')[0]} Auto-Distillation\n\n"
        new_section += f"**Source:** {distilled['source_days']} days of daily notes\n"
        new_section += f"**Events:** {distilled['unique_events']} unique events extracted\n\n"
        
        for event in distilled['events'][:20]:  # 最多 20 个事件
            new_section += f"- [{event['date']}] {event['event']}\n"
        
        new_section += "\n---\n"
        
        # 追加到 MEMORY.md
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write(existing_content + new_section)
        
        return True
    
    def get_stats(self) -> Dict:
        """获取统计"""
        # 读取蒸馏日志
        log = []
        if self.distill_log.exists():
            with open(self.distill_log, 'r', encoding='utf-8') as f:
                log = json.load(f)
        
        return {
            "total_distillations": len(log),
            "last_distillation": log[-1]['distilled_at'] if log else None,
            "avg_events_per_distillation": (
                sum(d.get('unique_events', 0) for d in log) / len(log)
            ) if log else 0
        }
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Auto Memory Distiller")
        output.append("=" * 70)
        
        output.append(f"\n[Stats]")
        output.append(f"  Total Distillations:  {stats['total_distillations']}")
        output.append(f"  Last Distillation:    {stats['last_distillation'] or 'Never'}")
        output.append(f"  Avg Events/Session:   {stats['avg_events_per_distillation']:.1f}")
        
        output.append(f"\n[Next Scheduled]")
        output.append(f"  Daily at 06:00 (via cron)")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)
    
    def run(self, days: int = 7) -> Dict:
        """运行蒸馏"""
        daily_notes = self.load_daily_notes(days)
        distilled = self.distill_to_memory(daily_notes)
        self.update_memory_md(distilled)
        
        # 记录日志
        log = []
        if self.distill_log.exists():
            with open(self.distill_log, 'r', encoding='utf-8') as f:
                log = json.load(f)
        log.append(distilled)
        log = log[-100:]  # 保留最近 100 次
        with open(self.distill_log, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        
        return {
            "distilled": distilled,
            "success": True
        }

def main():
    """测试入口"""
    distiller = AutoMemoryDistiller()
    
    print("Auto Memory Distiller Test")
    print("=" * 70)
    
    # 运行蒸馏
    result = distiller.run(days=1)
    print(f"\n[OK] Distilled {result['distilled']['unique_events']} events from {result['distilled']['source_days']} days")
    
    # 显示状态
    print(distiller.display_status())
    
    print(f"\n[OK] Distiller test completed")

if __name__ == "__main__":
    main()
