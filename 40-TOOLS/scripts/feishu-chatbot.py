#!/usr/bin/env python3
"""
Feishu Chatbot - Basic Command Handler
=======================================
Interactive chatbot for Feishu with command handling and smart replies.

Features:
- Command parsing (/status, /help, /queue, /persona)
- FAQ database with semantic matching
- Context-aware responses
- Integration with message queue and persona system
- Local LLM integration (Ollama) for smart replies

Usage:
    python feishu-chatbot.py
    # Listens for incoming messages and responds
"""

import os
import sys
import json
import logging
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

class ChatbotConfig:
    """Chatbot configuration"""
    
    # Database
    DB_PATH = os.path.join(os.path.dirname(__file__), 'feishu_chatbot.db')
    
    # Feishu
    FEISHU_USER_ID = os.getenv('FEISHU_USER_ID', 'ou_72a847b95fc25870dcdd8ce56d929252')
    
    # Local LLM
    LOCAL_LLM_ENABLED = os.getenv('LOCAL_LLM_ENABLED', 'true').lower() == 'true'
    LOCAL_LLM_URL = os.getenv('LOCAL_LLM_URL', 'http://localhost:11434/api/generate')
    LOCAL_LLM_MODEL = os.getenv('LOCAL_LLM_MODEL', 'qwen2.5:1.5b')
    
    # Commands
    COMMAND_PREFIX = '/'
    
    # FAQ similarity threshold
    FAQ_THRESHOLD = 0.6


# ============================================================================
# FAQ Database
# ============================================================================

DEFAULT_FAQS = [
    {
        'question': '系统状态如何？',
        'answer': '系统运行正常 ✅\n\n- 消息队列：运行中\n- 审批系统：运行中\n- 分析仪表板：运行中\n\n最后检查：{time}',
        'tags': ['状态', '健康', '运行']
    },
    {
        'question': '如何发送消息？',
        'answer': '使用消息队列发送：\n\n```bash\npython feishu_message_queue.py --send "内容" --priority P1\n```\n\n优先级：P0 (紧急), P1 (高), P2 (普通)',
        'tags': ['发送', '消息', '使用']
    },
    {
        'question': '审批流程是什么？',
        'answer': '审批流程：\n\n1. 创建审批请求\n2. 审批人收到通知卡片\n3. 点击"批准"或"拒绝"\n4. 系统记录结果\n\n超时自动升级（30 分钟）',
        'tags': ['审批', '流程', '工作流']
    },
    {
        'question': '如何查看统计？',
        'answer': '访问分析仪表板：\n\nhttp://localhost:8080\n\n实时显示：\n- 消息量趋势\n- 送达率\n- 审批统计\n- 优先级分布',
        'tags': ['统计', '分析', '仪表板']
    },
    {
        'question': '7 人格系统是什么？',
        'answer': '7 人格系统包括：\n\n🎯 规划者 - 制定计划\n⚡ 执行者 - 完成任务\n🔍 批判者 - 审查质量\n📚 学习者 - 更新记忆\n⚖️ 协调者 - 平衡决策\n💡 创新者 - 突破常规\n🧠 元认知 - 系统监控',
        'tags': ['人格', '7 人格', '系统']
    },
    {
        'question': 'Git Firewall 是什么？',
        'answer': 'Git Firewall Proxy 是敏感数据检测系统：\n\n- 12 种 secret 模式匹配\n- Shannon 熵值分析 (>7.5)\n- 6 种路径黑名单\n- pre-commit hook 自动拦截\n\n安装：python git-firewall-proxy.py --install-hook',
        'tags': ['Git', '安全', 'Firewall']
    },
    {
        'question': '如何查看队列状态？',
        'answer': '查看消息队列状态：\n\n```bash\npython feishu_message_queue.py --status\n```\n\n显示：待发送/发送中/失败消息数',
        'tags': ['队列', '状态', '消息']
    },
    {
        'question': '消息重试机制？',
        'answer': '自动重试机制：\n\n- 最多重试 3 次\n- 指数退避：30 秒 → 2 分钟 → 5 分钟\n- 失败后标记为 failed\n- 可手动重新处理',
        'tags': ['重试', '失败', '机制']
    }
]


