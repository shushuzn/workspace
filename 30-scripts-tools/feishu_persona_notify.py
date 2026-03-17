#!/usr/bin/env python3
"""
7-Persona Feishu Notification Integration
==========================================
Sends aggregated 7-persona status updates to Feishu.

Features:
- Aggregated daily summary (23:00)
- Immediate alerts for critical issues
- 7 persona-specific templates
- Quality score tracking

Usage:
    # Send persona status
    python feishu-persona-notify.py --status --score 94
    
    # Send critical alert
    python feishu-persona-notify.py --alert --persona 批判者 --score 70
    
    # Send daily summary
    python feishu-persona-notify.py --daily-summary
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from feishu_card_templates import CardTemplateLibrary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class PersonaNotifyConfig:
    """Configuration for persona notifications"""
    
    # Feishu settings
    FEISHU_USER_ID = os.getenv('FEISHU_USER_ID', 'ou_72a847b95fc25870dcdd8ce56d929252')
    
    # Notification thresholds
    CRITICAL_SCORE_THRESHOLD = 70  # Send immediate alert if < 70
    WARNING_SCORE_THRESHOLD = 85   # Send warning if < 85
    
    # Daily summary time
    DAILY_SUMMARY_TIME = "23:00"
    
    # Persona metadata
    PERSONA_INFO = {
        '规划者': {'emoji': '🎯', 'color': 'blue', 'priority': 'P1'},
        '执行者': {'emoji': '⚡', 'color': 'green', 'priority': 'P1'},
        '批判者': {'emoji': '🔍', 'color': 'purple', 'priority': 'P0'},
        '学习者': {'emoji': '📚', 'color': 'blue', 'priority': 'P1'},
        '协调者': {'emoji': '⚖️', 'color': 'grey', 'priority': 'P2'},
        '创新者': {'emoji': '💡', 'color': 'yellow', 'priority': 'P1'},
        '元认知': {'emoji': '🧠', 'color': 'purple', 'priority': 'P1'}
    }


# ============================================================================
# Persona Notification Manager
# ============================================================================

class PersonaNotificationManager:
    """Manager for 7-persona Feishu notifications"""
    
    def __init__(self):
        self.card_lib = CardTemplateLibrary()
        self.config = PersonaNotifyConfig()
        self._import_feishu_api()
    
    def _import_feishu_api(self):
        """Import Feishu API"""
        try:
            from feishu_api import FeishuAPI
            self.feishu = FeishuAPI()
        except ImportError:
            logger.warning("FeishuAPI not available, notifications will be logged only")
            self.feishu = None
    
    def _get_persona_emoji(self, persona_name: str) -> str:
        """Get emoji for persona"""
        return self.config.PERSONA_INFO.get(persona_name, {}).get('emoji', '•')
    
    def _get_persona_priority(self, persona_name: str, score: float) -> str:
        """Get notification priority based on persona and score"""
        if score < self.config.CRITICAL_SCORE_THRESHOLD:
            return 'P0'  # Critical
        elif score < self.config.WARNING_SCORE_THRESHOLD:
            return 'P1'  # Warning
        else:
            return 'P2'  # Normal
    
    def send_persona_status(
        self,
        persona_name: str,
        status: str,
        score: float,
        details: str = '',
        immediate: bool = False
    ):
        """
        Send single persona status update
        
        Args:
            persona_name: Name of persona (规划者/执行者/etc.)
            status: success/failed/skipped
            score: Score 0-100
            details: Additional details
            immediate: Send immediately vs batch
        """
        emoji = self._get_persona_emoji(persona_name)
        priority = self._get_persona_priority(persona_name, score)
        
        # Check if immediate alert needed
        if score < self.config.CRITICAL_SCORE_THRESHOLD:
            content = f"🚨 **紧急**: {emoji} {persona_name} 评分过低 ({score}/100)\n\n{details}"
            self._send_alert(persona_name, content, priority='P0')
            return
        
        # Create status card
        persona_states = {
            persona_name: {
                'status': status,
                'score': score,
                'details': details
            }
        }
        
        card = self.card_lib.create_persona_status(
            persona_states=persona_states,
            overall_score=score,
            summary=f"{emoji} {persona_name} 执行{status}"
        )
        
        if immediate and priority in ['P0', 'P1']:
            self._send_card(card, priority)
        else:
            logger.info(f"[BATCH] {persona_name}: {status} ({score}/100)")
    
    def send_aggregated_status(
        self,
        persona_states: Dict[str, Dict],
        overall_score: float,
        summary: str = ''
    ):
        """
        Send aggregated 7-persona status
        
        Args:
            persona_states: Dict of persona_name -> {status, score, details}
            overall_score: Overall system score
            summary: Summary text
        """
        card = self.card_lib.create_persona_status(
            persona_states=persona_states,
            overall_score=overall_score,
            summary=summary
        )
        
        # Determine priority based on overall score
        if overall_score < self.config.CRITICAL_SCORE_THRESHOLD:
            priority = 'P0'
        elif overall_score < self.config.WARNING_SCORE_THRESHOLD:
            priority = 'P1'
        else:
            priority = 'P2'
        
        self._send_card(card, priority)
        logger.info(f"Aggregated status sent: {overall_score}/100")
    
    def send_daily_summary(
        self,
        daily_stats: Dict
    ):
        """
        Send daily summary at 23:00
        
        Args:
            daily_stats: Dict with daily statistics
                - total_tasks: int
                - avg_score: float
                - critical_alerts: int
                - innovations: int
                - memory_updates: int
        """
        # Format content
        content = f"""**今日统计** ({datetime.now().strftime('%Y-%m-%d')})

