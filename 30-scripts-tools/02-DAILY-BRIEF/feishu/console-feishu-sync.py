#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console 会话 → 飞书 同步工具

功能:
1. 读取 Copaw Console 会话历史
2. 同步用户消息到飞书
3. 保持会话上下文

使用:
python console-feishu-sync.py --sync-last 10
python console-feishu-sync.py --watch --interval 30
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests

# Windows UTF-8 编码兼容
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 配置
COPOAW_CONFIG_DIR = Path.home() / ".copaw"
SESSIONS_DIR = COPOAW_CONFIG_DIR / "sessions"
SYNC_STATE_FILE = Path(__file__).parent / "console-feishu-sync-state.json"
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK"  # 需要配置


class ConsoleFeishuSync:
    """Console 会话到飞书的同步器"""

    def __init__(self):
        self.state = self.load_state()

    def load_state(self) -> Dict:
        """加载同步状态"""
        if SYNC_STATE_FILE.exists():
            try:
                with open(SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}")

        return {
            "last_sync_file": None,
            "last_sync_time": None,
            "last_message_id": None,
            "synced_count": 0
        }

    def save_state(self):
        """保存同步状态"""
        SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_recent_sessions(self, limit: int = 5) -> List[Path]:
        """获取最近的会话文件"""
        if not SESSIONS_DIR.exists():
            print(f"⚠️ 会话目录不存在：{SESSIONS_DIR}")
            return []

        session_files = list(SESSIONS_DIR.glob("*.json"))
        session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        return session_files[:limit]

    def read_session_messages(self, session_file: Path) -> List[Dict]:
        """读取会话文件中的消息"""
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 尝试不同的消息格式
            messages = []

            # 格式 1: messages 数组
            if "messages" in data:
                messages = data["messages"]
            # 格式 2: transcript 数组
            elif "transcript" in data:
                messages = data["transcript"]
            # 格式 3: 直接是数组
            elif isinstance(data, list):
                messages = data

            return messages
        except Exception as e:
            print(f"⚠️ 读取会话失败 {session_file.name}: {e}")
            return []

    def send_to_feishu(self, content: str, session_id: str = "") -> bool:
        """发送消息到飞书"""
        try:
            # 格式 1: 使用 Webhook (需要配置)
            if FEISHU_WEBHOOK_URL and "YOUR_WEBHOOK" not in FEISHU_WEBHOOK_URL:
                payload = {
                    "msg_type": "text",
                    "content": {
                        "text": f"[Console Session {session_id}]\n{content}"
                    }
                }
                response = requests.post(FEISHU_WEBHOOK_URL, json=payload, timeout=10)
                return response.status_code == 200

            # 格式 2: 使用飞书 API (需要 app_id/app_secret)
            # TODO: 从 config.json 读取飞书配置

            print(f"📨 飞书消息 (未配置 webhook): {content[:100]}...")
            return True

        except Exception as e:
            print(f"⚠️ 发送飞书消息失败：{e}")
            return False

    def sync_once(self, limit: int = 10):
        """执行一次同步"""
        print(f"🔄 开始同步... ({datetime.now().strftime('%H:%M:%S')})")

        session_files = self.get_recent_sessions(limit)
        if not session_files:
            print("⚠️ 没有找到会话文件")
            return

        new_messages_count = 0

        for session_file in session_files:
            # 跳过已同步的会话
            if self.state.get("last_sync_file") == str(session_file):
                continue

            messages = self.read_session_messages(session_file)
            session_id = session_file.stem

            for msg in messages:
                msg_id = msg.get("id") or msg.get("message_id")
                content = msg.get("content", "")
                role = msg.get("role", "")

                # 跳过已同步的消息
                if msg_id == self.state.get("last_message_id"):
                    continue

                # 只同步用户消息
                if role != "user":
                    continue

                # 跳过工具调用消息
                if "tool" in content.lower() or content.startswith("/"):
                    continue

                # 发送到飞书
                if self.send_to_feishu(content, session_id):
                    new_messages_count += 1
                    self.state["last_message_id"] = msg_id
                    print(f"✅ 已发送到飞书：[{session_id}] {content[:50]}...")

            self.state["last_sync_file"] = str(session_file)

        self.state["last_sync_time"] = datetime.now().isoformat()
        self.state["synced_count"] += new_messages_count
        self.save_state()

        print(f"✅ 同步完成 (新增：{new_messages_count} 条，累计：{self.state['synced_count']} 条)")

    def watch(self, interval: int = 30):
        """持续监听模式"""
        print(f"👁️ 开始监听 (间隔：{interval}秒)...")
        try:
            while True:
                self.sync_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n⏹️ 监听停止")

    def reset_state(self):
        """重置同步状态"""
        self.state = {
            "last_sync_file": None,
            "last_sync_time": None,
            "last_message_id": None,
            "synced_count": 0
        }
        self.save_state()
        print("✅ 同步状态已重置")


def main():
    parser = argparse.ArgumentParser(description="Console 会话 → 飞书同步工具")
    parser.add_argument("--sync-last", type=int, help="同步最近 N 条消息")
    parser.add_argument("--watch", action="store_true", help="持续监听模式")
    parser.add_argument("--interval", type=int, default=30, help="监听间隔 (秒)")
    parser.add_argument("--reset", action="store_true", help="重置同步状态")

    args = parser.parse_args()
    sync = ConsoleFeishuSync()

    if args.reset:
        sync.reset_state()
        return

    if args.sync_last:
        print(f"🔄 同步最近 {args.sync_last} 条消息...")
        sync.sync_once(limit=args.sync_last)
        return

    if args.watch:
        sync.watch(interval=args.interval)
        return

    # 默认执行一次同步
    sync.sync_once()


if __name__ == '__main__':
    main()
