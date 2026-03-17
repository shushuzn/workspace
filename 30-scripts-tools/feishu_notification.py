#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Feishu Notification - Send notifications to Feishu (Lark)

Usage:
    python feishu_notification.py --task TASK_NAME --status STATUS [--message MESSAGE]
    python feishu_notification.py --test
"""

import os
import sys
import json
import hashlib
import hmac
import base64
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Import cache manager
try:
    from cache_manager import CacheManager
    CACHE_ENABLED = True
    cache = CacheManager()
except ImportError:
    CACHE_ENABLED = False
    cache = None

# Config
WORKSPACE = Path(__file__).parent.parent
ENV_FILE = WORKSPACE / '.env'

class FeishuNotifier:
    """Feishu notification sender"""
    
    def __init__(self):
        self.app_id = ''
        self.app_secret = ''
        self.user_id = os.getenv('FEISHU_USER_ID', '999d5a38')  # Default to short format user_id
        self.token = None
        self.token_expiry = None
        
        # Load credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from .env file"""
        if ENV_FILE.exists():
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('FEISHU_APP_ID='):
                        self.app_id = line.split('=')[1].strip()
                    elif line.startswith('FEISHU_APP_SECRET='):
                        self.app_secret = line.split('=')[1].strip()
                    elif line.startswith('FEISHU_USER_ID='):
                        self.user_id = line.split('=')[1].strip()
    
    def _fetch_token(self) -> Optional[str]:
        """Fetch new token from Feishu API"""
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        headers = {'Content-Type': 'application/json'}
        payload = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                return data['tenant_access_token']
            else:
                print(f"[WARN] Token request failed: {data}")
                return None
                
        except Exception as e:
            print(f"[WARN] Token request error: {e}")
            return None
    
    def _get_access_token(self) -> Optional[str]:
        """Get access token (cached with smart cache manager)"""
        if CACHE_ENABLED and cache:
            # Use smart cache with auto-refresh
            return cache.get('feishu_token', self._fetch_token, ttl=7200)
        else:
            # Fallback to old caching method
            if self.token and self.token_expiry:
                if datetime.now() < self.token_expiry:
                    return self.token
            
            self.token = self._fetch_token()
            if self.token:
                self.token_expiry = datetime.now() + timedelta(hours=2, minutes=-10)
            return self.token
    
    def send_text(self, text: str, user_id: str = None) -> Dict:
        """Send text message"""
        if not user_id:
            user_id = self.user_id
        
        token = self._get_access_token()
        if not token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        url = f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=user_id'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Replace emoji with ASCII for Windows console compatibility
        text = self._sanitize_emoji(text)
        
        payload = {
            'receive_id': user_id,
            'msg_type': 'text',
            'content': json.dumps({'text': text}, ensure_ascii=False)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            
            return {
                'success': data.get('code') == 0,
                'message_id': data.get('data', {}).get('message_id'),
                'response': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_card(self, card_data: Dict, user_id: str = None) -> Dict:
        """Send interactive card message"""
        if not user_id:
            user_id = self.user_id
        
        token = self._get_access_token()
        if not token:
            return {'success': False, 'error': 'Failed to get access token'}
        
        url = f'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=user_id'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'receive_id': user_id,
            'msg_type': 'interactive',
            'content': json.dumps(card_data, ensure_ascii=False)
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            
            return {
                'success': data.get('code') == 0,
                'message_id': data.get('data', {}).get('message_id'),
                'response': data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _sanitize_emoji(self, text: str) -> str:
        """Replace emoji with ASCII for console compatibility"""
        emoji_map = {
            '[OK]': '[OK]',
            '[FAIL]': '[FAIL]',
            '[WARN]': '[WARN]',
            '🔴': '[HIGH]',
            '🟡': '[MED]',
            '🟢': '[LOW]',
            '[CHART]': '[STATS]',
            '[LIST]': '[TASK]',
            '🗑️': '[DELETE]',
            '⏭️': '[SKIP]',
            '🔄': '[UPDATE]',
            '📄': '[FILE]',
            '[TARGET]': '[TARGET]',
            '[LAUNCH]': '[LAUNCH]',
            '[PAW]': '[CLAW]',
            '💓': '[HEART]',
            '⏰': '[TIME]',
            '[FOLDER]': '[FOLDER]',
            '✨': '[NEW]',
            '🧠': '[BRAIN]',
            '💻': '[CODE]',
            '📚': '[BOOK]',
            '[SUCCESS]': '[DONE]',
            '[NOTE]': '[NOTE]',
            '[FIX]': '[TOOL]',
            '[TREND]': '[CHART]',
            '🔒': '[SECURE]',
            '☁️': '[CLOUD]',
            '📡': '[SIGNAL]',
            '⚡': '[FAST]',
            '[MASK]': '[PERSONA]',
            '📂': '[DIR]',
            '[SEARCH]': '[SEARCH]',
            '[IDEA]': '[IDEA]',
            '📌': '[PIN]',
            '🏷️': '[TAG]',
            '📅': '[DATE]',
            '⏱️': '[TIMER]',
            '📞': '[CALL]',
            '💬': '[MSG]',
            '🔔': '[NOTIFY]',
            '📢': '[ANNOUNCE]',
            '🎪': '[EVENT]',
            '🏆': '[ACHIEVE]',
            '💪': '[STRONG]',
            '👍': '[THUMBS]',
            '🙏': '[THANKS]',
            '😊': '[HAPPY]',
            '😄': '[SMILE]',
            '🤔': '[THINK]',
            '😅': '[AWKWARD]',
            '😭': '[SAD]',
            '😤': '[ANGRY]',
            '🎊': '[CELEBRATE]',
            '🌟': '[STAR]',
            '⭐': '[FAVORITE]',
            '🔥': '[FIRE]',
            '💯': '[PERFECT]',
            '🆕': '[BRAND]',
            '🆙': '[UP]',
            '🆓': '[FREE]',
            '🈶': '[HAVE]',
            '🈚': '[NONE]',
            '🈸': '[APPLY]',
            '🈴': '[PASS]',
            '🈳': '[EMPTY]',
            '㊗️': '[WISH]',
            '㊙️': '[SECRET]',
            '🉐': '[GET]',
            '🉑': '[OK]',
            '🚫': '[NO]',
            '🔞': '[ADULT]',
            '📶': '[SIGNAL]',
            '🎴': '[CARD]',
            '🀄': '[MAHJONG]',
            '[TARGET]': '[DART]',
            '🎲': '[DICE]',
            '🎮': '[GAME]',
            '🎨': '[ART]',
            '🎬': '[MOVIE]',
            '🎤': '[MIC]',
            '🎧': '[HEADPHONE]',
            '🎼': '[MUSIC]',
            '🎹': '[PIANO]',
            '🎸': '[GUITAR]',
            '🎺': '[TRUMPET]',
            '🎻': '[VIOLIN]',
            '🥁': '[DRUM]',
            '🎷': '[SAX]',
            '🪕': '[BANJO]',
            '🪗': '[ACCORDION]',
            '🪘': '[CONGA]',
            '🪙': '[COIN]',
            '🪐': '[PLANET]',
            '🪑': '[CHAIR]',
            '🪒': '[AXE]',
            '🪓': '[HAMMER]',
            '🪛': '[SCREWDRIVER]',
            '🪜': '[LADDER]',
            '🪝': '[HOOK]',
            '🪞': '[MIRROR]',
            '🪟': '[WINDOW]',
            '🪠': '[PLUNGER]',
            '🪡': '[NEEDLE]',
            '🪢': '[KNOT]',
            '🪣': '[BUCKET]',
            '🪤': '[MOUSETRAP]',
            '🪥': '[TOOTHBRUSH]',
            '🪦': '[TOMBSTONE]',
            '🪧': '[SIGN]',
            '🪨': '[ROCK]',
            '🪩': '[MIRROR_BALL]',
            '🪪': '[ID_CARD]',
            '🪫': '[LOW_BATTERY]',
            '🪬': '[HANDSAW]',
            '🪭': '[FOLDING]',
            '🪮': '[AFRO]',
            '🪯': '[KHANDA]',
            '🪰': '[FLY]',
            '🪱': '[WORM]',
            '🪲': '[BEETLE]',
            '🪳': '[COCKROACH]',
            '🪴': '[POTTED]',
            '🪵': '[WOOD]',
            '🪶': '[FEATHER]',
            '🪷': '[LOTUS]',
            '🪸': '[CORAL]',
            '🪹': '[NEST]',
            '🪺': '[NEST_WITH_EGGS]',
            '🪻': '[HYACINTH]',
            '🪼': '[JELLYFISH]',
            '🪽': '[WING]',
            '🪾': '[LEAFLESS]',
            '🪿': '[GOOSE]',
            '🫀': '[ANATOMICAL_HEART]',
            '🫁': '[LUNGS]',
            '🫂': '[PEOPLE_HUGGING]',
            '🫃': '[PREGNANT]',
            '🫄': '[PREGNANT_MAN]',
            '🫅': '[PERSON_WITH_CROWN]',
            '🫆': '[FINGERPRINT]',
            '🫇': '[PEA_POD]',
            '🫈': '[BEANS]',
            '🫉': '[OLIVE]',
            '🫊': '[TANGERINE]',
            '🫋': '[BLUEBERRIES]',
            '🫌': '[PICKLE]',
            '🫍': '[BELL_PEPPER]',
            '🫎': '[MOOSE]',
            '🫏': '[DONKEY]',
            '🫐': '[BLUEBERRY]',
            '🫑': '[BELL_PEPPER]',
            '🫒': '[OLIVE]',
            '🫓': '[FLATBREAD]',
            '🫔': '[TAMALE]',
            '🫕': '[FONDUE]',
            '🫖': '[TEAPOT]',
            '🫗': '[POURING_LIQUID]',
            '🫘': '[BEANS]',
            '🫙': '[JAR]',
            '🫚': '[GINGER]',
            '🫛': '[PEA_POD]',
            '🫜': '[ROOT_VEGETABLE]',
            '🫝': '[WORKOUT]',
            '🫞': '[BOWL]',
            '🫟': '[SPLASH]',
            '🫠': '[MELTING]',
            '🫡': '[SALUTE]',
            '🫢': '[FACE_WITH_OPEN_EYES]',
            '🫣': ['FACE_WITH_PEEPING_EYE'],
            '🫤': '[FACE_WITH_DIAGONAL_MOUTH]',
            '🫥': '[DOTTED_LINE_FACE]',
            '🫦': '[BITING_LIP]',
            '🫧': '[BUBBLES]',
            '🫨': '[SHAKING_FACE]',
            '🫩': '[PLATE]',
            '🫪': '[JAR]',
            '🫫': '[AIRPLANE]',
            '🫬': '[CLOUD]',
            '🫭': '[WIND]',
            '🫮': '[RAIN]',
            '🫯': '[SNOWFLAKE]',
            '🫰': '[LIGHTNING]',
            '🫱': '[EARTHQUAKE]',
            '🫲': '[TORNADO]',
            '🫳': '[TSUNAMI]',
            '🫴': '[VOLCANO]',
            '🫵': '[FLOOD]',
            '🫶': '[DROUGHT]',
            '🫷': '[WILDFIRE]',
            '🫸': '[HURRICANE]',
        }
        
        for emoji, ascii_text in emoji_map.items():
            if isinstance(ascii_text, str):
                text = text.replace(emoji, ascii_text)
        
        return text
    
    def send_task_notification(self, task_name: str, status: str, 
                               message: str = None, details: Dict = None) -> Dict:
        """Send task completion/failure notification"""
        # Status icon
        status_icons = {
            'success': '[OK]',
            'completed': '[OK]',
            'done': '[OK]',
            'failed': '[FAIL]',
            'error': '[FAIL]',
            'warning': '[WARN]',
            'running': '[PENDING]',
            'pending': '⏸️'
        }
        
        icon = status_icons.get(status.lower(), '[LIST]')
        
        # Build message
        title = f"{icon} Task: {task_name}"
        subtitle = f"Status: {status.upper()}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        text = f"""{title}
{subtitle}
Time: {timestamp}"""
        
        if message:
            text += f"\n\n{message}"
        
        if details:
            text += "\n\nDetails:"
            for key, value in details.items():
                text += f"\n- {key}: {value}"
        
        # Send
        return self.send_text(text)
    
    def send_daily_brief(self, brief_data: Dict) -> Dict:
        """Send daily research brief"""
        card = {
            'config': {
                'wide_screen_mode': True
            },
            'header': {
                'template': 'blue',
                'title': {
                    'content': '[CHART] Daily Research Brief',
                    'tag': 'plain_text'
                }
            },
            'elements': [
                {
                    'tag': 'div',
                    'text': {
                        'content': f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n**Generated:** {datetime.now().strftime('%H:%M')}",
                        'tag': 'lark_md'
                    }
                },
                {
                    'tag': 'divider'
                },
                {
                    'tag': 'div',
                    'text': {
                        'content': self._format_brief_content(brief_data),
                        'tag': 'lark_md'
                    }
                }
            ]
        }
        
        return self.send_card(card)
    
    def _format_brief_content(self, data: Dict) -> str:
        """Format brief content for card"""
        lines = []
        
        if 'papers' in data:
            lines.append(f"**📄 Papers Collected:** {data['papers']}")
        
        if 'repos' in data:
            lines.append(f"**💻 GitHub Trending:** {data['repos']}")
        
        if 'articles' in data:
            lines.append(f"**📰 Medium Articles:** {data['articles']}")
        
        if 'quality_score' in data:
            lines.append(f"**[CHART] Quality Score:** {data['quality_score']}/100")
        
        if 'highlights' in data:
            lines.append("\n**🌟 Highlights:**")
            for highlight in data['highlights'][:5]:
                lines.append(f"- {highlight}")
        
        return '\n'.join(lines)
    
    def send_error_alert(self, error_type: str, error_message: str, 
                         task_name: str = None) -> Dict:
        """Send error alert notification"""
        text = f"""🔴 ERROR ALERT

Task: {task_name or 'Unknown'}
Type: {error_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Error:
{error_message[:500]}"""
        
        return self.send_text(text)
    
    def test_notification(self) -> Dict:
        """Send test notification"""
        text = f"""[PAW] OpenClaw Test Notification

Status: [OK] SUCCESS
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test message from OpenClaw automation system.

If you receive this, Feishu notifications are working correctly!"""
        
        return self.send_text(text)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Feishu Notification')
    parser.add_argument('--task', type=str, help='Task name')
    parser.add_argument('--status', type=str, help='Task status')
    parser.add_argument('--message', type=str, help='Custom message')
    parser.add_argument('--test', action='store_true', help='Send test notification')
    parser.add_argument('--daily-brief', action='store_true', help='Send daily brief')
    parser.add_argument('--error', type=str, help='Send error alert')
    
    args = parser.parse_args()
    
    notifier = FeishuNotifier()
    
    if args.test:
        print("📤 Sending test notification...")
        result = notifier.test_notification()
        print(f"[OK] Test sent: {result.get('success', False)}")
    
    elif args.task and args.status:
        print(f"📤 Sending task notification: {args.task}")
        result = notifier.send_task_notification(args.task, args.status, args.message)
        print(f"[OK] Notification sent: {result.get('success', False)}")
    
    elif args.daily_brief:
        print("📤 Sending daily brief...")
        brief_data = {
            'papers': 25,
            'repos': 15,
            'articles': 20,
            'quality_score': 82,
            'highlights': ['Test highlight 1', 'Test highlight 2']
        }
        result = notifier.send_daily_brief(brief_data)
        print(f"[OK] Daily brief sent: {result.get('success', False)}")
    
    elif args.error:
        print("📤 Sending error alert...")
        result = notifier.send_error_alert('Test Error', args.error, 'Test Task')
        print(f"[OK] Error alert sent: {result.get('success', False)}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
