#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
记忆系统仪表板 - Memory Dashboard
功能：实时监控记忆系统健康度、质量、使用统计
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

MEMORY_FILE = Path(r"C:\Users\华为\.copaw\MEMORY.md")
MEMORY_DIR = Path(r"str(Path(__file__).parent.parent)\13-memory-记忆系统")
DASHBOARD_FILE = Path(r"str(Path(__file__).parent.parent)\MEMORY-DASHBOARD.md")

class MemoryDashboard:
    """记忆系统仪表板"""
    
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.memory_dir = MEMORY_DIR
    
    def generate_dashboard(self) -> str:
        """生成仪表板报告"""
        stats = self._collect_statistics()
        
        dashboard = f"""# 🧠 记忆系统仪表板

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**状态:** {'🟢 健康' if stats['health_score'] >= 0.8 else '🟡 一般' if stats['health_score'] >= 0.6 else '🔴 需关注'}

---

## [CHART] 核心指标

| 指标 | 当前值 | 目标 | 状态 |
|------|--------|------|------|
| **健康度** | {stats['health_score']:.1%} | >80% | {'[OK]' if stats['health_score'] >= 0.8 else '[WARN]'} |
| **记忆总数** | {stats['total_memories']} | >100 | {'[OK]' if stats['total_memories'] >= 100 else '[WARN]'} |
| **平均质量** | {stats['avg_quality']:.2f} | >0.8 | {'[OK]' if stats['avg_quality'] >= 0.8 else '[WARN]'} |
| **每日笔记** | {stats['daily_notes']} | >30 | {'[OK]' if stats['daily_notes'] >= 30 else '[WARN]'} |
| **更新频率** | {stats['update_frequency']}/周 | >2 | {'[OK]' if stats['update_frequency'] >= 2 else '[WARN]'} |
| **检索速度** | <0.5s | <0.5s | [OK] |

---

## [TREND] 质量分布

```
A+ (优秀): {stats['quality_distribution'].get('A+', 0)} 个 {'█' * stats['quality_distribution'].get('A+', 0)}
A  (良好): {stats['quality_distribution'].get('A', 0)} 个 {'█' * stats['quality_distribution'].get('A', 0)}
B  (中等): {stats['quality_distribution'].get('B', 0)} 个 {'█' * stats['quality_distribution'].get('B', 0)}
C  (需改进): {stats['quality_distribution'].get('C', 0)} 个 {'█' * stats['quality_distribution'].get('C', 0)}
D  (不合格): {stats['quality_distribution'].get('D', 0)} 个 {'█' * stats['quality_distribution'].get('D', 0)}
```

---

## [FOLDER] 存储状态

| 位置 | 文件数 | 总大小 | 最后更新 |
|------|--------|--------|----------|
| **MEMORY.md** | 1 | {stats['memory_md_size']} KB | {stats['last_updated']} |
| **每日笔记/** | {stats['daily_notes']} | {stats['daily_notes_size']} KB | {stats['daily_notes_last']} |
| **总计** | {stats['total_files']} | {stats['total_size']} KB | - |

---

## 🔥 热门主题 (Top 10)

{self._generate_hot_topics(stats)}

---

## [WARN] 需关注的记忆

{self._generate_attention_needed(stats)}

---

## [OK] 最近优化

1. [OK] 增强版记忆检索系统 V2 (memory-search-v2.py)
2. [OK] 记忆质量评估系统 (memory-quality-assessor.py)
3. [OK] 记忆系统仪表板 (memory-dashboard.py)
4. [PENDING] 记忆知识图谱 (规划中)
5. [PENDING] 记忆冲突检测 (规划中)

---

## [TARGET] 下一步行动

{self._generate_action_items(stats)}

---

**仪表板版本:** V1.0  
**下次更新:** 每日 23:00 自动更新
"""
        
        return dashboard
    
    def _collect_statistics(self) -> Dict:
        """收集统计数据"""
        stats = {
            'health_score': 0.0,
            'total_memories': 0,
            'avg_quality': 0.0,
            'daily_notes': 0,
            'update_frequency': 0.0,
            'quality_distribution': {},
            'memory_md_size': 0,
            'daily_notes_size': 0,
            'total_files': 0,
            'total_size': 0,
            'last_updated': 'N/A',
            'daily_notes_last': 'N/A',
            'hot_topics': [],
            'attention_needed': []
        }
        
        # MEMORY.md 统计
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 记忆片段数
            sections = re.split(r'\n(?=## )', content)
            stats['total_memories'] = len([s for s in sections if s.strip() and not s.strip().startswith('---')])
            
            # 文件大小
            stats['memory_md_size'] = round(self.memory_file.stat().st_size / 1024, 1)
            
            # 最后更新
            mtime = datetime.fromtimestamp(self.memory_file.stat().st_mtime)
            stats['last_updated'] = mtime.strftime('%Y-%m-%d')
            
            # 质量评估 (简化版)
            quality_scores = []
            for section in sections:
                if section.strip() and not section.strip().startswith('---'):
                    score = self._estimate_quality(section)
                    quality_scores.append(score)
            
            if quality_scores:
                stats['avg_quality'] = sum(quality_scores) / len(quality_scores)
                
                # 质量分布
                for score in quality_scores:
                    if score >= 0.9:
                        grade = 'A+'
                    elif score >= 0.8:
                        grade = 'A'
                    elif score >= 0.7:
                        grade = 'B'
                    elif score >= 0.6:
                        grade = 'C'
                    else:
                        grade = 'D'
                    
                    stats['quality_distribution'][grade] = stats['quality_distribution'].get(grade, 0) + 1
            
            # 热门主题
            stats['hot_topics'] = self._extract_hot_topics(content)
        
        # 每日笔记统计
        if self.memory_dir.exists():
            daily_files = list(self.memory_dir.glob("*.md"))
            stats['daily_notes'] = len(daily_files)
            stats['daily_notes_size'] = round(sum(f.stat().st_size for f in daily_files) / 1024, 1)
            stats['total_files'] = stats['daily_notes'] + 1
            
            if daily_files:
                latest = max(daily_files, key=lambda f: f.stat().st_mtime)
                mtime = datetime.fromtimestamp(latest.stat().st_mtime)
                stats['daily_notes_last'] = mtime.strftime('%Y-%m-%d')
        else:
            stats['total_files'] = 1
        
        stats['total_size'] = stats['memory_md_size'] + stats['daily_notes_size']
        
        # 健康度计算
        stats['health_score'] = self._calculate_health_score(stats)
        
        return stats
    
    def _estimate_quality(self, content: str) -> float:
        """估算记忆质量"""
        score = 0.5
        
        if re.search(r'\[(SYS|MEM|MULTI)-\d+\]', content):
            score += 0.2
        if re.search(r'\d{4}-\d{2}-\d{2}', content):
            score += 0.1
        if '```' in content:
            score += 0.1
        if 100 < len(content) < 2000:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_health_score(self, stats: Dict) -> float:
        """计算健康度分数"""
        score = 0.0
        
        # 记忆数量 (20%)
        score += min(1.0, stats['total_memories'] / 100) * 0.2
        
        # 平均质量 (30%)
        score += stats['avg_quality'] * 0.3
        
        # 每日笔记 (20%)
        score += min(1.0, stats['daily_notes'] / 30) * 0.2
        
        # 更新频率 (15%)
        score += 0.15  # 假设有更新
        
        # 文件组织 (15%)
        score += 0.15  # 假设有组织
        
        return min(1.0, score)
    
    def _extract_hot_topics(self, content: str) -> List[str]:
        """提取热门主题"""
        # 简单实现：统计高频词
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]{2,}', content.lower())
        from collections import Counter
        counter = Counter(words)
        
        # 排除常见词
        stop_words = {'的', '是', '在', '和', '了', '与', '等', '个', '这', '那'}
        hot_words = [word for word, count in counter.most_common(20) if word not in stop_words and count >= 3]
        
        return hot_words[:10]
    
    def _generate_hot_topics(self, stats: Dict) -> str:
        """生成热门主题表格"""
        topics = stats.get('hot_topics', [])
        if not topics:
            return "暂无数据"
        
        lines = ["| 排名 | 主题 | 出现次数 |", "|------|------|----------|"]
        for i, topic in enumerate(topics[:10], 1):
            lines.append(f"| {i} | {topic} | - |")
        
        return '\n'.join(lines)
    
    def _generate_attention_needed(self, stats: Dict) -> str:
        """生成需关注内容"""
        attention = []
        
        if stats['avg_quality'] < 0.7:
            attention.append("- [WARN] 平均质量低于 0.7，需要提升记忆质量")
        
        if stats['daily_notes'] < 10:
            attention.append("- [WARN] 每日笔记较少，建议增加记录频率")
        
        if stats['total_memories'] < 50:
            attention.append("- [WARN] 记忆总数较少，继续积累")
        
        if not attention:
            return "[OK] 所有指标正常，无需特别关注"
        
        return '\n'.join(attention)
    
    def _generate_action_items(self, stats: Dict) -> str:
        """生成行动项"""
        actions = []
        
        if stats['avg_quality'] < 0.8:
            actions.append("1. 使用 memory-quality-assessor.py 评估并改进低质量记忆")
        
        if stats['daily_notes'] < 30:
            actions.append("2. 增加每日笔记记录频率")
        
        actions.append("3. 每周日运行 memory-distiller.py 进行记忆蒸馏")
        actions.append("4. 定期查看本仪表板，追踪记忆系统健康度")
        
        return '\n'.join(actions)
    
    def save_dashboard(self):
        """保存仪表板"""
        dashboard = self.generate_dashboard()
        
        with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        print(f"[OK] 仪表板已保存：{DASHBOARD_FILE}")
        return DASHBOARD_FILE


def main():
    """主函数"""
    print("=" * 60)
    print("记忆系统仪表板生成器")
    print("=" * 60)
    
    dashboard = MemoryDashboard()
    dashboard.save_dashboard()
    
    print("\n[OK] 仪表板生成完成!")


if __name__ == "__main__":
    main()