📊 **任务总数**: {daily_stats.get('total_tasks', 0)}
⭐ **平均评分**: {daily_stats.get('avg_score', 0):.1f}/100
🚨 **紧急告警**: {daily_stats.get('critical_alerts', 0)}
💡 **创新方案**: {daily_stats.get('innovations', 0)}
📚 **记忆更新**: {daily_stats.get('memory_updates', 0)}"""
        
        card = self.card_lib.create_system_notification(
            title="7 人格系统日报",
            subtitle=f"每日总结 - {datetime.now().strftime('%Y-%m-%d')}",
            content=content,
            link_text="查看详情",
            link_url=""
        )
        
        self._send_card(card, 'P2')
        logger.info("Daily summary sent")
    
    def _send_alert(self, persona_name: str, content: str, priority: str = 'P0'):
        """Send critical alert"""
        if self.feishu:
            try:
                # Add @all for P0 alerts
                if priority == 'P0':
                    content += "\n\n<at user_id=\"all\">所有人</at>"
                
                self.feishu.send_text(content, self.config.FEISHU_USER_ID)
                logger.info(f"Alert sent: {persona_name} ({priority})")
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
        else:
            logger.info(f"[ALERT] {persona_name}: {content}")
    
    def _send_card(self, card: Dict, priority: str = 'P2'):
        """Send card message"""
        if self.feishu:
            try:
                self.feishu.send_card(card, self.config.FEISHU_USER_ID)
                logger.info(f"Card sent ({priority})")
            except Exception as e:
                logger.error(f"Failed to send card: {e}")
        else:
            logger.info(f"[CARD] {json.dumps(card, ensure_ascii=False)[:200]}...")


# ============================================================================
# CLI Interface
# ============================================================================

def send_status(args):
    """Send persona status"""
    manager = PersonaNotificationManager()
    
    persona_states = {}
    
    if args.persona:
        # Single persona
        persona_states[args.persona] = {
            'status': 'success' if args.score >= 85 else 'failed',
            'score': args.score,
            'details': args.details or ''
        }
        manager.send_persona_status(
            persona_name=args.persona,
            status=persona_states[args.persona]['status'],
            score=args.score,
            details=args.details,
            immediate=args.immediate
        )
    else:
        # All personas (demo)
        persona_states = {
            '规划者': {'status': 'success', 'score': 96, 'details': '任务分解清晰'},
            '执行者': {'status': 'success', 'score': 95, 'details': '代码质量优秀'},
            '批判者': {'status': 'success', 'score': 93, 'details': '审查通过'},
            '学习者': {'status': 'success', 'score': 94, 'details': '记忆已更新'},
            '协调者': {'status': 'success', 'score': 90, 'details': '时间检查完成'},
            '创新者': {'status': 'success', 'score': 95, 'details': '3 个创新方案'},
            '元认知': {'status': 'success', 'score': 91, 'details': '系统健康'}
        }
        
        manager.send_aggregated_status(
            persona_states=persona_states,
            overall_score=args.score or 94,
            summary="7 人格系统运行正常"
        )


def send_alert(args):
    """Send critical alert"""
    manager = PersonaNotificationManager()
    
    manager.send_persona_status(
        persona_name=args.persona,
        status='failed',
        score=args.score,
        details=args.details or '需要立即关注',
        immediate=True
    )


def send_daily_summary(args):
    """Send daily summary"""
    manager = PersonaNotificationManager()
    
    daily_stats = {
        'total_tasks': args.tasks or 10,
        'avg_score': args.avg_score or 90.0,
        'critical_alerts': args.alerts or 0,
        'innovations': args.innovations or 3,
        'memory_updates': args.memory or 5
    }
    
    manager.send_daily_summary(daily_stats)


def main():
    parser = argparse.ArgumentParser(
        description='7-Persona Feishu Notification Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send single persona status
  python feishu-persona-notify.py --status --persona 批判者 --score 93
  
  # Send aggregated status (all personas)
  python feishu-persona-notify.py --status --score 94
  
  # Send critical alert
  python feishu-persona-notify.py --alert --persona 批判者 --score 65 --details "质量不达标"
  
  # Send daily summary
  python feishu-persona-notify.py --daily-summary --tasks 15 --avg-score 92.5
        """
    )
    
    parser.add_argument('--status', action='store_true', help='Send persona status')
    parser.add_argument('--alert', action='store_true', help='Send critical alert')
    parser.add_argument('--daily-summary', action='store_true', help='Send daily summary')
    
    parser.add_argument('--persona', type=str, help='Persona name (规划者/执行者/etc.)')
    parser.add_argument('--score', type=float, help='Score (0-100)')
    parser.add_argument('--details', type=str, help='Additional details')
    parser.add_argument('--immediate', action='store_true', help='Send immediately')
    
    parser.add_argument('--tasks', type=int, help='Daily task count')
    parser.add_argument('--avg-score', type=float, help='Daily average score')
    parser.add_argument('--alerts', type=int, help='Critical alert count')
    parser.add_argument('--innovations', type=int, help='Innovation count')
    parser.add_argument('--memory', type=int, help='Memory update count')
    
    args = parser.parse_args()
    
    if args.status:
        send_status(args)
    elif args.alert:
        send_alert(args)
    elif args.daily_summary:
        send_daily_summary(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
