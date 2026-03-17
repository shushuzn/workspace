#!/usr/bin/env python3
"""
7-Persona Collaboration System v2.0
多人格协作引擎 - 并行执行 + 消息队列 + 状态管理
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class PersonaMessage:
    """人格消息"""
    message_id: str
    timestamp: str
    sender: str
    receiver: str
    priority: str
    payload: dict
    status: str = "pending"

@dataclass
class TaskLog:
    """任务日志"""
    task_id: str
    persona: str
    action: str
    status: str
    duration: str
    timestamp: str

class PersonaMessageQueue:
    """人格消息队列"""
    
    def __init__(self, log_dir: str = "persona-logs"):
        self.log_dir = log_dir
        self.queues: Dict[str, List[PersonaMessage]] = {
            'planner': [],
            'executor': [],
            'critic': [],
            'learner': [],
            'coordinator': [],
            'innovator': [],
            'metacognition': []
        }
        os.makedirs(log_dir, exist_ok=True)
    
    def generate_message_id(self) -> str:
        """生成唯一消息 ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"MSG-{timestamp}"
    
    def send(self, sender: str, receiver: str, payload: dict, priority: str = "normal") -> str:
        """发送消息到队列"""
        message = PersonaMessage(
            message_id=self.generate_message_id(),
            timestamp=datetime.now().isoformat(),
            sender=sender,
            receiver=receiver,
            priority=priority,
            payload=payload,
            status="pending"
        )
        
        if receiver in self.queues:
            self.queues[receiver].append(message)
            self._log_message(message)
            print(f"[QUEUE] {sender} → {receiver}: {message.message_id}")
            return message.message_id
        else:
            raise ValueError(f"Unknown receiver: {receiver}")
    
    def receive(self, receiver: str) -> List[PersonaMessage]:
        """接收消息"""
        messages = self.queues.get(receiver, [])
        self.queues[receiver] = []
        return messages
    
    def _log_message(self, message: PersonaMessage):
        """记录消息日志"""
        log_file = os.path.join(self.log_dir, f"messages-{datetime.now().strftime('%Y%m%d')}.json")
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []
        
        logs.append(asdict(message))
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

