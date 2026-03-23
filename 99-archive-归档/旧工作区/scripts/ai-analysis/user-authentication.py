#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Authentication System v1
用户认证系统实现
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

class UserAuth:
    """用户认证系统"""
    
    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        self.token_expiry_hours = 24
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """验证密码"""
        try:
            salt, pwd_hash = stored_hash.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return new_hash.hex() == pwd_hash
        except Exception:
            return False
    
    def register_user(self, username: str, password: str, email: str = None) -> Dict:
        """注册用户"""
        if username in self.users:
            return {"status": "error", "message": "User already exists"}
        
        self.users[username] = {
            "username": username,
            "password_hash": self.hash_password(password),
            "email": email,
            "created_at": datetime.now().isoformat(),
            "role": "user"
        }
        
        return {"status": "success", "message": "User registered"}
    
    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        if username not in self.users:
            return {"status": "error", "message": "Invalid credentials"}
        
        user = self.users[username]
        if not self.verify_password(password, user["password_hash"]):
            return {"status": "error", "message": "Invalid credentials"}
        
        # 生成会话 token
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=self.token_expiry_hours)
        
        self.sessions[token] = {
            "username": username,
            "expires_at": expiry.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "token": token,
            "expires_at": expiry.isoformat(),
            "user": {
                "username": username,
                "email": user.get("email"),
                "role": user.get("role")
            }
        }
    
    def logout(self, token: str) -> Dict:
        """用户登出"""
        if token in self.sessions:
            del self.sessions[token]
            return {"status": "success", "message": "Logged out"}
        return {"status": "error", "message": "Invalid token"}
    
    def verify_token(self, token: str) -> Dict:
        """验证 token"""
        if token not in self.sessions:
            return {"status": "error", "message": "Invalid token"}
        
        session = self.sessions[token]
        expiry = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expiry:
            del self.sessions[token]
            return {"status": "error", "message": "Token expired"}
        
        return {
            "status": "success",
            "user": {
                "username": session["username"],
                "role": self.users[session["username"]].get("role")
            }
        }
    
    def get_user_count(self) -> int:
        """获取用户数"""
        return len(self.users)
    
    def get_session_count(self) -> int:
        """获取会话数"""
        return len(self.sessions)

def demo():
    """演示使用"""
    print("=" * 60)
    print("User Authentication System v1 Demo")
    print("=" * 60)
    
    auth = UserAuth()
    
    # 注册用户
    print("\n📝 注册用户:")
    result = auth.register_user("admin", "password123", "admin@example.com")
    print(f"  状态：{result['status']}")
    print(f"  消息：{result['message']}")
    
    # 用户登录
    print("\n🔐 用户登录:")
    result = auth.login("admin", "password123")
    if result["status"] == "success":
        token = result["token"]
        print(f"  状态：{result['status']}")
        print(f"  Token: {token[:20]}...")
        print(f"  过期：{result['expires_at']}")
        
        # 验证 token
        print("\n✅ 验证 Token:")
        result = auth.verify_token(token)
        print(f"  状态：{result['status']}")
        if result["status"] == "success":
            print(f"  用户：{result['user']['username']}")
            print(f"  角色：{result['user']['role']}")
        
        # 用户登出
        print("\n🚪 用户登出:")
        result = auth.logout(token)
        print(f"  状态：{result['status']}")
    else:
        print(f"  状态：{result['status']}")
        print(f"  消息：{result['message']}")
    
    # 统计信息
    print("\n📊 统计信息:")
    print(f"  用户数：{auth.get_user_count()}")
    print(f"  会话数：{auth.get_session_count()}")
    
    print("-" * 60)
    print("[COMPLETE]")
    print("=" * 60)

if __name__ == "__main__":
    demo()
