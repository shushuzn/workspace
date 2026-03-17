#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
报告质量评分系统
=================
自动评估报告质量并生成质量报告

评分维度 (7 个):
1. 标题 (15%): 是否清晰、具体、包含关键信息
2. 执行摘要 (15%): 是否有简洁的概述
3. 背景 (15%): 是否有充分的上下文
4. 结论 (15%): 是否有明确的结论和建议
5. 元数据 (15%): 是否有完整的元数据 (日期、作者、类型等)
6. 长度 (15%): 是否在合理范围内 (500-5000 字)
7. 检查清单 (10%): 是否有任务清单和验收标准

质量等级:
- 90-100%: 优秀 (Excellent)
- 70-89%:  良好 (Good)
- 50-69%:  需改进 (Needs Improvement)
- <50%:    不合格 (Poor)

使用:
  python report_quality_scorer.py --score "report.md"    # 评分单个报告
  python report_quality_scorer.py --batch                # 批量评分所有报告
  python report_quality_scorer.py --report               # 生成质量报告
  python report_quality_scorer.py --stats                # 显示统计信息
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('D:/OpenClaw/workspace')
REPORTS_DIR = WORKSPACE / '21-reports'
QUALITY_CONFIG = WORKSPACE / 'data' / 'report_quality_config.json'
QUALITY_STATE = WORKSPACE / 'data' / 'report_quality_state.json'
QUALITY_REPORTS_DIR = WORKSPACE / '21-reports' / 'quality-reports'


