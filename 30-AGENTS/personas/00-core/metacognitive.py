#!/usr/bin/env python3
"""
元认知子代理 v2 - 增强系统监控与元进化

角色：监控系统本身、人格健康、元进化决策
模型：qwen3.5-plus
权重：1.5
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MetacognitiveAgent:
    """元认知子代理 v2"""
    
    def __init__(self):
        self.name = "元认知"
        self.role = "监控系统本身、人格健康、元进化决策"
        self.model = "qwen3.5-plus"
        self.weight = 1.5
        self.agent_id = f"metacognitive-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 人格健康指标
        self.persona_health_metrics = {
            'planner': {'name': '规划者', 'target_range': (70, 90), 'warning_line': 60},
            'executor': {'name': '执行者', 'target_range': (80, 95), 'warning_line': 70},
            'critic': {'name': '批判者', 'target_range': (85, 95), 'warning_line': 80},
            'learner': {'name': '学习者', 'target_range': (80, 95), 'warning_line': 70},
            'coordinator': {'name': '协调者', 'target_range': (80, 95), 'warning_line': 70},
            'innovator': {'name': '创新者', 'target_range': (75, 90), 'warning_line': 65},
            'metacognitive': {'name': '元认知', 'target_range': (90, 98), 'warning_line': 85}
        }
        
        # 系统整体指标
        self.system_metrics = {
            'continuous_work_minutes': {'name': '连续工作时间', 'normal': 90, 'warning': 120, 'danger': 150},
            'critic_avg_score': {'name': '批判者平均分', 'normal': 85, 'warning': 75, 'danger': 65},
            'task_backlog': {'name': '任务积压', 'normal': 5, 'warning': 10, 'danger': 15},
            'persona_conflicts': {'name': '人格冲突', 'normal': 0, 'warning': 2, 'danger': 3}
        }
        
        # 仲裁规则
        self.arbitration_rules = {
            ('executor', 'critic'): {'principle': '质量>速度', 'priority': 'critic'},
            ('executor', 'coordinator'): {'principle': '健康>产出', 'priority': 'coordinator'},
            ('planner', 'executor'): {'principle': '方向>效率', 'priority': 'planner'},
            ('innovator', 'critic'): {'principle': '平衡创新与质量', 'priority': 'metacognitive'},
            ('learner', 'executor'): {'principle': '进化>产出', 'priority': 'learner'}
        }
    
    def process(self, system_state: dict, context: dict) -> dict:
        """
        元认知处理
        
        Args:
            system_state: 系统状态 (包含各人格状态)
            context: 上下文信息
            
        Returns:
            元认知评估结果
        """
        # 1. 人格健康评估
        persona_health = self._evaluate_persona_health(system_state)
        
        # 2. 系统整体健康评估
        system_health = self._evaluate_system_health(system_state)
        
        # 3. 冲突检测与仲裁
        conflicts = self._detect_conflicts(system_state)
        arbitration = self._arbitrate_conflicts(conflicts, system_state)
        
        # 4. 元进化建议
        evolution_suggestions = self._suggest_evolution(persona_health, system_health)
        
        # 5. 风险预警
        risk_warnings = self._generate_risk_warnings(system_health)
        
        # 6. 综合评分
        overall_score = self._calculate_overall_score(persona_health, system_health)
        
        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "persona_health": persona_health,
            "system_health": system_health,
            "conflicts": conflicts,
            "arbitration": arbitration,
            "evolution_suggestions": evolution_suggestions,
            "risk_warnings": risk_warnings,
            "overall_score": overall_score,
            "recommendation": self._generate_recommendation(overall_score, risk_warnings),
            "next_check_time": self._calculate_next_check_time(risk_warnings)
        }
        return result
    
    def _evaluate_persona_health(self, system_state: dict) -> dict:
        """评估各人格健康状态"""
        health_report = {}
        
        for persona_id, metrics in self.persona_health_metrics.items():
            persona_data = system_state.get('personas', {}).get(persona_id, {})
            
            # 获取实际分数
            actual_score = persona_data.get('avg_score', 85)
            
            # 评估状态
            if actual_score >= metrics['target_range'][1]:
                status = 'excellent'
            elif actual_score >= metrics['target_range'][0]:
                status = 'healthy'
            elif actual_score >= metrics['warning_line']:
                status = 'warning'
            else:
                status = 'critical'
            
            health_report[persona_id] = {
                'name': metrics['name'],
                'score': actual_score,
                'target_range': metrics['target_range'],
                'warning_line': metrics['warning_line'],
                'status': status,
                'trend': persona_data.get('trend', 'stable'),
                'task_count': persona_data.get('task_count', 0),
                'success_rate': persona_data.get('success_rate', 0)
            }
        
        return health_report
    
    def _evaluate_system_health(self, system_state: dict) -> dict:
        """评估系统整体健康"""
        health_report = {}
        
        for metric_id, config in self.system_metrics.items():
            actual_value = system_state.get(metric_id, config['normal'])
            
            # 评估状态
            if metric_id in ['critic_avg_score']:
                # 分数越高越好
                if actual_value >= config['normal']:
                    status = 'healthy'
                elif actual_value >= config['warning']:
                    status = 'warning'
                else:
                    status = 'critical'
            else:
                # 其他指标越低越好
                if actual_value <= config['normal']:
                    status = 'healthy'
                elif actual_value <= config['warning']:
                    status = 'warning'
                else:
                    status = 'critical'
            
            health_report[metric_id] = {
                'name': config['name'],
                'value': actual_value,
                'thresholds': {
                    'normal': config['normal'],
                    'warning': config['warning'],
                    'danger': config['danger']
                },
                'status': status,
                'unit': '分钟' if 'work_minutes' in metric_id else '分' if 'score' in metric_id else '个' if 'backlog' in metric_id or 'conflicts' in metric_id else ''
            }
        
        return health_report
    
    def _detect_conflicts(self, system_state: dict) -> list:
        """检测人格冲突"""
        conflicts = []
        
        # 从系统状态中读取冲突
        detected_conflicts = system_state.get('conflicts', [])
        
        for conflict in detected_conflicts:
            conflicts.append({
                'id': conflict.get('id', f'conflict-{len(conflicts)+1}'),
                'personas': conflict.get('personas', []),
                'description': conflict.get('description', ''),
                'severity': conflict.get('severity', 'medium'),
                'frequency': conflict.get('frequency', 1),
                'last_occurrence': conflict.get('last_occurrence', '')
            })
        
        return conflicts
    
    def _arbitrate_conflicts(self, conflicts: list, system_state: dict) -> list:
        """仲裁人格冲突"""
        arbitration_results = []
        
        for conflict in conflicts:
            personas = conflict.get('personas', [])
            
            if len(personas) >= 2:
                key = tuple(sorted([personas[0], personas[1]]))
                
                if key in self.arbitration_rules:
                    rule = self.arbitration_rules[key]
                    arbitration_results.append({
                        'conflict_id': conflict['id'],
                        'principle': rule['principle'],
                        'priority': rule['priority'],
                        'decision': f"{rule['priority']} 优先",
                        'reasoning': self._generate_arbitration_reasoning(rule, system_state)
                    })
                else:
                    # 默认仲裁：平衡双方
                    arbitration_results.append({
                        'conflict_id': conflict['id'],
                        'principle': '平衡双方利益',
                        'priority': 'balance',
                        'decision': '寻求平衡方案',
                        'reasoning': '无明确规则，建议平衡双方需求'
                    })
        
        return arbitration_results
    
    def _generate_arbitration_reasoning(self, rule: dict, system_state: dict) -> str:
        """生成仲裁理由"""
        principle = rule['principle']
        priority = rule['priority']
        
        reasoning = f"根据原则「{principle}」，"
        
        if priority == 'critic':
            reasoning += "质量是系统的生命线，批判者的审查必须得到尊重。"
        elif priority == 'coordinator':
            reasoning += "健康是长期产出的基础，协调者的休息建议必须执行。"
        elif priority == 'planner':
            reasoning += "正确的方向比快速执行更重要，规划者的计划应当遵循。"
        elif priority == 'learner':
            reasoning += "系统进化是长期竞争力的保证，学习者的更新需求应当满足。"
        else:
            reasoning += "需要综合考虑双方观点，寻求最优解。"
        
        return reasoning
    
    def _suggest_evolution(self, persona_health: dict, system_health: dict) -> list:
        """生成元进化建议"""
        suggestions = []
        
        # 检查各人格健康状态
        for persona_id, health in persona_health.items():
            if health['status'] == 'critical':
                suggestions.append({
                    'type': 'urgent_fix',
                    'target': persona_id,
                    'description': f"{health['name']} 状态危急 (分数：{health['score']})",
                    'suggestion': f'立即检查 {health["name"]} 执行逻辑，修复潜在问题',
                    'priority': 'high',
                    'estimated_impact': 'high'
                })
            elif health['status'] == 'warning':
                suggestions.append({
                    'type': 'optimization',
                    'target': persona_id,
                    'description': f"{health['name']} 状态不佳 (分数：{health['score']})",
                    'suggestion': f'优化 {health["name"]} 工作流程，提升性能',
                    'priority': 'medium',
                    'estimated_impact': 'medium'
                })
        
        # 检查系统指标
        for metric_id, health in system_health.items():
            if health['status'] == 'critical':
                suggestions.append({
                    'type': 'system_alert',
                    'target': metric_id,
                    'description': f"{health['name']} 超限 (值：{health['value']})",
                    'suggestion': f'立即干预：{self._get_intervention_suggestion(metric_id)}',
                    'priority': 'high',
                    'estimated_impact': 'high'
                })
        
        # 定期进化建议
        if not suggestions:
            suggestions.append({
                'type': 'routine_review',
                'target': 'system',
                'description': '系统运行正常',
                'suggestion': '建议进行例行审查，寻找优化机会',
                'priority': 'low',
                'estimated_impact': 'low'
            })
        
        return suggestions
    
    def _get_intervention_suggestion(self, metric_id: str) -> str:
        """获取干预建议"""
        suggestions = {
            'continuous_work_minutes': '强制休息 15 分钟，启动协调者干预',
            'critic_avg_score': '检查批判者评分标准，可能需要调整阈值',
            'task_backlog': '暂停新任务，优先处理积压任务',
            'persona_conflicts': '启动冲突调解流程，元认知介入仲裁'
        }
        return suggestions.get(metric_id, '需要人工审查')
    
    def _generate_risk_warnings(self, system_health: dict) -> list:
        """生成风险预警"""
        warnings = []
        
        for metric_id, health in system_health.items():
            if health['status'] == 'critical':
                warnings.append({
                    'level': 'critical',
                    'metric': health['name'],
                    'value': health['value'],
                    'threshold': health['thresholds']['danger'],
                    'message': f'严重风险：{health["name"]} 已达危险水平 ({health["value"]})',
                    'action': self._get_intervention_suggestion(metric_id)
                })
            elif health['status'] == 'warning':
                warnings.append({
                    'level': 'warning',
                    'metric': health['name'],
                    'value': health['value'],
                    'threshold': health['thresholds']['warning'],
                    'message': f'风险预警：{health["name"]} 接近警戒线 ({health["value"]})',
                    'action': f'建议关注 {health["name"]} 趋势'
                })
        
        return warnings
    
    def _calculate_overall_score(self, persona_health: dict, system_health: dict) -> int:
        """计算综合评分"""
        # 人格健康平均分 (60% 权重)
        persona_scores = [h['score'] for h in persona_health.values()]
        persona_avg = sum(persona_scores) / len(persona_scores) if persona_scores else 85
        
        # 系统健康分 (40% 权重)
        system_scores = []
        for health in system_health.values():
            if health['status'] == 'healthy':
                system_scores.append(100)
            elif health['status'] == 'warning':
                system_scores.append(70)
            else:
                system_scores.append(40)
        
        system_avg = sum(system_scores) / len(system_scores) if system_scores else 85
        
        # 综合评分
        overall = int(persona_avg * 0.6 + system_avg * 0.4)
        return max(0, min(100, overall))
    
    def _generate_recommendation(self, overall_score: int, risk_warnings: list) -> str:
        """生成建议"""
        if risk_warnings:
            critical_warnings = [w for w in risk_warnings if w['level'] == 'critical']
            if critical_warnings:
                return '立即干预 - 存在严重风险'
            else:
                return '尽快处理 - 存在风险预警'
        
        if overall_score >= 90:
            return '系统优秀 - 保持当前状态'
        elif overall_score >= 80:
            return '系统良好 - 持续监控'
        elif overall_score >= 70:
            return '系统需改进 - 建议优化'
        else:
            return '系统需关注 - 建议审查'
    
    def _calculate_next_check_time(self, risk_warnings: list) -> str:
        """计算下次检查时间"""
        if any(w['level'] == 'critical' for w in risk_warnings):
            # 严重风险：15 分钟后检查
            next_check = datetime.now() + timedelta(minutes=15)
        elif any(w['level'] == 'warning' for w in risk_warnings):
            # 风险预警：30 分钟后检查
            next_check = datetime.now() + timedelta(minutes=30)
        else:
            # 正常：2 小时后检查
            next_check = datetime.now() + timedelta(hours=2)
        
        return next_check.isoformat()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read().strip())
    
    agent = MetacognitiveAgent()
    result = agent.process(input_data.get("system_state", {}), input_data.get("context", {}))
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
