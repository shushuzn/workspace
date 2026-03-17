#!/usr/bin/env python3
"""
记忆质量评估系统 - Memory Quality Assessor
功能：自动评估记忆质量，提供改进建议
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

MEMORY_FILE = Path(r"C:\Users\华为\.copaw\MEMORY.md")

class MemoryQualityAssessor:
    """记忆质量评估器"""
    
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.criteria = {
            'completeness': 0.25,  # 完整性
            'clarity': 0.25,       # 清晰度
            'relevance': 0.25,     # 相关性
            'actionability': 0.25  # 可操作性
        }
    
    def assess_memory(self, content: str) -> Dict:
        """评估单个记忆片段质量"""
        scores = {
            'completeness': self._assess_completeness(content),
            'clarity': self._assess_clarity(content),
            'relevance': self._assess_relevance(content),
            'actionability': self._assess_actionability(content)
        }
        
        # 加权总分
        total_score = sum(scores[k] * self.criteria[k] for k in scores)
        
        # 等级评定
        if total_score >= 0.9:
            grade = 'A+'  # 优秀
        elif total_score >= 0.8:
            grade = 'A'   # 良好
        elif total_score >= 0.7:
            grade = 'B'   # 中等
        elif total_score >= 0.6:
            grade = 'C'   # 需改进
        else:
            grade = 'D'   # 不合格
        
        # 改进建议
        suggestions = self._generate_suggestions(scores, content)
        
        return {
            'total_score': total_score,
            'grade': grade,
            'scores': scores,
            'suggestions': suggestions,
            'strengths': self._identify_strengths(scores, content)
        }
    
    def _assess_completeness(self, content: str) -> float:
        """评估完整性"""
        score = 0.5
        
        # 有编号 → +0.2
        if re.search(r'\[(SYS|MEM|MULTI|SEC|FEISHU|CR)-\d+\]', content):
            score += 0.2
        
        # 有日期 → +0.1
        if re.search(r'\d{4}-\d{2}-\d{2}', content):
            score += 0.1
        
        # 有解决方案 → +0.1
        if any(kw in content.lower() for kw in ['solution', '解决', '方案', 'fix']):
            score += 0.1
        
        # 长度适中 (100-2000 字) → +0.1
        if 100 <= len(content) <= 2000:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_clarity(self, content: str) -> float:
        """评估清晰度"""
        score = 0.5
        
        # 有明确标题 → +0.2
        if re.search(r'^## .+', content, re.MULTILINE):
            score += 0.2
        
        # 有结构化内容 (列表/表格) → +0.2
        if re.search(r'^[-*]|\|.*\|', content, re.MULTILINE):
            score += 0.2
        
        # 有代码块 → +0.1
        if '```' in content:
            score += 0.1
        
        # 段落分明 → +0.1
        if content.count('\n\n') >= 2:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_relevance(self, content: str) -> float:
        """评估相关性"""
        score = 0.6
        
        # 包含关键词 → +0.2
        keywords = ['工作目录', '路径', '防护', '系统', '配置', '自动化']
        if any(kw in content for kw in keywords):
            score += 0.2
        
        # 置信度标注 → +0.2
        if '置信度' in content or 'confidence' in content.lower():
            score += 0.2
        
        return min(1.0, score)
    
    def _assess_actionability(self, content: str) -> float:
        """评估可操作性"""
        score = 0.5
        
        # 有具体步骤 → +0.3
        if re.search(r'\d\.[\s\S]*?\n', content):
            score += 0.3
        
        # 有代码示例 → +0.2
        if '```' in content and len(re.findall(r'```[\s\S]*?```', content)) > 0:
            score += 0.2
        
        # 有工具/文件引用 → +0.1
        if re.search(r'\.[a-z]+|\.py|\.md|\.bat', content, re.IGNORECASE):
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_suggestions(self, scores: Dict[str, float], content: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if scores['completeness'] < 0.7:
            suggestions.append("添加编号 (如 [SYS-XXX]) 和日期")
        
        if scores['clarity'] < 0.7:
            suggestions.append("使用列表、表格或代码块增强结构")
        
        if scores['relevance'] < 0.7:
            suggestions.append("明确标注置信度和相关性")
        
        if scores['actionability'] < 0.7:
            suggestions.append("添加具体步骤和代码示例")
        
        if len(content) < 100:
            suggestions.append("内容过短，建议补充更多细节")
        elif len(content) > 2000:
            suggestions.append("内容过长，建议精简到 2000 字以内")
        
        return suggestions
    
    def _identify_strengths(self, scores: Dict[str, float], content: str) -> List[str]:
        """识别优点"""
        strengths = []
        
        if scores['completeness'] >= 0.8:
            strengths.append("信息完整，包含编号和日期")
        
        if scores['clarity'] >= 0.8:
            strengths.append("结构清晰，易于阅读")
        
        if scores['relevance'] >= 0.8:
            strengths.append("高度相关，置信度明确")
        
        if scores['actionability'] >= 0.8:
            strengths.append("可操作性强，有具体步骤")
        
        return strengths
    
    def assess_all_memories(self) -> List[Dict]:
        """评估所有记忆片段"""
        if not self.memory_file.exists():
            return []
        
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割记忆片段
        sections = re.split(r'\n(?=## )', content)
        
        results = []
        for section in sections:
            if not section.strip() or section.strip().startswith('---'):
                continue
            
            assessment = self.assess_memory(section)
            
            # 提取标题
            title_match = re.search(r'^## (.+)', section, re.MULTILINE)
            title = title_match.group(1) if title_match else "Untitled"
            
            results.append({
                'title': title,
                'assessment': assessment,
                'preview': section[:100]
            })
        
        return results


def demo_assessment():
    """演示记忆质量评估"""
    print("=" * 60)
    print("记忆质量评估系统")
    print("=" * 60)
    
    assessor = MemoryQualityAssessor()
    
    # 评估所有记忆
    results = assessor.assess_all_memories()
    
    print(f"\n共评估 {len(results)} 个记忆片段\n")
    
    # 按质量排序
    results.sort(key=lambda x: x['assessment']['total_score'], reverse=True)
    
    # 显示前 5 个
    print("高质量记忆 (Top 5):")
    for i, result in enumerate(results[:5], 1):
        assessment = result['assessment']
        print(f"\n{i}. {result['title']}")
        print(f"   评分：{assessment['total_score']:.2f} ({assessment['grade']})")
        print(f"   优点：{', '.join(assessment['strengths'][:2])}")
    
    # 显示需改进的
    low_quality = [r for r in results if r['assessment']['total_score'] < 0.7]
    if low_quality:
        print(f"\n{'='*60}")
        print(f"需改进的记忆 ({len(low_quality)} 个):")
        for i, result in enumerate(low_quality[:3], 1):
            assessment = result['assessment']
            print(f"\n{i}. {result['title']}")
            print(f"   评分：{assessment['total_score']:.2f} ({assessment['grade']})")
            print(f"   建议：{assessment['suggestions'][0] if assessment['suggestions'] else '无'}")
    
    # 总体统计
    avg_score = sum(r['assessment']['total_score'] for r in results) / len(results) if results else 0
    print(f"\n{'='*60}")
    print("总体统计:")
    print(f"  平均质量：{avg_score:.2f}")
    print(f"  高质量 (A 级): {len([r for r in results if r['assessment']['grade'] in ['A', 'A+']])}")
    print(f"  需改进 (C/D 级): {len([r for r in results if r['assessment']['grade'] in ['C', 'D']])}")


if __name__ == "__main__":
    demo_assessment()