class ReportQualityScorer:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _load_config(self):
        default_config = {
            'dimensions': {
                'has_title': {'weight': 0.15, 'description': '标题清晰具体'},
                'has_executive_summary': {'weight': 0.15, 'description': '有执行摘要'},
                'has_background': {'weight': 0.15, 'description': '有背景说明'},
                'has_conclusions': {'weight': 0.15, 'description': '有结论建议'},
                'has_metadata': {'weight': 0.15, 'description': '元数据完整'},
                'min_length': {'weight': 0.15, 'description': '长度合理 (500-5000 字)'},
                'has_checklist': {'weight': 0.10, 'description': '有检查清单'}
            },
            'thresholds': {
                'excellent': 90,
                'good': 70,
                'needs_improvement': 50
            },
            'min_word_count': 500,
            'max_word_count': 5000,
            'required_metadata': ['date', 'author', 'type', 'status']
        }
        
        if QUALITY_CONFIG.exists():
            with open(QUALITY_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default_config
    
    def _load_state(self):
        if QUALITY_STATE.exists():
            with open(QUALITY_STATE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'last_scan': None, 'scores': []}
    
    def _save_state(self):
        QUALITY_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUALITY_STATE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def _count_words(self, text):
        """计算中文字数"""
        # 移除 Markdown 符号
        text = re.sub(r'[#*`\[\]()]', '', text)
        # 计算中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 计算英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + english_words
    
    def _check_title(self, content, filepath):
        """检查标题质量"""
        # 检查是否有 H1 标题
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not h1_match:
            return 0.0, "缺少 H1 标题"
        
        title = h1_match.group(1).strip()
        
        # 标题长度检查 (10-100 字符)
        if len(title) < 10:
            return 0.5, "标题过短"
        if len(title) > 100:
            return 0.7, "标题过长"
        
        # 检查是否包含关键信息 (日期、类型等)
        has_date = bool(re.search(r'\d{4}-\d{2}-\d{2}', title))
        has_type = bool(re.search(r'(报告 | 总结 | 完成 | 分析|评估)', title))
        
        score = 1.0
        feedback = []
        if not has_date:
            score -= 0.2
            feedback.append("标题建议包含日期")
        if not has_type:
            score -= 0.2
            feedback.append("标题建议包含报告类型")
        
        return max(0.5, score), "标题质量良好" if score == 1.0 else "; ".join(feedback)
    
    def _check_executive_summary(self, content):
        """检查执行摘要"""
        # 查找执行摘要部分
        summary_patterns = [
            r'##\s*执行摘要',
            r'##\s*摘要',
            r'##\s*Executive Summary',
            r'###\s*🎯\s*目标',
            r'##\s*任务[:：]'
        ]
        
        for pattern in summary_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 1.0, "有执行摘要"
        
        # 检查是否有简短的概述段落
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:500]
        if 50 < len(first_paragraph) < 500:
            return 0.7, "有概述但非标准摘要"
        
        return 0.0, "缺少执行摘要"
    
    def _check_background(self, content):
        """检查背景说明"""
        background_patterns = [
            r'##\s*背景',
            r'##\s*上下文',
            r'##\s*Background',
            r'##\s*简介',
            r'##\s*概述',
            r'###\s*📋\s*背景',
            r'##\s*任务[:：]',
            r'##\s*目标'
        ]
        
        for pattern in background_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 1.0, "有背景说明"
        
        # 检查是否有上下文信息
        if len(content) > 1000:
            return 0.7, "有上下文但不完整"
        
        return 0.3, "背景信息不足"
    
    def _check_conclusions(self, content):
        """检查结论和建议"""
        conclusion_patterns = [
            r'##\s*结论',
            r'##\s*总结',
            r'##\s*Conclusion',
            r'##\s*建议',
            r'##\s*下一步',
            r'###\s*✅\s*总结',
            r'###\s*🎯\s*下一步',
            r'##\s*关键发现'
        ]
        
        for pattern in conclusion_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 1.0, "有结论和建议"
        
        # 检查是否有总结性段落
        last_section = content.split('\n##')[-1] if '\n##' in content else content[-1000:]
        if '总结' in last_section or '下一步' in last_section:
            return 0.7, "有总结但不完整"
        
        return 0.3, "缺少明确结论"
    
    def _check_metadata(self, content, filepath):
        """检查元数据"""
        metadata_score = 0.0
        found_fields = []
        missing_fields = []
        
        # 检查常见元数据字段
        metadata_checks = [
            ('date', [r'\d{4}-\d{2}-\d{2}', r'日期[:：]', r'Date[::]']),
            ('author', [r'作者[:：]', r'Author[::]', r'By\s+\w+']),
            ('type', [r'类型[:：]', r'Type[::]', r'报告类型']),
            ('status', [r'状态[:：]', r'Status[::]', r'✅', r'❌', r'⏳']),
            ('tags', [r'标签[:：]', r'Tags[::]', r'#\w+']),
        ]
        
        for field, patterns in metadata_checks:
            found = any(re.search(p, content, re.IGNORECASE) for p in patterns)
            if found:
                found_fields.append(field)
                metadata_score += 0.2
            else:
                missing_fields.append(field)
        
        feedback = f"找到 {len(found_fields)} 个元数据字段"
        if missing_fields:
            feedback += f", 缺少：{', '.join(missing_fields)}"
        
        return min(1.0, metadata_score), feedback
    
    def _check_length(self, content):
        """检查报告长度"""
        word_count = self._count_words(content)
        
        if word_count < self.config['min_word_count']:
            return 0.3, f"过短 ({word_count} 字，建议>{self.config['min_word_count']})"
        elif word_count > self.config['max_word_count']:
            return 0.7, f"过长 ({word_count} 字，建议<{self.config['max_word_count']})"
        else:
            return 1.0, f"长度合适 ({word_count} 字)"
    
    def _check_checklist(self, content):
        """检查任务清单"""
        checklist_patterns = [
            r'-\s*\[[ xX]\]',  # Markdown 复选框
            r'\d+\.\s+',       # 编号列表
            r'验收标准',
            r'下一步',
            r'Todo',
            r'Task',
            r'检查清单'
        ]
        
        found_patterns = sum(1 for p in checklist_patterns if re.search(p, content))
        
        if found_patterns >= 3:
            return 1.0, "有完整的检查清单"
        elif found_patterns >= 1:
            return 0.6, "有部分清单"
        else:
            return 0.2, "缺少检查清单"
    
    def score_report(self, filepath):
        """对单个报告进行评分"""
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filepath = Path(filepath)
        
        # 各维度评分
        scores = {
            'has_title': self._check_title(content, filepath),
            'has_executive_summary': self._check_executive_summary(content),
            'has_background': self._check_background(content),
            'has_conclusions': self._check_conclusions(content),
            'has_metadata': self._check_metadata(content, filepath),
            'min_length': self._check_length(content),
            'has_checklist': self._check_checklist(content)
        }
        
        # 计算加权总分
        total_score = 0.0
        details = []
        
        for dimension, (score, feedback) in scores.items():
            weight = self.config['dimensions'][dimension]['weight']
            weighted_score = score * weight
            total_score += weighted_score
            details.append({
                'dimension': dimension,
                'score': score,
                'weight': weight,
                'weighted_score': weighted_score,
                'feedback': feedback
            })
        
        total_score = round(total_score * 100, 1)
        
        # 确定质量等级
        if total_score >= self.config['thresholds']['excellent']:
            grade = 'excellent'
            grade_cn = '优秀'
        elif total_score >= self.config['thresholds']['good']:
            grade = 'good'
            grade_cn = '良好'
        elif total_score >= self.config['thresholds']['needs_improvement']:
            grade = 'needs_improvement'
            grade_cn = '需改进'
        else:
            grade = 'poor'
            grade_cn = '不合格'
        
        result = {
            'file': str(filepath.relative_to(WORKSPACE)),
            'score': total_score,
            'grade': grade,
            'grade_cn': grade_cn,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def score_batch(self):
        """批量评分所有报告"""
        print('='*60)
        print('Batch Report Quality Scoring')
        print('='*60)
        
        scores = []
        now = datetime.now()
        
        for root, dirs, files in os.walk(REPORTS_DIR):
            # 跳过特殊目录
            if any(skip in root for skip in ['archive', 'quality-reports']):
                continue
            
            for file in files:
                if not file.endswith('.md'):
                    continue
                
                filepath = Path(root) / file
                print(f'Scoring: {file}...', end=' ')
                
                result = self.score_report(filepath)
                if result:
                    scores.append(result)
                    print(f"{result['score']}% ({result['grade_cn']})")
                else:
                    print("ERROR")
        
        self.state['last_scan'] = now.isoformat()
        self.state['scores'] = scores
        self._save_state()
        
        # 打印统计
        self._print_stats(scores)
        
        return scores
    
    def _print_stats(self, scores):
        """打印统计信息"""
        if not scores:
            print('No reports scored')
            return
        
        total = len(scores)
        avg_score = sum(s['score'] for s in scores) / total
        
        grades = {}
        for s in scores:
            grade = s['grade_cn']
            grades[grade] = grades.get(grade, 0) + 1
        
        print('\n' + '='*60)
        print('Statistics')
        print('='*60)
        print(f'Total reports: {total}')
        print(f'Average score: {avg_score:.1f}%')
        print('Grade distribution:')
        for grade, count in sorted(grades.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            print(f'  {grade}: {count} ({pct:.1f}%)')
    
    def generate_quality_report(self):
        """生成质量报告"""
        print('='*60)
        print('Generating Quality Report')
        print('='*60)
        
        if not self.state.get('scores'):
            print('No score data. Run --batch first.')
            return
        
        QUALITY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 生成报告
        scores = self.state['scores']
        total = len(scores)
        avg_score = sum(s['score'] for s in scores) / total if total > 0 else 0
        
        grades = {}
        for s in scores:
            grade = s['grade']
            grades[grade] = grades.get(grade, 0) + 1
        
        # 找出低分报告
        low_quality = [s for s in scores if s['score'] < 70]
        
        report_content = f'''# 报告质量评估报告

**生成日期:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**评估报告数:** {total}
**平均质量分:** {avg_score:.1f}%

## 质量分布

| 等级 | 数量 | 占比 |
|------|------|------|
'''
        
        for grade, count in sorted(grades.items(), key=lambda x: -x[1]):
            pct = count / total * 100 if total > 0 else 0
            grade_cn = {'excellent': '优秀', 'good': '良好', 'needs_improvement': '需改进', 'poor': '不合格'}[grade]
            report_content += f'| {grade_cn} | {count} | {pct:.1f}% |\n'
        
        report_content += f'''
## 低质量报告 (需要改进)

共 {len(low_quality)} 个报告质量分<70%

'''
        
        for s in low_quality[:10]:  # 只显示前 10 个
            report_content += f'''### {s['file']}

- **得分:** {s['score']}%
- **等级:** {s['grade_cn']}
- **主要问题:**
'''
            for detail in s['details']:
                if detail['score'] < 0.7:
                    report_content += f'  - {detail["dimension"]}: {detail["feedback"]}\n'
            report_content += '\n'
        
        report_content += '''
## 改进建议

1. **标题优化**: 包含日期和报告类型
2. **执行摘要**: 添加简洁的目标和成果概述
3. **背景说明**: 提供充分的上下文信息
4. **结论明确**: 总结关键发现和建议
5. **元数据完整**: 填写日期、作者、类型、状态
6. **长度适中**: 保持在 500-5000 字之间
7. **检查清单**: 添加任务和验收标准

## 下一步

- [ ] 审查低质量报告并改进
- [ ] 建立质量门槛 (新报告必须>70%)
- [ ] 定期生成质量报告 (每月)
- [ ] 追踪质量趋势
'''
        
        report_file = QUALITY_REPORTS_DIR / f'quality-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'Quality report generated: {report_file}')
        return report_file
    
    def show_stats(self):
        """显示统计信息"""
        print('='*60)
        print('Report Quality Statistics')
        print('='*60)
        
        if not self.state.get('scores'):
            print('No score data. Run --batch first.')
            return
        
        self._print_stats(self.state['scores'])


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Quality Scorer')
    parser.add_argument('--score', type=str, help='Score a single report')
    parser.add_argument('--batch', action='store_true', help='Batch score all reports')
    parser.add_argument('--report', action='store_true', help='Generate quality report')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    scorer = ReportQualityScorer()
    
    if args.score:
        result = scorer.score_report(args.score)
        if result:
            print(f'Score: {result["score"]}% ({result["grade_cn"]})')
            for detail in result['details']:
                icon = '[OK]' if detail['score'] >= 0.7 else '[FAIL]'
                print(f'  {icon} {detail["dimension"]}: {detail["score"]*100:.0f}% - {detail["feedback"]}')
    elif args.batch:
        scorer.score_batch()
    elif args.report:
        scorer.generate_quality_report()
    elif args.stats:
        scorer.show_stats()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
