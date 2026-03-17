#!/usr/bin/env python3
"""
Feishu Approval Workflow System
================================
Interactive approval cards with callback handling and auto-escalation.

Features:
- Approval request creation
- Callback URL handling (approve/reject)
- Status tracking (pending/approved/rejected/escalated)
- Auto-escalation after timeout
- Approval history logging
- Multi-step approval chains

Usage:
    # Create approval request
    python feishu-approval-workflow.py --create --title "部署审批" --approver "user_id"
    
    # Handle callback
    python feishu-approval-workflow.py --callback --request-id 123 --action approve
    
    # Check status
    python feishu-approval-workflow.py --status --request-id 123
    
    # Process escalations
    python feishu-approval-workflow.py --escalate
"""

import os
import sys
import json
import time
import hashlib
import logging
import argparse
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

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

class ApprovalConfig:
    """Approval workflow configuration"""
    
    # Database
    DB_PATH = os.path.join(os.path.dirname(__file__), 'feishu_approvals.db')
    
    # Timeout settings (seconds)
    DEFAULT_TIMEOUT = 1800  # 30 minutes
    ESCALATION_TIMEOUT = 3600  # 1 hour
    
    # Priority levels
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_CRITICAL = 'critical'
    
    # Status
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_ESCALATED = 'escalated'
    STATUS_EXPIRED = 'expired'
    
    # Feishu
    FEISHU_USER_ID = os.getenv('FEISHU_USER_ID', 'ou_72a847b95fc25870dcdd8ce56d929252')


# ============================================================================
# Database Manager
# ============================================================================

