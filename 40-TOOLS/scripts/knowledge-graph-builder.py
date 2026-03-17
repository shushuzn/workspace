#!/usr/bin/env python3
"""
知识图谱构建器 - Knowledge Graph Builder
功能：自动构建教训知识图谱，发现知识关联
"""

import json
from typing import Dict, List, Set
from datetime import datetime

class KnowledgeGraphBuilder:
    """知识图谱构建器"""
    
    def __init__(self):
        self.entities = {}  # 知识实体
        self.relationships = []  # 关系
    
    def add_lesson(self, lesson: Dict):
        """添加教训到知识图谱"""
        lesson_id = lesson.get('id', 'UNKNOWN')
        
        # 创建实体
        entity = {
            'id': lesson_id,
            'type': 'lesson',
            'title': lesson.get('title', ''),
            'category': lesson.get('category', ''),
            'keywords': lesson.get('keywords', []),
            'confidence': lesson.get('confidence', 0.5),
            'created_at': lesson.get('created_at', datetime.now().strftime('%Y-%m-%d'))
        }
        
        self.entities[lesson_id] = entity
        
        # 基于关键词建立关系
        self._build_keyword_relationships(lesson_id, lesson.get('keywords', []))
        
        # 基于分类建立关系
        self._build_category_relationships(lesson_id, lesson.get('category', ''))
    
    def _build_keyword_relationships(self, lesson_id: str, keywords: List[str]):
        """基于关键词建立关系"""
        for keyword in keywords:
            # 查找有相同关键词的其他教训
            for other_id, other_entity in self.entities.items():
                if other_id != lesson_id and keyword in other_entity.get('keywords', []):
                    relationship = {
                        'from': lesson_id,
                        'to': other_id,
                        'type': 'shares_keyword',
                        'data': {'keyword': keyword}
                    }
                    
                    # 避免重复
                    if not self._relationship_exists(relationship):
                        self.relationships.append(relationship)
    
    def _build_category_relationships(self, lesson_id: str, category: str):
        """基于分类建立关系"""
        for other_id, other_entity in self.entities.items():
            if other_id != lesson_id and other_entity.get('category') == category:
                relationship = {
                    'from': lesson_id,
                    'to': other_id,
                    'type': 'same_category',
                    'data': {'category': category}
                }
                
                if not self._relationship_exists(relationship):
                    self.relationships.append(relationship)
    
    def _relationship_exists(self, relationship: Dict) -> bool:
        """检查关系是否已存在"""
        for rel in self.relationships:
            if (rel['from'] == relationship['from'] and rel['to'] == relationship['to'] and
                rel['type'] == relationship['type']):
                return True
            # 反向也视为存在
            if (rel['from'] == relationship['to'] and rel['to'] == relationship['from'] and
                rel['type'] == relationship['type']):
                return True
        return False
    
    def get_related_lessons(self, lesson_id: str, max_results: int = 5) -> List[Dict]:
        """获取相关教训"""
        related = []
        
        for rel in self.relationships:
            if rel['from'] == lesson_id:
                target_id = rel['to']
            elif rel['to'] == lesson_id:
                target_id = rel['from']
            else:
                continue
            
            if target_id in self.entities:
                target = self.entities[target_id]
                related.append({
                    'id': target['id'],
                    'title': target['title'],
                    'relationship_type': rel['type'],
                    'relationship_data': rel['data']
                })
        
        # 去重并限制数量
        seen = set()
        unique_related = []
        for item in related:
            if item['id'] not in seen:
                seen.add(item['id'])
                unique_related.append(item)
        
        return unique_related[:max_results]
    
    def get_knowledge_clusters(self) -> List[Dict]:
        """获取知识聚类"""
        clusters = {}
        
        # 按分类聚类
        for lesson_id, entity in self.entities.items():
            category = entity.get('category', 'UNKNOWN')
            if category not in clusters:
                clusters[category] = []
            clusters[category].append({
                'id': entity['id'],
                'title': entity['title'],
                'keywords': entity['keywords']
            })
        
        # 转换为列表
        cluster_list = []
        for category, lessons in clusters.items():
            cluster_list.append({
                'category': category,
                'lesson_count': len(lessons),
                'lessons': lessons
            })
        
        # 按数量排序
        cluster_list.sort(key=lambda x: x['lesson_count'], reverse=True)
        
        return cluster_list
    
    def get_statistics(self) -> Dict:
        """获取图谱统计"""
        return {
            'total_lessons': len(self.entities),
            'total_relationships': len(self.relationships),
            'avg_relationships_per_lesson': len(self.relationships) / max(len(self.entities), 1),
            'categories': len(set(e['category'] for e in self.entities.values())),
            'avg_keywords': sum(len(e['keywords']) for e in self.entities.values()) / max(len(self.entities), 1)
        }
    
    def export_graph(self) -> Dict:
        """导出图谱"""
        return {
            'entities': list(self.entities.values()),
            'relationships': self.relationships,
            'statistics': self.get_statistics(),
            'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def print_graph(self):
        """打印图谱"""
        print("=" * 60)
        print("知识图谱")
        print("=" * 60)
        
        stats = self.get_statistics()
        print(f"\n【统计】")
        print(f"  教训总数：{stats['total_lessons']}")
        print(f"  关系总数：{stats['total_relationships']}")
        print(f"  平均每教训关系：{stats['avg_relationships_per_lesson']:.1f}")
        print(f"  分类数量：{stats['categories']}")
        print(f"  平均关键词：{stats['avg_keywords']:.1f}")
        
        print(f"\n【知识聚类】")
        clusters = self.get_knowledge_clusters()
        for cluster in clusters[:5]:
            print(f"\n  {cluster['category']} ({cluster['lesson_count']}个教训):")
            for lesson in cluster['lessons'][:3]:
                print(f"    - {lesson['id']}: {lesson['title']}")
        
        print(f"\n【关系网络】")
        # 显示前 10 个关系
        for rel in self.relationships[:10]:
            print(f"  {rel['from']} --[{rel['type']}]--> {rel['to']}")
        
        print("\n" + "=" * 60)


def demo_knowledge_graph():
    """演示知识图谱"""
    print("=" * 60)
    print("知识图谱构建器")
    print("=" * 60)
    
    builder = KnowledgeGraphBuilder()
    
    # 示例教训
    lessons = [
        {
            'id': '[SYS-019]',
            'title': '100% 防护系统',
            'category': 'SYS - 系统配置',
            'keywords': ['防护', '路径', 'sitecustomize', '环境变量'],
            'confidence': 0.95,
            'created_at': '2026-03-14'
        },
        {
            'id': '[SYS-020]',
            'title': '7 人格检测验证',
            'category': 'SYS - 系统配置',
            'keywords': ['7 人格', '检测', '验证', '防护'],
            'confidence': 0.95,
            'created_at': '2026-03-14'
        },
        {
            'id': '[MULTI-021]',
            'title': '规划者优化',
            'category': 'MULTI - 7 人格系统',
            'keywords': ['规划者', '优化', '质量评估', '自动化'],
            'confidence': 0.92,
            'created_at': '2026-03-14'
        },
        {
            'id': '[MEM-011]',
            'title': '记忆系统优化',
            'category': 'MEM - 记忆系统',
            'keywords': ['记忆', '检索', '质量评估', '仪表板'],
            'confidence': 0.90,
            'created_at': '2026-03-14'
        }
    ]
    
    # 添加到图谱
    for lesson in lessons:
        builder.add_lesson(lesson)
        print(f"[添加] {lesson['id']}: {lesson['title']}")
    
    print()
    
    # 打印图谱
    builder.print_graph()
    
    # 查询相关教训
    print(f"\n【查询相关教训】[SYS-019]")
    related = builder.get_related_lessons('[SYS-019]', max_results=3)
    for rel in related:
        print(f"  - {rel['id']}: {rel['title']} (关系:{rel['relationship_type']})")


if __name__ == "__main__":
    demo_knowledge_graph()