class FAQDatabase:
    """FAQ database manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        self._load_defaults()
    
    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT UNIQUE NOT NULL,
                    answer TEXT NOT NULL,
                    tags TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()
    
    def _load_defaults(self):
        """Load default FAQs"""
        conn = sqlite3.connect(self.db_path)
        try:
            for faq in DEFAULT_FAQS:
                conn.execute('''
                    INSERT OR IGNORE INTO faqs (question, answer, tags)
                    VALUES (?, ?, ?)
                ''', (faq['question'], faq['answer'], json.dumps(faq['tags'])))
            conn.commit()
        finally:
            conn.close()
    
    def search(self, query: str, threshold: float = 0.6) -> Optional[str]:
        """Search FAQ by question"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.execute('SELECT * FROM faqs')
            best_match = None
            best_score = 0
            
            for row in cursor:
                # Calculate similarity
                score = SequenceMatcher(None, query.lower(), row['question'].lower()).ratio()
                
                # Also check tags
                tags = json.loads(row['tags'] or '[]')
                tag_score = max([
                    SequenceMatcher(None, query.lower(), tag.lower()).ratio()
                    for tag in tags
                ], default=0)
                
                # Combined score
                combined_score = max(score, tag_score * 0.9)
                
                if combined_score > best_score and combined_score >= threshold:
                    best_score = combined_score
                    best_match = row
            
            if best_match:
                # Update usage count
                conn.execute('''
                    UPDATE faqs SET usage_count = usage_count + 1 WHERE id = ?
                ''', (best_match['id'],))
                conn.commit()
                
                # Format answer
                answer = best_match['answer'].format(time=datetime.now().strftime('%Y-%m-%d %H:%M'))
                return answer
        finally:
            conn.close()
        
        return None


# ============================================================================
# Command Handler
# ============================================================================

class CommandHandler:
    """Handle chatbot commands"""
    
    def __init__(self):
        self.commands = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'queue': self.cmd_queue,
            'persona': self.cmd_persona,
            'approvals': self.cmd_approvals,
            'stats': self.cmd_stats,
            'faq': self.cmd_faq,
        }
    
    def handle(self, command: str, args: List[str]) -> str:
        """Handle command"""
        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"❌ 命令执行失败：{e}"
        else:
            return f"❌ 未知命令：/{command}\n输入 /help 查看可用命令"
    
    def cmd_help(self, args: List[str]) -> str:
        """Help command"""
        return """📚 可用命令

/ status - 查看系统状态
/ queue - 查看消息队列
/ persona - 查看 7 人格状态
/ approvals - 查看待审批
/ stats - 查看统计
/ faq <问题> - 常见问题查询
/ help - 显示帮助

示例:
  /status
  /faq 如何发送消息
  /persona"""
    
    def cmd_status(self, args: List[str]) -> str:
        """Status command"""
        from feishu_message_queue import FeishuMessageQueue
        
        queue = FeishuMessageQueue()
        status = queue.get_status()
        
        return f"""📊 系统状态

消息队列:
  待发送：{status.get('pending', 0)}
  发送中：{status.get('sending', 0)}
  失败：{status.get('failed', 0)}

最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    def cmd_queue(self, args: List[str]) -> str:
        """Queue status command"""
        from feishu_message_queue import FeishuMessageQueue
        
        queue = FeishuMessageQueue()
        status = queue.get_status()
        
        return f"""📨 消息队列状态

待发送：{status.get('pending', 0)}
发送中：{status.get('sending', 0)}
失败：{status.get('failed', 0)}

优先级分布:
  P0 (紧急): {status.get('by_priority', {}).get('P0', 0)}
  P1 (高): {status.get('by_priority', {}).get('P1', 0)}
  P2 (普通): {status.get('by_priority', {}).get('P2', 0)}"""
    
    def cmd_persona(self, args: List[str]) -> str:
        """Persona status command"""
        return """🎭 7 人格系统

📋 状态查询功能开发中...

预计下次迭代实现"""
    
    def cmd_approvals(self, args: List[str]) -> str:
        """Approvals command"""
        from feishu_approval_workflow import ApprovalWorkflowManager
        
        manager = ApprovalWorkflowManager()
        pending = manager.get_pending_approvals(ChatbotConfig.FEISHU_USER_ID)
        
        if not pending:
            return "✅ 无待审批事项"
        
        lines = [f"📋 待审批 ({len(pending)}):"]
        for item in pending:
            lines.append(f"\n• {item['title']}")
            lines.append(f"  优先级：{item['priority']}")
            lines.append(f"  超时：{item['expires_at']}")
        
        return '\n'.join(lines)
    
    def cmd_stats(self, args: List[str]) -> str:
        """Stats command"""
        days = int(args[0]) if args else 7
        
        return f"""📈 统计信息 (过去{days}天)

