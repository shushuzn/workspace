#!/usr/bin/env python3
"""
批判者子代理 v2 - 增强质量审查

角色：审查质量、发现问题、提供修复建议
模型：qwen3.5-plus
权重：1.2
"""

import sys
import json
from datetime import datetime
from typing import Dict, List

class CriticAgent:
    """批判者子代理 v2"""
    
    def __init__(self):
        self.name = "批判者"
        self.role = "审查质量、发现问题、提供修复建议"
        self.model = "qwen3.5-plus"
        self.weight = 1.2
        self.agent_id = f"critic-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 质量维度权重
        self.dimensions = {
            'completeness': 0.30,  # 完整性
            'correctness': 0.30,   # 正确性
            'clarity': 0.20,       # 清晰度
            'actionability': 0.20  # 可操作性
        }
    
    def process(self, output: dict, context: dict) -> dict:
        """
        审查执行者输出
        
        Args:
            output: 执行者输出
            context: 上下文信息
            
        Returns:
            审查结果（含修复建议）
        """
        # 多维度评分
        scores = self._calculate_dimension_scores(output, context)
        overall_score = self._calculate_overall_score(scores)
        
        # 问题检测
        issues = self._find_issues(output, context)
        
        # 修复建议
        fixes = self._generate_fixes(issues, context)
        
        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "reviewed_output": output.get("agent_id", "unknown"),
            "overall_score": overall_score,
            "dimension_scores": scores,
            "issues": issues,
            "fixes": fixes,
            "recommendation": "approve" if overall_score >= 85 else "revise",
            "confidence": self._calculate_confidence(scores),
            "critical_issues": [i for i in issues if i.get('severity') == 'critical']
        }
        return result
    
    def _calculate_dimension_scores(self, output: dict, context: dict) -> dict:
        """多维度评分"""
        scores = {}
        
        # 1. 完整性 (30%)
        scores['completeness'] = self._score_completeness(output, context)
        
        # 2. 正确性 (30%)
        scores['correctness'] = self._score_correctness(output, context)
        
        # 3. 清晰度 (20%)
        scores['clarity'] = self._score_clarity(output)
        
        # 4. 可操作性 (20%)
        scores['actionability'] = self._score_actionability(output, context)
        
        return scores
    
    def _score_completeness(self, output: dict, context: dict) -> int:
        """完整性评分"""
        score = 100
        
        # 检查必需字段
        required_fields = ['output', 'status']
        for field in required_fields:
            if not output.get(field):
                score -= 25
        
        # 检查验收标准
        if context.get('acceptance_criteria'):
            if not output.get('verification'):
                score -= 15
        
        # 检查输出质量
        output_text = output.get('output', '')
        if len(output_text) < 50:
            score -= 20
        elif len(output_text) < 200:
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_correctness(self, output: dict, context: dict) -> int:
        """正确性评分"""
        score = 100
        
        # 检查错误标记
        if output.get('error'):
            score -= 40
        
        # 检查状态
        if output.get('status') == 'failed':
            score -= 30
        elif output.get('status') == 'partial':
            score -= 15
        
        # 检查一致性
        if context.get('expected_format'):
            if not self._check_format(output.get('output', ''), context['expected_format']):
                score -= 20
        
        return max(0, min(100, score))
    
    def _score_clarity(self, output: dict) -> int:
        """清晰度评分"""
        score = 100
        
        output_text = output.get('output', '')
        
        # 检查结构
        if not any(marker in output_text for marker in ['\n', '###', '**', '- ']):
            score -= 20
        
        # 检查长度合理性
        if len(output_text) > 5000:
            score -= 15  # 可能过于冗长
        
        # 检查是否有总结
        if len(output_text) > 200 and not any(word in output_text.lower() for word in ['总结', 'conclusion', 'summary']):
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_actionability(self, output: dict, context: dict) -> int:
        """可操作性评分"""
        score = 100
        
        output_text = output.get('output', '')
        
        # 检查是否有具体步骤
        if context.get('task_type') in ['optimization', 'creation', 'fix']:
            if not any(marker in output_text for marker in ['步骤', 'step', '1.', '2.', '- [']):
                score -= 25
        
        # 检查是否有验证方法
        if not any(marker in output_text for marker in ['验证', 'verify', 'test', 'check']):
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_overall_score(self, scores: dict) -> int:
        """计算综合评分"""
        overall = sum(scores[dim] * weight for dim, weight in self.dimensions.items())
        return int(overall)
    
    def _calculate_confidence(self, scores: dict) -> float:
        """计算置信度"""
        # 评分越一致，置信度越高
        values = list(scores.values())
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        
        # 方差越小，置信度越高
        confidence = 0.95 - min(0.3, variance / 100)
        return round(confidence, 2)
    
    def _find_issues(self, output: dict, context: dict) -> list:
        """找出问题（带严重性分级）"""
        issues = []
        
        # 关键问题
        if not output.get('output'):
            issues.append({
                'type': 'missing_output',
                'severity': 'critical',
                'description': '缺少输出内容',
                'dimension': 'completeness'
            })
        
        if output.get('status') == 'failed':
            issues.append({
                'type': 'task_failed',
                'severity': 'critical',
                'description': '任务执行失败',
                'dimension': 'correctness'
            })
        
        # 严重问题
        if output.get('error'):
            issues.append({
                'type': 'has_error',
                'severity': 'major',
                'description': f'存在错误：{output.get("error")}',
                'dimension': 'correctness'
            })
        
        if len(output.get('output', '')) < 50:
            issues.append({
                'type': 'output_too_short',
                'severity': 'major',
                'description': '输出内容过短 (<50 字符)',
                'dimension': 'completeness'
            })
        
        # 一般问题
        if context.get('acceptance_criteria') and not output.get('verification'):
            issues.append({
                'type': 'missing_verification',
                'severity': 'minor',
                'description': '缺少验收验证',
                'dimension': 'completeness'
            })
        
        return issues
    
    def _generate_fixes(self, issues: list, context: dict) -> list:
        """生成修复建议"""
        fixes = []
        
        for issue in issues:
            fix = {
                'issue_type': issue['type'],
                'priority': 'high' if issue['severity'] == 'critical' else 'medium' if issue['severity'] == 'major' else 'low',
                'action': self._get_fix_action(issue['type'], context),
                'estimated_effort': self._estimate_effort(issue['type'])
            }
            fixes.append(fix)
        
        return fixes
    
    def _get_fix_action(self, issue_type: str, context: dict) -> str:
        """获取修复动作"""
        fix_actions = {
            'missing_output': '重新执行任务，确保生成完整输出',
            'task_failed': '检查错误日志，修复后重新执行',
            'has_error': '解决报错问题：检查输入、依赖、权限',
            'output_too_short': '扩展输出内容，添加详细说明和示例',
            'missing_verification': '添加验证步骤和验收标准检查结果'
        }
        return fix_actions.get(issue_type, '手动审查并修复')
    
    def _estimate_effort(self, issue_type: str) -> str:
        """估算修复工作量"""
        efforts = {
            'missing_output': '5-10 分钟',
            'task_failed': '10-30 分钟',
            'has_error': '5-20 分钟',
            'output_too_short': '5-15 分钟',
            'missing_verification': '2-5 分钟'
        }
        return efforts.get(issue_type, '未知')
    
    def _check_format(self, output: str, expected_format: str) -> bool:
        """检查格式是否符合预期"""
        # 简单格式检查
        if expected_format == 'json':
            try:
                json.loads(output)
                return True
            except:
                return False
        elif expected_format == 'markdown':
            return output.strip().startswith('#') or '---' in output
        return True


def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read().strip())
    
    agent = CriticAgent()
    result = agent.process(input_data.get("output", {}), input_data.get("context", {}))
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
