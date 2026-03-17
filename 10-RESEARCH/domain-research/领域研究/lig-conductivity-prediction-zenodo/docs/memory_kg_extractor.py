#!/usr/bin/env python3
"""
Memory to Knowledge Graph Extractor
从 MEMORY.md 自动提取教训代码，构建知识图谱

Usage:
    python memory_kg_extractor.py --extract
    python memory_kg_extractor.py --preview
    python memory_kg_extractor.py --stats
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Lesson:
    """教训数据结构"""
    id: str  # 如 INNOVATOR-152
    content: str  # 教训内容
    category: str  # 类别 (INNOVATOR/SYS/MULTI/FILE/等)
    source: str  # 来源文件
    line_number: int  # 行号
    confidence: float  # 置信度
    created_at: str  # 创建时间
    tags: List[str]  # 标签


@dataclass
class ExtractionResult:
    """提取结果"""
    total_lessons: int
    by_category: Dict[str, int]
    lessons: List[Lesson]
    entities: List[Dict]
    relations: List[Dict]
    extraction_time_ms: float


class MemoryKGExtractor:
    """MEMORY.md 到知识图谱提取器"""
    
    def __init__(self, memory_file: str = "MEMORY.md"):
        self.memory_file = memory_file
        self.lessons: List[Lesson] = []
        self.categories = {
            'INNOVATOR': '创新者系统',
            'SYS': '系统配置',
            'MULTI': '7 人格系统',
            'FILE': '文件操作',
            'FEISHU': '飞书集成',
            'SEC': '安全相关',
            'MEM': '记忆系统',
            'CR': '批判者发现',
            'OLLAMA': '本地 LLM',
            'LEARNER': '学习者',
            'STOCK': '股票分析',
            'ARXIV': 'arXiv 研究',
            'GIT': 'Git 工作流',
            'KG': '知识图谱',
        }
    
    def extract_lessons(self) -> List[Lesson]:
        """从 MEMORY.md 提取所有教训"""
        
        if not Path(self.memory_file).exists():
            print(f"❌ 文件不存在：{self.memory_file}")
            return []
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        lessons = []
        
        # 模式 1: [INNOVATOR-XXX] 教训内容
        pattern_lesson = r'\[([A-Z]+-\d+)\]\s*(.+?)(?:\n|$)'
        
        for line_num, line in enumerate(lines, 1):
            matches = re.findall(pattern_lesson, line)
            for lesson_id, lesson_content in matches:
                # 提取类别
                category = lesson_id.split('-')[0]
                
                # 计算置信度 (基于格式完整性)
                confidence = self._calculate_confidence(line, lesson_id)
                
                # 提取标签
                tags = self._extract_tags(lesson_content)
                
                lesson = Lesson(
                    id=lesson_id,
                    content=lesson_content.strip(),
                    category=category,
                    source=self.memory_file,
                    line_number=line_num,
                    confidence=confidence,
                    created_at=datetime.now().isoformat(),
                    tags=tags
                )
                lessons.append(lesson)
        
        self.lessons = lessons
        return lessons
    
    def _calculate_confidence(self, line: str, lesson_id: str) -> float:
        """计算教训置信度"""
        score = 0.5  # 基础分
        
        # 格式完整 +0.2
        if re.match(r'\[([A-Z]+-\d+)\]\s*.+', line):
            score += 0.2
        
        # 有详细描述 +0.1
        if len(line) > 50:
            score += 0.1
        
        # 在教训章节 +0.2
        if '教训' in line or 'LESSON' in line:
            score += 0.2
        
        return min(1.0, score)
    
    def _extract_tags(self, content: str) -> List[str]:
        """从内容提取标签"""
        tags = []
        
        # 提取关键词
        keywords = ['自动化', '优化', '集成', '部署', '测试', '监控', '安全', '性能']
        for keyword in keywords:
            if keyword in content:
                tags.append(keyword)
        
        # 提取技术名词
        tech_terms = ['Ollama', 'LLM', 'arXiv', 'Git', 'Dashboard', 'API', 'CLI']
        for term in tech_terms:
            if term in content:
                tags.append(term)
        
        return list(set(tags))
    
    def generate_entities(self) -> List[Dict]:
        """从教训生成知识图谱实体"""
        
        entities = []
        seen_ids = set()
        
        for lesson in self.lessons:
            if lesson.id in seen_ids:
                continue
            
            entity = {
                'id': f"LESSON-{lesson.id}",
                'type': 'Lesson',
                'properties': {
                    'lesson_id': lesson.id,
                    'content': lesson.content,
                    'category': lesson.category,
                    'category_name': self.categories.get(lesson.category, '其他'),
                    'confidence': lesson.confidence,
                    'source': lesson.source,
                    'line_number': lesson.line_number,
                    'created_at': lesson.created_at,
                    'tags': lesson.tags
                }
            }
            entities.append(entity)
            seen_ids.add(lesson.id)
        
        return entities
    
    def generate_relations(self) -> List[Dict]:
        """从教训生成知识图谱关系"""
        
        relations = []
        
        # 关系 1: 教训 → 类别
        category_lessons = {}
        for lesson in self.lessons:
            if lesson.category not in category_lessons:
                category_lessons[lesson.category] = []
            category_lessons[lesson.category].append(lesson.id)
        
        for category, lesson_ids in category_lessons.items():
            for lesson_id in lesson_ids:
                relation = {
                    'source': f"LESSON-{lesson_id}",
                    'target': f"CATEGORY-{category}",
                    'type': 'BELONGS_TO',
                    'properties': {
                        'weight': 1.0
                    }
                }
                relations.append(relation)
            
            # 添加类别实体
            category_entity = {
                'id': f"CATEGORY-{category}",
                'type': 'Category',
                'properties': {
                    'name': self.categories.get(category, category),
                    'lesson_count': len(lesson_ids)
                }
            }
        
        # 关系 2: 教训 → 标签
        for lesson in self.lessons:
            for tag in lesson.tags:
                relation = {
                    'source': f"LESSON-{lesson.id}",
                    'target': f"TAG-{tag}",
                    'type': 'TAGGED_WITH',
                    'properties': {
                        'weight': 0.8
                    }
                }
                relations.append(relation)
        
        return relations
    
    def get_stats(self) -> Dict:
        """获取提取统计"""
        
        by_category = {}
        for lesson in self.lessons:
            category = lesson.category
            by_category[category] = by_category.get(category, 0) + 1
        
        return {
            'total_lessons': len(self.lessons),
            'by_category': by_category,
            'avg_confidence': sum(l.confidence for l in self.lessons) / len(self.lessons) if self.lessons else 0,
            'total_tags': len(set(tag for l in self.lessons for tag in l.tags)),
            'unique_categories': len(by_category)
        }
    
    def extract_and_save(self, output_dir: str = "data") -> ExtractionResult:
        """提取并保存结果"""
        
        start_time = datetime.now()
        
        # 提取教训
        print("📚 从 MEMORY.md 提取教训...")
        lessons = self.extract_lessons()
        print(f"✅ 提取 {len(lessons)} 条教训")
        
        # 生成实体
        print("🔷 生成实体...")
        entities = self.generate_entities()
        print(f"✅ 生成 {len(entities)} 个实体")
        
        # 生成关系
        print("🔗 生成关系...")
        relations = self.generate_relations()
        print(f"✅ 生成 {len(relations)} 个关系")
        
        # 保存结果
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存教训
        lessons_file = output_path / "memory_lessons.json"
        with open(lessons_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(l) for l in lessons], f, ensure_ascii=False, indent=2)
        print(f"💾 教训保存到：{lessons_file}")
        
        # 保存实体
        entities_file = output_path / "memory_entities.json"
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)
        print(f"💾 实体保存到：{entities_file}")
        
        # 保存关系
        relations_file = output_path / "memory_relations.json"
        with open(relations_file, 'w', encoding='utf-8') as f:
            json.dump(relations, f, ensure_ascii=False, indent=2)
        print(f"💾 关系保存到：{relations_file}")
        
        # 计算时间
        end_time = datetime.now()
        extraction_time = (end_time - start_time).total_seconds() * 1000
        
        # 生成统计
        stats = self.get_stats()
        
        result = ExtractionResult(
            total_lessons=len(lessons),
            by_category=stats['by_category'],
            lessons=lessons,
            entities=entities,
            relations=relations,
            extraction_time_ms=extraction_time
        )
        
        # 保存统计
        stats_file = output_path / "memory_extraction_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, ensure_ascii=False, indent=2, default=str)
        print(f"💾 统计保存到：{stats_file}")
        
        return result
    
    def preview(self, limit: int = 10):
        """预览提取结果"""
        
        lessons = self.extract_lessons()
        
        print("\n" + "="*80)
        print("📚 MEMORY.md 教训预览")
        print("="*80)
        
        for i, lesson in enumerate(lessons[:limit], 1):
            print(f"\n{i}. [{lesson.id}]")
            print(f"   内容：{lesson.content[:80]}...")
            print(f"   类别：{lesson.category} ({self.categories.get(lesson.category, '其他')})")
            print(f"   置信度：{lesson.confidence:.2f}")
            print(f"   标签：{', '.join(lesson.tags) if lesson.tags else '无'}")
        
        if len(lessons) > limit:
            print(f"\n... 还有 {len(lessons) - limit} 条教训")
        
        print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MEMORY.md 到知识图谱提取器')
    parser.add_argument('--extract', action='store_true', help='提取并保存')
    parser.add_argument('--preview', action='store_true', help='预览提取结果')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--memory-file', default='MEMORY.md', help='MEMORY.md 文件路径')
    
    args = parser.parse_args()
    
    extractor = MemoryKGExtractor(args.memory_file)
    
    if args.preview:
        extractor.preview()
    
    elif args.extract:
        result = extractor.extract_and_save()
        
        print("\n" + "="*80)
        print("📊 提取统计")
        print("="*80)
        print(f"  总教训数：{result.total_lessons}")
        print(f"  实体数：{len(result.entities)}")
        print(f"  关系数：{len(result.relations)}")
        print(f"  提取时间：{result.extraction_time_ms:.1f}ms")
        
        print("\n  按类别分布:")
        for category, count in sorted(result.by_category.items(), key=lambda x: x[1], reverse=True):
            category_name = extractor.categories.get(category, category)
            print(f"    {category} ({category_name}): {count}")
        
        print("\n" + "="*80)
        print("✅ 提取完成！")
        print("="*80)
    
    elif args.stats:
        lessons = extractor.extract_lessons()
        stats = extractor.get_stats()
        
        print("\n" + "="*80)
        print("📊 MEMORY.md 教训统计")
        print("="*80)
        print(f"  总教训数：{stats['total_lessons']}")
        print(f"  平均置信度：{stats['avg_confidence']:.2f}")
        print(f"  唯一标签数：{stats['total_tags']}")
        print(f"  类别数：{stats['unique_categories']}")
        
        print("\n  按类别分布:")
        for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
            category_name = extractor.categories.get(category, category)
            percentage = count / stats['total_lessons'] * 100 if stats['total_lessons'] > 0 else 0
            print(f"    {category} ({category_name}): {count} ({percentage:.1f}%)")
        
        print("\n" + "="*80)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