访问分析仪表板:
http://localhost:8080

或运行:
python feishu-analytics-dashboard.py"""
    
    def cmd_faq(self, args: List[str]) -> str:
        """FAQ command"""
        if not args:
            return "❌ 请提供问题\n示例：/faq 如何发送消息"
        
        query = ' '.join(args)
        faq_db = FAQDatabase(ChatbotConfig.DB_PATH)
        answer = faq_db.search(query)
        
        if answer:
            return answer
        else:
            return f"❓ 未找到相关问题\n\n尝试：\n- 如何发送消息\n- 审批流程\n- 系统状态"


# ============================================================================
# Local LLM Integration
# ============================================================================

class LocalLLMHandler:
    """Local LLM handler for smart replies"""
    
    def __init__(self, config: ChatbotConfig):
        self.config = config
        self.enabled = config.LOCAL_LLM_ENABLED
        self.url = config.LOCAL_LLM_URL
        self.model = config.LOCAL_LLM_MODEL
    
    def generate(self, prompt: str, max_tokens: int = 256) -> Optional[str]:
        """Generate response using local LLM"""
        if not self.enabled:
            return None
        
        try:
            import requests
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'max_tokens': max_tokens,
                'stream': False
            }
            
            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            logger.warning(f"Local LLM failed: {e}")
            return None


# ============================================================================
# Chatbot Manager
# ============================================================================

class FeishuChatbot:
    """Feishu chatbot manager"""
    
    def __init__(self):
        self.config = ChatbotConfig()
        self.command_handler = CommandHandler()
        self.faq_db = FAQDatabase(self.config.DB_PATH)
        self.llm_handler = LocalLLMHandler(self.config)
        self._import_feishu_api()
    
    def _import_feishu_api(self):
        """Import Feishu API"""
        try:
            from feishu_api import FeishuAPI
            self.feishu = FeishuAPI()
        except ImportError:
            logger.warning("FeishuAPI not available")
            self.feishu = None
    
    def process_message(self, text: str, user_id: str) -> Optional[str]:
        """
        Process incoming message and generate response
        
        Args:
            text: Message text
            user_id: Sender user ID
        
        Returns:
            Response text or None
        """
        text = text.strip()
        
        # Check if command
        if text.startswith(self.config.COMMAND_PREFIX):
            return self._handle_command(text, user_id)
        
        # Try FAQ match
        faq_answer = self.faq_db.search(text, threshold=0.5)
        if faq_answer:
            return faq_answer
        
        # Try LLM
        if self.llm_handler.enabled:
            llm_response = self.llm_handler.generate(
                f"你是飞书助手。简短回答：{text}"
            )
            if llm_response:
                return llm_response
        
        # Default response
        return "🤔 我不太理解，试试 /help 查看可用命令"
    
    def _handle_command(self, text: str, user_id: str) -> str:
        """Handle command"""
        # Parse command
        parts = text[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        logger.info(f"Command: {command}, Args: {args}, User: {user_id}")
        
        return self.command_handler.handle(command, args)
    
    def send_response(self, text: str, user_id: str):
        """Send response"""
        if self.feishu:
            try:
                self.feishu.send_text(text, user_id)
                logger.info(f"Response sent to {user_id}")
            except Exception as e:
                logger.error(f"Failed to send response: {e}")
        else:
            logger.info(f"[MOCK] Response to {user_id}: {text}")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point"""
    print("🤖 飞书聊天机器人")
    print("=" * 50)
    print("输入消息测试响应 (输入 /quit 退出)")
    print("=" * 50)
    
    chatbot = FeishuChatbot()
    
    while True:
        try:
            text = input("\n📥 输入：").strip()
            
            if text.lower() in ['quit', 'exit', '/quit']:
                print("👋 再见！")
                break
            
            if not text:
                continue
            
            response = chatbot.process_message(text, 'test_user')
            
            if response:
                print(f"\n📤 响应:\n{response}")
                chatbot.send_response(response, ChatbotConfig.FEISHU_USER_ID)
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误：{e}")


if __name__ == '__main__':
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    main()
