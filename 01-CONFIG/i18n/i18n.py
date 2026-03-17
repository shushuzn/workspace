#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n - Internationalization Support
国际化支持 - 中英双语

Author: Claw 🐾
Version: 1.0
"""

from typing import Dict


# ============== 双语翻译字典 ==============

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Persona Names
    'planner': {'zh': '规划者', 'en': 'Planner'},
    'executor': {'zh': '执行者', 'en': 'Executor'},
    'critic': {'zh': '批判者', 'en': 'Critic'},
    'learner': {'zh': '学习者', 'en': 'Learner'},
    'coordinator': {'zh': '协调者', 'en': 'Coordinator'},
    'innovator': {'zh': '创新者', 'en': 'Innovator'},
    'metacognition': {'zh': '元认知', 'en': 'Metacognition'},
    
    # Persona Descriptions
    'planner_desc': {'zh': '任务分解与规划', 'en': 'Task decomposition & planning'},
    'executor_desc': {'zh': '任务执行', 'en': 'Task execution'},
    'critic_desc': {'zh': '质量审查', 'en': 'Quality review'},
    'learner_desc': {'zh': '知识吸收', 'en': 'Knowledge absorption'},
    'coordinator_desc': {'zh': '资源协调', 'en': 'Resource coordination'},
    'innovator_desc': {'zh': '创意生成', 'en': 'Idea generation'},
    'metacognition_desc': {'zh': '全局监控', 'en': 'Global monitoring'},
    
    # Status
    'idle': {'zh': '空闲', 'en': 'Idle'},
    'busy': {'zh': '忙碌', 'en': 'Busy'},
    'waiting': {'zh': '等待', 'en': 'Waiting'},
    'pending': {'zh': '待处理', 'en': 'Pending'},
    'running': {'zh': '运行中', 'en': 'Running'},
    'completed': {'zh': '已完成', 'en': 'Completed'},
    'failed': {'zh': '失败', 'en': 'Failed'},
    
    # Priority
    'critical': {'zh': '紧急', 'en': 'Critical'},
    'high': {'zh': '高', 'en': 'High'},
    'medium': {'zh': '中', 'en': 'Medium'},
    'normal': {'zh': '普通', 'en': 'Normal'},
    'low': {'zh': '低', 'en': 'Low'},
    
    # API Messages
    'healthy': {'zh': '健康', 'en': 'Healthy'},
    'task_assigned': {'zh': '任务已分配', 'en': 'Task assigned'},
    'task_completed': {'zh': '任务已完成', 'en': 'Task completed'},
    'persona_not_found': {'zh': '人格未找到', 'en': 'Persona not found'},
    'unknown_persona': {'zh': '未知人格', 'en': 'Unknown persona'},
    
    # Dashboard Labels
    'dashboard_title': {'zh': '创新者仪表盘 v4.1 - 7 人格增强版', 'en': 'Innovator Dashboard v4.1 - 7-Persona Enhanced'},
    'all_personas': {'zh': '所有人格', 'en': 'All Personas'},
    'persona_status': {'zh': '人格状态', 'en': 'Persona Status'},
    'statistics': {'zh': '统计信息', 'en': 'Statistics'},
    'system_health': {'zh': '系统健康', 'en': 'System Health'},
    'task_queue': {'zh': '任务队列', 'en': 'Task Queue'},
    
    # Metrics
    'tasks_completed': {'zh': '已完成任务', 'en': 'Tasks Completed'},
    'tasks_failed': {'zh': '失败任务', 'en': 'Tasks Failed'},
    'success_rate': {'zh': '成功率', 'en': 'Success Rate'},
    'active_personas': {'zh': '活跃人格', 'en': 'Active Personas'},
    'pending_tasks': {'zh': '待处理任务', 'en': 'Pending Tasks'},
    'avg_response_time': {'zh': '平均响应时间', 'en': 'Average Response Time'},
    'last_active': {'zh': '最后活跃', 'en': 'Last Active'},
    'current_task': {'zh': '当前任务', 'en': 'Current Task'},
    
    # System
    'cpu_usage': {'zh': 'CPU 使用率', 'en': 'CPU Usage'},
    'memory_usage': {'zh': '内存使用率', 'en': 'Memory Usage'},
    'disk_usage': {'zh': '磁盘使用率', 'en': 'Disk Usage'},
    'timestamp': {'zh': '时间戳', 'en': 'Timestamp'},
    'version': {'zh': '版本', 'en': 'Version'},
    
    # Actions
    'assign_task': {'zh': '分配任务', 'en': 'Assign Task'},
    'view_queue': {'zh': '查看队列', 'en': 'View Queue'},
    'refresh': {'zh': '刷新', 'en': 'Refresh'},
    'language': {'zh': '语言', 'en': 'Language'},
}


class I18n:
    """
    国际化管理器
    Internationalization Manager
    """
    
    def __init__(self, default_lang: str = 'zh'):
        self.default_lang = default_lang
        self.supported_languages = ['zh', 'en']
    
    def t(self, key: str, lang: str = None) -> str:
        """
        Translate a key to the specified language
        翻译键到指定语言
        
        Args:
            key: Translation key
            lang: Language code ('zh' or 'en'), defaults to default_lang
            
        Returns:
            Translated string, or key if not found
        """
        if lang is None:
            lang = self.default_lang
        
        if key not in TRANSLATIONS:
            return key
        
        if lang not in TRANSLATIONS[key]:
            return TRANSLATIONS[key].get(self.default_lang, key)
        
        return TRANSLATIONS[key][lang]
    
    def get_persona_info(self, persona: str, lang: str = None) -> Dict[str, str]:
        """
        Get persona information in specified language
        获取指定语言的人格信息
        
        Args:
            persona: Persona key (e.g., 'planner')
            lang: Language code
            
        Returns:
            Dict with name, description in specified language
        """
        if lang is None:
            lang = self.default_lang
        
        return {
            'name': self.t(persona, lang),
            'description': self.t(f'{persona}_desc', lang)
        }
    
    def set_language(self, lang: str):
        """
        Set default language
        设置默认语言
        
        Args:
            lang: Language code ('zh' or 'en')
        """
        if lang in self.supported_languages:
            self.default_lang = lang
    
    def get_supported_languages(self) -> list:
        """Get supported language codes"""
        return self.supported_languages.copy()


# Global instance
i18n = I18n(default_lang='zh')


def t(key: str, lang: str = None) -> str:
    """Convenience function for translation"""
    return i18n.t(key, lang)


def get_persona_info(persona: str, lang: str = None) -> Dict[str, str]:
    """Convenience function for persona info"""
    return i18n.get_persona_info(persona, lang)


if __name__ == '__main__':
    # Test
    print("Testing i18n...")
    print("\nChinese (zh):")
    for key in ['planner', 'executor', 'critic', 'healthy', 'tasks_completed']:
        print(f"  {key}: {t(key, 'zh')}")
    
    print("\nEnglish (en):")
    for key in ['planner', 'executor', 'critic', 'healthy', 'tasks_completed']:
        print(f"  {key}: {t(key, 'en')}")
    
    print("\nPersona Info (zh):")
    print(get_persona_info('planner', 'zh'))
    
    print("\nPersona Info (en):")
    print(get_persona_info('planner', 'en'))