class PersonaStateManager:
    """人格状态管理器"""
    
    def __init__(self, log_dir: str = "persona-logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log(self, task_id: str, persona: str, action: str, status: str, duration: str):
        """记录任务日志"""
        log_entry = TaskLog(
            task_id=task_id,
            persona=persona,
            action=action,
            status=status,
            duration=duration,
            timestamp=datetime.now().isoformat()
        )
        
        log_file = os.path.join(self.log_dir, f"{task_id}.md")
        
        # 如果是新任务，创建表头
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write(f"# Task Log: {task_id}\n\n")
                f.write(f"Created: {datetime.now().isoformat()}\n\n")
                f.write("| Timestamp | Persona | Action | Status | Duration |\n")
                f.write("|-----------|---------|--------|--------|----------|\n")
        
        # 追加日志
        with open(log_file, 'a') as f:
            f.write(f"| {log_entry.timestamp} | {persona} | {action} | {status} | {duration} |\n")
    
    def get_metrics(self, task_id: str) -> dict:
        """获取任务指标"""
        log_file = os.path.join(self.log_dir, f"{task_id}.md")
        
        if not os.path.exists(log_file):
            return {"error": "Task not found"}
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # 解析日志
        logs = []
        for line in lines[5:]:  # 跳过表头
            if line.startswith('|'):
                parts = line.strip().split('|')
                if len(parts) >= 6:
                    logs.append({
                        'timestamp': parts[1].strip(),
                        'persona': parts[2].strip(),
                        'action': parts[3].strip(),
                        'status': parts[4].strip(),
                        'duration': parts[5].strip()
                    })
        
        # 计算指标
        total_time = sum([int(log['duration'].replace('min', '')) for log in logs if 'min' in log['duration']])
        persona_count = len(set([log['persona'] for log in logs]))
        
        return {
            'task_id': task_id,
            'total_steps': len(logs),
            'total_time_min': total_time,
            'personas_involved': persona_count,
            'logs': logs
        }

class PersonaCritic:
    """批判者评分系统"""
    
    @staticmethod
    def evaluate(deliverables: dict, requirements: dict) -> dict:
        """评估交付物"""
        scores = {
            'accuracy': PersonaCritic._score_accuracy(deliverables, requirements),
            'completeness': PersonaCritic._score_completeness(deliverables, requirements),
            'efficiency': PersonaCritic._score_efficiency(deliverables),
            'maintainability': PersonaCritic._score_maintainability(deliverables),
            'innovation': PersonaCritic._score_innovation(deliverables)
        }
        
        # 加权评分
        weights = {'accuracy': 0.30, 'completeness': 0.25, 'efficiency': 0.20, 
                   'maintainability': 0.15, 'innovation': 0.10}
        
        weighted_score = sum(scores[dim] * weights[dim] for dim in scores)
        
        decision = "pass" if weighted_score >= 85 else ("fix" if weighted_score >= 70 else "redo")
        
        return {
            'scores': scores,
            'weighted_score': round(weighted_score, 1),
            'decision': decision,
            'feedback': PersonaCritic._generate_feedback(scores),
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def _score_accuracy(deliverables: dict, requirements: dict) -> int:
        """准确性评分 (0-100)"""
        # 检查错误数量
        errors = deliverables.get('errors', 0)
        if errors == 0:
            return 95
        elif errors <= 2:
            return 80
        else:
            return 60
    
    @staticmethod
    def _score_completeness(deliverables: dict, requirements: dict) -> int:
        """完整性评分 (0-100)"""
        required = requirements.get('deliverables', [])
        completed = deliverables.get('deliverables', [])
        
        if len(required) == 0:
            return 100
        
        completion_rate = len(completed) / len(required)
        return min(100, int(completion_rate * 100))
    
    @staticmethod
    def _score_efficiency(deliverables: dict) -> int:
        """效率评分 (0-100)"""
        estimated_time = deliverables.get('estimated_time', 30)
        actual_time = deliverables.get('actual_time', 30)
        
        if actual_time <= estimated_time:
            return 95
        elif actual_time <= estimated_time * 1.2:
            return 85
        else:
            return 70
    
    @staticmethod
    def _score_maintainability(deliverables: dict) -> int:
        """可维护性评分 (0-100)"""
        has_docs = deliverables.get('has_documentation', True)
        has_tests = deliverables.get('has_tests', False)
        has_comments = deliverables.get('has_comments', True)
        
        score = 70
        if has_docs:
            score += 15
        if has_tests:
            score += 10
        if has_comments:
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def _score_innovation(deliverables: dict) -> int:
        """创新性评分 (0-100)"""
        innovations = deliverables.get('innovations', 0)
        
        if innovations >= 2:
            return 95
        elif innovations == 1:
            return 85
        else:
            return 70
    
    @staticmethod
    def _generate_feedback(scores: dict) -> List[str]:
        """生成反馈"""
        feedback = []
        
        if scores['accuracy'] >= 90:
            feedback.append("✅ 准确性优秀，零错误")
        elif scores['accuracy'] >= 80:
            feedback.append("⚠️ 准确性良好，有小错误")
        else:
            feedback.append("❌ 准确性需改进，有大错误")
        
        if scores['completeness'] >= 90:
            feedback.append("✅ 完整性优秀，所有需求满足")
        elif scores['completeness'] >= 80:
            feedback.append("⚠️ 完整性良好，部分需求未满足")
        else:
            feedback.append("❌ 完整性不足，缺失关键需求")
        
        if scores['efficiency'] >= 90:
            feedback.append("✅ 效率优秀，超出预期")
        elif scores['efficiency'] >= 80:
            feedback.append("⚠️ 效率良好，符合预期")
        else:
            feedback.append("❌ 效率需改进，低于预期")
        
        return feedback

class PersonaInnovator:
    """创新者评估系统"""
    
    @staticmethod
    def evaluate_innovation(problem: str, solution: str) -> dict:
        """评估创新方案"""
        # 简化评估 (实际应更复杂)
        evaluation = {
            'impact': 85,  # 影响力
            'feasibility': 90,  # 可行性
            'novelty': 80,  # 新颖性
            'efficiency': 88  # 效率
        }
        
        weights = {'impact': 0.40, 'feasibility': 0.30, 'novelty': 0.20, 'efficiency': 0.10}
        weighted_score = sum(evaluation[dim] * weights[dim] for dim in evaluation)
        
        decision = "implement" if weighted_score >= 85 else ("optimize" if weighted_score >= 70 else "defer")
        
        return {
            'problem': problem,
            'solution': solution,
            'evaluation': evaluation,
            'weighted_score': round(weighted_score, 1),
            'decision': decision,
            'timestamp': datetime.now().isoformat()
        }

def demo_persona_collaboration():
    """演示多人格协作"""
    print("=" * 60)
    print("7-Persona Collaboration System v2.0 Demo")
    print("=" * 60)
    
    # 初始化
    queue = PersonaMessageQueue()
    state = PersonaStateManager()
    critic = PersonaCritic()
    innovator = PersonaInnovator()
    
    task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 1. 规划者 → 执行者
    print("\n[1] 规划者制定计划...")
    plan = {
        'task_id': task_id,
        'subtasks': ['分析', '实施', '测试'],
        'estimated_time': '30min'
    }
    queue.send('planner', 'executor', plan)
    state.log(task_id, 'planner', '制定计划', 'success', '3min')
    
    # 2. 执行者执行
    print("\n[2] 执行者执行任务...")
    time.sleep(1)  # 模拟执行
    deliverables = {
        'task_id': task_id,
        'deliverables': ['optimized_script.py'],
        'errors': 0,
        'estimated_time': 30,
        'actual_time': 25,
        'has_documentation': True,
        'has_tests': True,
        'has_comments': True,
        'innovations': 1
    }
    queue.send('executor', 'critic', deliverables)
    state.log(task_id, 'executor', '执行任务', 'success', '25min')
    
    # 3. 创新者并行扫描
    print("\n[3] 创新者提出方案...")
    innovation = innovator.evaluate_innovation(
        "顺序执行导致延迟高",
        "并行执行核心流程"
    )
    print(f"创新评分：{innovation['weighted_score']} - {innovation['decision']}")
    state.log(task_id, 'innovator', '提出创新', 'success', '5min')
    
    # 4. 批判者审查
    print("\n[4] 批判者质量审查...")
    requirements = {'deliverables': ['optimized_script.py']}
    evaluation = critic.evaluate(deliverables, requirements)
    print(f"批判者评分：{evaluation['weighted_score']} - {evaluation['decision']}")
    state.log(task_id, 'critic', '质量审查', 'success', '5min')
    
    # 5. 学习者更新记忆 (如果评分≥85)
    if evaluation['weighted_score'] >= 85:
        print("\n[5] 学习者更新记忆...")
        state.log(task_id, 'learner', '更新记忆', 'success', '3min')
    
    # 6. 获取指标
    print("\n[6] 任务指标:")
    metrics = state.get_metrics(task_id)
    print(f"总步骤：{metrics['total_steps']}")
    print(f"总时间：{metrics['total_time_min']}min")
    print(f"参与人格：{metrics['personas_involved']}")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)

if __name__ == "__main__":
    demo_persona_collaboration()
