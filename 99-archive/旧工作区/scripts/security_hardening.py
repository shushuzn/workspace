#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Hardening
安全加固系统
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.api_keys = {}
        self.rate_limits = {}
        self.audit_log = []
    
    def generate_api_key(self, user_id: str) -> str:
        """生成 API Key"""
        api_key = secrets.token_urlsafe(32)
        self.api_keys[user_id] = {
            'key': api_key,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'usage_count': 0
        }
        
        self._audit_log('api_key_generated', user_id)
        return api_key
    
    def validate_api_key(self, api_key: str) -> bool:
        """验证 API Key"""
        for user_id, key_info in self.api_keys.items():
            if key_info['key'] == api_key:
                # 更新使用记录
                key_info['last_used'] = datetime.now().isoformat()
                key_info['usage_count'] += 1
                self._audit_log('api_key_validated', user_id)
                return True
        return False
    
    def check_rate_limit(self, user_id: str, limit: int = 100, window: int = 60) -> bool:
        """检查速率限制"""
        now = datetime.now()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # 清理过期记录
        window_start = now - timedelta(seconds=window)
        self.rate_limits[user_id] = [
            t for t in self.rate_limits[user_id] if t > window_start
        ]
        
        # 检查是否超限
        if len(self.rate_limits[user_id]) >= limit:
            self._audit_log('rate_limit_exceeded', user_id)
            return False
        
        # 记录请求
        self.rate_limits[user_id].append(now)
        return True
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${password_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            salt, hash_value = password_hash.split('$')
            password_hash_check = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return password_hash_check.hex() == hash_value
        except Exception:
            return False
    
    def _audit_log(self, action: str, user_id: str, details: str = None):
        """审计日志"""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details or ''
        })
        
        # 限制审计日志大小
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_audit_log(self, limit: int = 100) -> list:
        """获取审计日志"""
        return self.audit_log[-limit:]
    
    def get_security_report(self) -> Dict:
        """获取安全报告"""
        return {
            'api_keys_count': len(self.api_keys),
            'rate_limits_count': len(self.rate_limits),
            'audit_log_count': len(self.audit_log),
            'last_audit': self.audit_log[-1] if self.audit_log else None
        }

def require_auth(f):
    """需要认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取 API Key
        api_key = kwargs.get('api_key')
        if not api_key:
            return {'error': 'Missing API key'}, 401
        
        security_manager = SecurityManager()
        if not security_manager.validate_api_key(api_key):
            return {'error': 'Invalid API key'}, 403
        
        return f(*args, **kwargs)
    return decorated

def rate_limit(limit: int = 100, window: int = 60):
    """速率限制装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_id = kwargs.get('user_id', 'anonymous')
            security_manager = SecurityManager()
            
            if not security_manager.check_rate_limit(user_id, limit, window):
                return {'error': 'Rate limit exceeded'}, 429
            
            return f(*args, **kwargs)
        return decorated
    return decorator

if __name__ == '__main__':
    # 测试安全功能
    security = SecurityManager()
    
    # 生成 API Key
    api_key = security.generate_api_key('user1')
    print(f"API Key: {api_key}")
    
    # 验证 API Key
    valid = security.validate_api_key(api_key)
    print(f"API Key 有效：{valid}")
    
    # 哈希密码
    password_hash = security.hash_password('password123')
    print(f"密码哈希：{password_hash}")
    
    # 验证密码
    valid = security.verify_password('password123', password_hash)
    print(f"密码有效：{valid}")
    
    # 获取安全报告
    report = security.get_security_report()
    print(f"安全报告：{report}")