class ApprovalDatabase:
    """SQLite database manager for approval workflow"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            # Approval requests table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS approval_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    approver_id TEXT NOT NULL,
                    creator_id TEXT,
                    priority TEXT DEFAULT 'normal',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    responded_at TIMESTAMP,
                    response_comment TEXT,
                    escalation_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # Approval history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS approval_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor_id TEXT,
                    comment TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (request_id) REFERENCES approval_requests(request_id)
                )
            ''')
            
            # Create indexes
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
                ON approval_requests(status, expires_at)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_approver 
                ON approval_requests(approver_id, status)
            ''')


# ============================================================================
# Approval Workflow Manager
# ============================================================================

class ApprovalWorkflowManager:
    """Manager for approval workflow"""
    
    def __init__(self, config: ApprovalConfig = None):
        self.config = config or ApprovalConfig()
        self.db = ApprovalDatabase(self.config.DB_PATH)
        self.card_lib = CardTemplateLibrary()
        self._import_feishu_api()
    
    def _import_feishu_api(self):
        """Import Feishu API"""
        try:
            from feishu_api import FeishuAPI
            self.feishu = FeishuAPI()
        except ImportError:
            logger.warning("FeishuAPI not available, notifications will be logged only")
            self.feishu = None
    
    def _generate_request_id(self, title: str, timestamp: str) -> str:
        """Generate unique request ID"""
        content = f"{title}:{timestamp}:{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def create_approval_request(
        self,
        title: str,
        description: str,
        approver_id: str,
        creator_id: str = '',
        priority: str = 'normal',
        timeout_minutes: int = 30,
        metadata: Dict = None
    ) -> str:
        """
        Create new approval request
        
        Args:
            title: Request title
            description: What needs approval
            approver_id: Feishu user ID of approver
            creator_id: Feishu user ID of creator
            priority: low/normal/high/critical
            timeout_minutes: Timeout in minutes
            metadata: Additional metadata (JSON)
        
        Returns:
            request_id: Unique request identifier
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        request_id = self._generate_request_id(title, timestamp)
        expires_at = datetime.now() + timedelta(minutes=timeout_minutes)
        
        # Insert into database
        with self.db.get_connection() as conn:
            conn.execute('''
                INSERT INTO approval_requests 
                (request_id, title, description, approver_id, creator_id, 
                 priority, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (request_id, title, description, approver_id, creator_id,
                  priority, expires_at, json.dumps(metadata or {})))
            
            # Log history
            conn.execute('''
                INSERT INTO approval_history (request_id, action, actor_id, comment)
                VALUES (?, 'created', ?, 'Approval request created')
            ''', (request_id, creator_id))
        
        logger.info(f"Approval request created: {request_id}")
        
        # Send notification
        self._send_approval_notification(request_id, title, description, approver_id, expires_at)
        
        return request_id
    
    def _send_approval_notification(
        self,
        request_id: str,
        title: str,
        description: str,
        approver_id: str,
        expires_at: datetime
    ):
        """Send approval notification card"""
        card = self.card_lib.create_approval_request(
            title=title,
            description=description,
            approver=approver_id,
            deadline=expires_at.strftime('%Y-%m-%d %H:%M'),
            callback_url=f"http://localhost:8080/approval/callback?request_id={request_id}",
            approve_value='approved',
            reject_value='rejected'
        )
        
        if self.feishu:
            try:
                self.feishu.send_card(card, approver_id)
                logger.info(f"Approval notification sent to {approver_id}")
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
        else:
            logger.info(f"[MOCK] Sent approval card to {approver_id}")
    
    def handle_callback(
        self,
        request_id: str,
        action: str,
        actor_id: str,
        comment: str = ''
    ) -> Tuple[bool, str]:
        """
        Handle approval callback (button click)
        
        Args:
            request_id: Request identifier
            action: approve/reject
            actor_id: Feishu user ID of actor
            comment: Optional comment
        
        Returns:
            (success, message)
        """
        with self.db.get_connection() as conn:
            # Get request
            cursor = conn.execute('''
                SELECT * FROM approval_requests WHERE request_id = ?
            ''', (request_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, f"Request not found: {request_id}"
            
            if row['status'] != self.config.STATUS_PENDING:
                return False, f"Request already {row['status']}"
            
            # Update status
            new_status = self.config.STATUS_APPROVED if action == 'approve' else self.config.STATUS_REJECTED
            
            conn.execute('''
                UPDATE approval_requests 
                SET status = ?, responded_at = ?, response_comment = ?
                WHERE request_id = ?
            ''', (new_status, datetime.now(), comment, request_id))
            
            # Log history
            conn.execute('''
                INSERT INTO approval_history (request_id, action, actor_id, comment)
                VALUES (?, ?, ?, ?)
            ''', (request_id, action, actor_id, comment))
        
        logger.info(f"Approval {action}d: {request_id} by {actor_id}")
        
        # Send confirmation
        self._send_confirmation(request_id, new_status, actor_id)
        
        return True, f"Request {action}d successfully"
    
    def _send_confirmation(self, request_id: str, status: str, actor_id: str):
        """Send confirmation notification"""
        emoji = '✅' if status == 'approved' else '❌'
        color = 'green' if status == 'approved' else 'red'
        
        content = f"{emoji} 审批{status}\n\n请求 ID: {request_id}\n操作人：{actor_id}"
        
        if self.feishu:
            try:
                self.feishu.send_text(content, self.config.FEISHU_USER_ID)
            except Exception as e:
                logger.error(f"Failed to send confirmation: {e}")
        else:
            logger.info(f"[MOCK] Confirmation: {content}")
    
    def process_escalations(self) -> int:
        """Process expired approvals (auto-escalate)"""
        now = datetime.now()
        escalated = 0
        
        with self.db.get_connection() as conn:
            # Find expired pending requests
            cursor = conn.execute('''
                SELECT * FROM approval_requests 
                WHERE status = 'pending' AND expires_at <= ?
            ''', (now,))
            
            for row in cursor:
                request_id = row['request_id']
                escalation_count = row['escalation_count']
                
                if escalation_count >= 2:
                    # Mark as expired after 2 escalations
                    conn.execute('''
                        UPDATE approval_requests 
                        SET status = 'expired' 
                        WHERE request_id = ?
                    ''', (request_id,))
                    logger.warning(f"Request expired: {request_id}")
                else:
                    # Escalate to next level (mock: same approver + notification)
                    conn.execute('''
                        UPDATE approval_requests 
                        SET status = 'escalated', escalation_count = escalation_count + 1,
                            expires_at = datetime(expires_at, '+1 hour')
                        WHERE request_id = ?
                    ''', (request_id,))
                    
                    # Log history
                    conn.execute('''
                        INSERT INTO approval_history (request_id, action, comment)
                        VALUES (?, 'escalated', 'Auto-escalated due to timeout')
                    ''', (request_id,))
                    
                    # Send escalation notification
                    self._send_escalation_notification(request_id, escalation_count + 1)
                    escalated += 1
        
        return escalated
    
    def _send_escalation_notification(self, request_id: str, level: int):
        """Send escalation notification"""
        content = f"⚠️ 审批升级 (第{level}次)\n\n请求 ID: {request_id}\n超时未响应，已升级处理"
        
        if self.feishu:
            try:
                self.feishu.send_text(content, self.config.FEISHU_USER_ID)
            except Exception as e:
                logger.error(f"Failed to send escalation: {e}")
        else:
            logger.info(f"[MOCK] Escalation: {content}")
    
    def get_request_status(self, request_id: str) -> Optional[Dict]:
        """Get request status and details"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM approval_requests WHERE request_id = ?
            ''', (request_id,))
            row = cursor.fetchone()
            
            if row:
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                return result
        return None
    
    def get_pending_approvals(self, approver_id: str) -> List[Dict]:
        """Get pending approvals for user"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM approval_requests 
                WHERE approver_id = ? AND status = 'pending'
                ORDER BY created_at DESC
            ''', (approver_id,))
            return [dict(row) for row in cursor]
    
    def get_approval_history(self, request_id: str) -> List[Dict]:
        """Get approval history"""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM approval_history 
                WHERE request_id = ?
                ORDER BY timestamp DESC
            ''', (request_id,))
            return [dict(row) for row in cursor]
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Get approval statistics"""
        cutoff = datetime.now() - timedelta(days=days)
        
        with self.db.get_connection() as conn:
            stats = {}
            
            # Count by status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as count
                FROM approval_requests
                WHERE created_at > ?
                GROUP BY status
            ''', (cutoff,))
            stats['by_status'] = {row['status']: row['count'] for row in cursor}
            
            # Average response time
            cursor = conn.execute('''
                SELECT AVG(
                    (julianday(responded_at) - julianday(created_at)) * 24 * 60
                ) as avg_minutes
                FROM approval_requests
                WHERE responded_at IS NOT NULL AND created_at > ?
            ''', (cutoff,))
            row = cursor.fetchone()
            stats['avg_response_minutes'] = row['avg_minutes'] or 0
            
            # Escalation rate
            cursor = conn.execute('''
                SELECT COUNT(*) FROM approval_requests
                WHERE escalation_count > 0 AND created_at > ?
            ''', (cutoff,))
            escalated = cursor.fetchone()[0]
            
            cursor = conn.execute('''
                SELECT COUNT(*) FROM approval_requests
                WHERE created_at > ?
            ''', (cutoff,))
            total = cursor.fetchone()[0]
            
            stats['escalation_rate'] = (escalated / total * 100) if total > 0 else 0
            
            return stats


# ============================================================================
# CLI Interface
# ============================================================================

def create_request(args):
    """Create approval request"""
    manager = ApprovalWorkflowManager()
    
    request_id = manager.create_approval_request(
        title=args.title,
        description=args.description or '请审批',
        approver_id=args.approver,
        creator_id=args.creator or '',
        priority=args.priority or 'normal',
        timeout_minutes=args.timeout or 30
    )
    
    print(f"✅ Approval request created: {request_id}")


def handle_callback(args):
    """Handle approval callback"""
    manager = ApprovalWorkflowManager()
    
    success, message = manager.handle_callback(
        request_id=args.request_id,
        action=args.action,
        actor_id=args.actor or 'system',
        comment=args.comment or ''
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def check_status(args):
    """Check request status"""
    manager = ApprovalWorkflowManager()
    
    status = manager.get_request_status(args.request_id)
    
    if status:
        print(f"📋 Request Status: {args.request_id}")
        print("=" * 50)
        print(f"Title: {status['title']}")
        print(f"Status: {status['status']}")
        print(f"Approver: {status['approver_id']}")
        print(f"Created: {status['created_at']}")
        print(f"Expires: {status['expires_at']}")
        if status['responded_at']:
            print(f"Responded: {status['responded_at']}")
        if status['response_comment']:
            print(f"Comment: {status['response_comment']}")
        print("=" * 50)
    else:
        print(f"❌ Request not found: {args.request_id}")


def process_escalations(args):
    """Process escalations"""
    manager = ApprovalWorkflowManager()
    escalated = manager.process_escalations()
    print(f"⚠️  Processed {escalated} escalation(s)")


def show_statistics(args):
    """Show approval statistics"""
    manager = ApprovalWorkflowManager()
    stats = manager.get_statistics(days=args.days or 7)
    
    print("📊 Approval Statistics")
    print("=" * 50)
    print(f"Period: Last {args.days or 7} days")
    print(f"\nBy Status:")
    for status, count in stats['by_status'].items():
        print(f"  {status}: {count}")
    print(f"\nAvg Response Time: {stats['avg_response_minutes']:.1f} minutes")
    print(f"Escalation Rate: {stats['escalation_rate']:.1f}%")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='Feishu Approval Workflow System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create approval request
  python feishu-approval-workflow.py --create --title "部署审批" --approver "user_id"
  
  # Handle callback
  python feishu-approval-workflow.py --callback --request-id 123 --action approve
  
  # Check status
  python feishu-approval-workflow.py --status --request-id 123
  
  # Process escalations
  python feishu-approval-workflow.py --escalate
  
  # Show statistics
  python feishu-approval-workflow.py --stats --days 7
        """
    )
    
    parser.add_argument('--create', action='store_true', help='Create approval request')
    parser.add_argument('--callback', action='store_true', help='Handle callback')
    parser.add_argument('--status', action='store_true', help='Check request status')
    parser.add_argument('--escalate', action='store_true', help='Process escalations')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    parser.add_argument('--title', type=str, help='Request title')
    parser.add_argument('--description', type=str, help='Request description')
    parser.add_argument('--approver', type=str, help='Approver user ID')
    parser.add_argument('--creator', type=str, help='Creator user ID')
    parser.add_argument('--priority', type=str, choices=['low', 'normal', 'high', 'critical'])
    parser.add_argument('--timeout', type=int, help='Timeout in minutes')
    
    parser.add_argument('--request-id', type=str, help='Request ID')
    parser.add_argument('--action', type=str, choices=['approve', 'reject'])
    parser.add_argument('--actor', type=str, help='Actor user ID')
    parser.add_argument('--comment', type=str, help='Comment')
    
    parser.add_argument('--days', type=int, help='Statistics period (days)')
    
    args = parser.parse_args()
    
    if args.create:
        create_request(args)
    elif args.callback:
        handle_callback(args)
    elif args.status:
        check_status(args)
    elif args.escalate:
        process_escalations(args)
    elif args.stats:
        show_statistics(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
