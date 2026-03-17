#!/usr/bin/env python3
"""
Feishu Card Templates Library
==============================
Reusable interactive card templates for common notification scenarios.

Templates:
- System Notification (blue)
- Security Alert (red)
- Data Report (green)
- Task Completion (yellow)
- 7-Persona Status (purple)

Usage:
    from feishu_card_templates import CardTemplateLibrary
    
    lib = CardTemplateLibrary()
    card = lib.create_system_notification("Task", "Completed", "Details...")
    api.send_card(card)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class CardTemplateLibrary:
    """Library of reusable Feishu card templates"""
    
    # Color templates
    COLOR_BLUE = 'blue'
    COLOR_RED = 'red'
    COLOR_GREEN = 'green'
    COLOR_YELLOW = 'yellow'
    COLOR_PURPLE = 'purple'
    COLOR_GREY = 'grey'
    
    def __init__(self):
        self.templates = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Register default card templates"""
        self.templates['system_notification'] = self.create_system_notification
        self.templates['security_alert'] = self.create_security_alert
        self.templates['data_report'] = self.create_data_report
        self.templates['task_completion'] = self.create_task_completion
        self.templates['persona_status'] = self.create_persona_status
        self.templates['approval_request'] = self.create_approval_request
    
    # ========================================================================
    # Template: System Notification
    # ========================================================================
    
    def create_system_notification(
        self,
        title: str,
        subtitle: str,
        content: str,
        link_url: str = '',
        link_text: str = '查看详情'
    ) -> Dict:
        """
        Create system notification card (blue)
        
        Args:
            title: Main title (e.g., "系统通知")
            subtitle: Subtitle (e.g., "Git 安全扫描完成")
            content: Markdown content
            link_url: Optional detail URL
            link_text: Link button text
        """
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": self.COLOR_BLUE,
                "title": {
                    "tag": "plain_text",
                    "content": f"🔔 {title}"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**时间**\n{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**类型**\n{subtitle}"
                            }
                        }
                    ]
                },
                {
                    "tag": "divider"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
        
        # Add action button if URL provided
        if link_url:
            card["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": link_text
                        },
                        "url": link_url,
                        "type": "primary"
                    }
                ]
            })
        
        return card
    
    # ========================================================================
    # Template: Security Alert
    # ========================================================================
    
    def create_security_alert(
        self,
        alert_type: str,
        severity: str,
        details: str,
        file_path: str = '',
        commit_hash: str = '',
        action_url: str = ''
    ) -> Dict:
        """
        Create security alert card (red)
        
        Args:
            alert_type: Alert type (e.g., "Token 泄露", "敏感文件")
            severity: CRITICAL/HIGH/MEDIUM/LOW
            details: Alert details
            file_path: Optional file path
            commit_hash: Optional commit hash
            action_url: Action URL
        """
        # Severity color mapping
        severity_colors = {
            'CRITICAL': self.COLOR_RED,
            'HIGH': self.COLOR_RED,
            'MEDIUM': self.COLOR_YELLOW,
            'LOW': self.COLOR_BLUE
        }
        
        # Severity emoji
        severity_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '⚡',
            'LOW': 'ℹ️'
        }
        
        color = severity_colors.get(severity, self.COLOR_BLUE)
        emoji = severity_emoji.get(severity, 'ℹ️')
        
        content = f"""**告警类型**: {alert_type}
**严重级别**: {severity}
**详细信息**: {details}"""
        
        if file_path:
            content += f"\n**文件路径**: `{file_path}`"
        
        if commit_hash:
            content += f"\n**提交哈希**: `{commit_hash[:7]}`"
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": color,
                "title": {
                    "tag": "plain_text",
                    "content": f"{emoji} 安全告警"
                }
            },
            "elements": [
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "请立即处理！" if severity in ['CRITICAL', 'HIGH'] else "请及时查看"
                        }
                    ]
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
        
        if action_url:
            card["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "立即处理"
                        },
                        "url": action_url,
                        "type": "primary"
                    }
                ]
            })
        
        return card
    
    # ========================================================================
    # Template: Data Report
    # ========================================================================
    
    def create_data_report(
        self,
        title: str,
        period: str,
        metrics: Dict[str, str],
        trend_analysis: str = '',
        chart_url: str = ''
    ) -> Dict:
        """
        Create data report card (green)
        
        Args:
            title: Report title
            period: Time period (e.g., "2026-03-17")
            metrics: Dict of metric name -> value
            trend_analysis: Optional trend analysis text
            chart_url: Optional chart image URL
        """
        # Format metrics
        metrics_content = "\n".join([f"**{k}**: {v}" for k, v in metrics.items()])
        
        elements = [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**周期**\n{period}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**生成时间**\n{datetime.now().strftime('%H:%M')}"
                        }
                    }
                ]
            },
            {
                "tag": "divider"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**关键指标**\n{metrics_content}"
                }
            }
        ]
        
        if trend_analysis:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**趋势分析**\n{trend_analysis}"
                }
            })
        
        if chart_url:
            elements.append({
                "tag": "img",
                "img_key": chart_url,
                "alt": {
                    "tag": "plain_text",
                    "content": "Chart"
                }
            })
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": self.COLOR_GREEN,
                "title": {
                    "tag": "plain_text",
                    "content": f"📊 {title}"
                }
            },
            "elements": elements
        }
        
        return card
    
    # ========================================================================
    # Template: Task Completion
    # ========================================================================
    
    def create_task_completion(
        self,
        task_name: str,
        status: str,
        duration: str = '',
        details: str = '',
        artifacts: List[Dict] = None
    ) -> Dict:
        """
        Create task completion card (yellow)
        
        Args:
            task_name: Task name
            status: success/failed/skipped
            duration: Task duration
            details: Additional details
            artifacts: List of {name, url} for outputs
        """
        # Status styling
        status_config = {
            'success': (self.COLOR_GREEN, '✅', '完成'),
            'failed': (self.COLOR_RED, '❌', '失败'),
            'skipped': (self.COLOR_GREY, '⏭️', '跳过')
        }
        
        color, emoji, status_text = status_config.get(status, (self.COLOR_BLUE, 'ℹ️', status))
        
        content = f"**任务**: {task_name}\n**状态**: {emoji} {status_text}"
        
        if duration:
            content += f"\n**耗时**: {duration}"
        
        if details:
            content += f"\n\n{details}"
        
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            }
        ]
        
        # Add artifact links
        if artifacts:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": artifact['name']
                        },
                        "url": artifact.get('url', '#'),
                        "type": "default"
                    }
                    for artifact in artifacts
                ]
            })
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": color,
                "title": {
                    "tag": "plain_text",
                    "content": "📋 任务完成"
                }
            },
            "elements": elements
        }
        
        return card
    
    # ========================================================================
    # Template: 7-Persona Status
    # ========================================================================
    
    def create_persona_status(
        self,
        persona_states: Dict[str, Dict],
        overall_score: float,
        summary: str = ''
    ) -> Dict:
        """
        Create 7-persona status card (purple)
        
        Args:
            persona_states: Dict of persona_name -> {status, score, details}
            overall_score: Overall system score (0-100)
            summary: Optional summary text
        """
        # Persona emoji mapping
        persona_emoji = {
            '规划者': '🎯',
            '执行者': '⚡',
            '批判者': '🔍',
            '学习者': '📚',
            '协调者': '⚖️',
            '创新者': '💡',
            '元认知': '🧠'
        }
        
        # Format persona states
        persona_content = ""
        for name, state in persona_states.items():
            emoji = persona_emoji.get(name, '•')
            status_icon = '✅' if state.get('status') == 'success' else '❌'
            score = state.get('score', 'N/A')
            details = state.get('details', '')
            
            persona_content += f"{emoji} **{name}**: {status_icon} ({score}/100)\n"
            if details:
                persona_content += f"  └─ {details}\n"
        
        # Score color
        if overall_score >= 90:
            score_color = self.COLOR_GREEN
            score_emoji = '🏆'
        elif overall_score >= 80:
            score_color = self.COLOR_BLUE
            score_emoji = '👍'
        elif overall_score >= 70:
            score_color = self.COLOR_YELLOW
            score_emoji = '⚠️'
        else:
            score_color = self.COLOR_RED
            score_emoji = '🚨'
        
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**综合评分**: {score_emoji} {overall_score}/100"
                }
            },
            {
                "tag": "divider"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": persona_content
                }
            }
        ]
        
        if summary:
            elements.append({
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": summary
                    }
                ]
            })
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": score_color,
                "title": {
                    "tag": "plain_text",
                    "content": "🎭 7 人格系统状态"
                }
            },
            "elements": elements
        }
        
        return card
    
    # ========================================================================
    # Template: Approval Request
    # ========================================================================
    
    def create_approval_request(
        self,
        title: str,
        description: str,
        approver: str,
        deadline: str,
        callback_url: str,
        approve_value: str = 'approved',
        reject_value: str = 'rejected'
    ) -> Dict:
        """
        Create approval request card (purple)
        
        Args:
            title: Approval title
            description: What needs approval
            approver: Who should approve
            deadline: Approval deadline
            callback_url: URL for button callbacks
            approve_value: Value sent on approve
            reject_value: Value sent on reject
        """
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": self.COLOR_PURPLE,
                "title": {
                    "tag": "plain_text",
                    "content": "✅ 审批请求"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**审批人**\n{approver}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**截止时间**\n{deadline}"
                            }
                        }
                    ]
                },
                {
                    "tag": "divider"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**事项**: {title}\n\n{description}"
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "✅ 批准"
                            },
                            "type": "primary",
                            "value": json.dumps({
                                "action": "approve",
                                "value": approve_value
                            })
                        },
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "❌ 拒绝"
                            },
                            "type": "danger",
                            "value": json.dumps({
                                "action": "reject",
                                "value": reject_value
                            })
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"超时未处理将自动升级"
                        }
                    ]
                }
            ]
        }
        
        return card
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def get_template(self, name: str):
        """Get template function by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        return list(self.templates.keys())
    
    def render_card(self, template_name: str, **kwargs) -> str:
        """Render card to JSON string"""
        template_func = self.get_template(template_name)
        if not template_func:
            raise ValueError(f"Unknown template: {template_name}")
        
        card = template_func(**kwargs)
        return json.dumps(card, ensure_ascii=False, indent=2)


# ============================================================================
# Demo / Testing
# ============================================================================

def demo():
    """Demo all card templates"""
    lib = CardTemplateLibrary()
    
    print("📋 Available Templates:")
    print("=" * 50)
    for name in lib.list_templates():
        print(f"  - {name}")
    print()
    
    # Demo: System Notification
    print("1️⃣ System Notification:")
    card = lib.create_system_notification(
        title="系统通知",
        subtitle="Git 安全扫描完成",
        content="✅ 扫描完成，未发现敏感信息\n\n**扫描范围**: 1149 个提交\n**检测模式**: 12 种密钥模式",
        link_url="https://github.com",
        link_text="查看报告"
    )
    print(json.dumps(card, ensure_ascii=False, indent=2)[:500] + "...")
    print()
    
    # Demo: Security Alert
    print("2️⃣ Security Alert:")
    card = lib.create_security_alert(
        alert_type="Token 泄露",
        severity="CRITICAL",
        details="检测到 GitHub Token 提交到仓库",
        file_path=".env",
        commit_hash="a12ce4c",
        action_url="https://github.com/settings/tokens"
    )
    print(json.dumps(card, ensure_ascii=False, indent=2)[:500] + "...")
    print()
    
    # Demo: 7-Persona Status
    print("3️⃣ 7-Persona Status:")
    card = lib.create_persona_status(
        persona_states={
            '规划者': {'status': 'success', 'score': 96, 'details': '任务分解清晰'},
            '执行者': {'status': 'success', 'score': 95, 'details': '代码质量优秀'},
            '批判者': {'status': 'success', 'score': 93, 'details': '审查通过'},
            '学习者': {'status': 'success', 'score': 94, 'details': '记忆已更新'},
            '协调者': {'status': 'success', 'score': 90, 'details': '时间检查完成'},
            '创新者': {'status': 'success', 'score': 95, 'details': '3 个创新方案'},
            '元认知': {'status': 'success', 'score': 91, 'details': '系统健康'}
        },
        overall_score=94,
        summary="7 人格系统运行正常，综合评分优秀"
    )
    print(json.dumps(card, ensure_ascii=False, indent=2)[:500] + "...")
    print()
    
    print("=" * 50)
    print("✅ Demo complete!")


if __name__ == '__main__':
    demo()
