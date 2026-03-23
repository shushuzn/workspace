#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu ↔ Control UI 消息同步工具
双向同步飞书和 Control UI 的消息

功能:
1. 监听飞书消息 → 转发到 Control UI
2. 监听 Control UI 消息 → 转发到飞书
3. 保持会话上下文

使用:
python feishu-ui-sync.py --watch
python feishu-ui-sync.py --sync-last 10
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
GATEWAY_URL = "http://127.0.0.1:18789"
FEISHU_USER_ID = "ou_72a847b95fc25870dcdd8ce56d929252"
SYNC_STATE_FILE = Path(__file__).parent.parent / "13-memory" / "feishu-ui-sync-state.json"


class MessageSync:
    """消息同步器"""

    def __init__(self, gateway_url: str = GATEWAY_URL, feishu_user_id: str = FEISHU_USER_ID):
        self.gateway_url = gateway_url
        self.feishu_user_id = feishu_user_id
        self.state = self.load_state()

    def load_state(self) -> Dict:
        """加载同步状态"""
        if SYNC_STATE_FILE.exists():
            try:
                with open(SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        return {
            "last_feishu_msg_id": None,
            "last_ui_msg_id": None,
            "last_sync_time": None,
            "synced_count": 0
        }

    def save_state(self):
        """保存同步状态"""
        SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_feishu_messages(self, limit: int = 10) -> List[Dict]:
        """获取最近的飞书消息"""
        try:
            # 使用 feishu_im_user_get_messages API
            # 这里需要通过 Gateway 调用
            result = requests.post(
                f"{self.gateway_url}/api/tool",
                json={
                    "tool": "feishu_im_user_get_messages",
                    "params": {
                        "chat_id": f"p2p_{self.feishu_user_id}",
                        "page_size": limit
                    }
                },
                timeout=10
            )

            if result.status_code == 200:
                data = result.json()
                return data.get("messages", [])
        except Exception as e:
            print(f"⚠️ 获取飞书消息失败：{e}")

        return []

    def get_ui_messages(self, limit: int = 10) -> List[Dict]:
        """获取最近的 Control UI 消息"""
        try:
            # 通过 sessions_history 获取
            result = requests.post(
                f"{self.gateway_url}/api/tool",
                json={
                    "tool": "sessions_history",
                    "params": {
                        "sessionKey": "agent:main:main",
                        "limit": limit
                    }
                },
                timeout=10
            )

            if result.status_code == 200:
                data = result.json()
                return data.get("messages", [])
        except Exception as e:
            print(f"⚠️ 获取 UI 消息失败：{e}")

        return []

    def send_to_feishu(self, message: str):
        """发送消息到飞书"""
        try:
            result = requests.post(
                f"{self.gateway_url}/api/tool",
                json={
                    "tool": "feishu_im_user_message",
                    "params": {
                        "action": "send",
                        "msg_type": "text",
                        "receive_id_type": "open_id",
                        "receive_id": self.feishu_user_id,
                        "content": json.dumps({"text": message}, ensure_ascii=False)
                    }
                },
                timeout=10
            )

            if result.status_code == 200:
                print(f"✅ 已发送到飞书：{message[:50]}...")
                return True
        except Exception as e:
            print(f"❌ 发送到飞书失败：{e}")

        return False

    def send_to_ui(self, message: str):
        """发送消息到 Control UI (通过 sessions_send)"""
        try:
            result = requests.post(
                f"{self.gateway_url}/api/tool",
                json={
                    "tool": "sessions_send",
                    "params": {
                        "sessionKey": "agent:main:main",
                        "message": message
                    }
                },
                timeout=10
            )

            if result.status_code == 200:
                print(f"✅ 已发送到 UI: {message[:50]}...")
                return True
        except Exception as e:
            print(f"❌ 发送到 UI 失败：{e}")

        return False

    def sync_feishu_to_ui(self, new_messages: List[Dict]):
        """同步飞书消息到 UI"""
        for msg in reversed(new_messages):
            msg_id = msg.get("message_id")
            content = msg.get("content", "")
            sender = msg.get("sender", {})

            # 跳过已同步的消息
            if msg_id == self.state.get("last_feishu_msg_id"):
                continue

            # 跳过自己的消息
            if sender.get("id") == "bot":
                continue

            # 转发到 UI
            sender_name = sender.get("name", "飞书用户")
            ui_message = f"[飞书] {sender_name}: {content}"
            self.send_to_ui(ui_message)

            # 更新状态
            self.state["last_feishu_msg_id"] = msg_id
            self.state["last_sync_time"] = datetime.now().isoformat()
            self.state["synced_count"] += 1

        self.save_state()

    def sync_ui_to_feishu(self, new_messages: List[Dict]):
        """同步 UI 消息到飞书"""
        for msg in reversed(new_messages):
            msg_id = msg.get("id") or msg.get("message_id")
            content = msg.get("content", "")
            role = msg.get("role", "user")

            # 跳过已同步的消息
            if msg_id == self.state.get("last_ui_msg_id"):
                continue

            # 只同步用户消息
            if role != "user":
                continue

            # 跳过工具调用消息
            if "tool" in content.lower() or content.startswith("/"):
                continue

            # 转发到飞书
            feishu_message = f"[UI] {content}"
            self.send_to_feishu(feishu_message)

            # 更新状态
            self.state["last_ui_msg_id"] = msg_id
            self.state["last_sync_time"] = datetime.now().isoformat()
            self.state["synced_count"] += 1

        self.save_state()

    def sync_once(self):
        """执行一次同步"""
        print(f"\n🔄 开始同步... ({datetime.now().strftime('%H:%M:%S')})")

        # 获取新消息
        feishu_msgs = self.get_feishu_messages(limit=5)
        ui_msgs = self.get_ui_messages(limit=5)

        # 同步
        if feishu_msgs:
            print(f"📥 飞书消息：{len(feishu_msgs)} 条")
            self.sync_feishu_to_ui(feishu_msgs)

        if ui_msgs:
            print(f"📥 UI 消息：{len(ui_msgs)} 条")
            self.sync_ui_to_feishu(ui_msgs)

        print(f"✅ 同步完成 (累计：{self.state['synced_count']} 条)")

    def watch(self, interval: int = 30):
        """持续监听并同步"""
        print(f"🚀 启动消息同步监听...")
        print(f"📊 飞书用户：{self.feishu_user_id}")
        print(f"🔄 同步间隔：{interval}秒")
        print(f"💾 状态文件：{SYNC_STATE_FILE}")
        print(f"{'=' *60}\n")

        try:
            while True:
                self.sync_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\n\n👋 停止同步 (累计同步：{self.state['synced_count']} 条)")


def main():
    parser = argparse.ArgumentParser(description='Feishu ↔ UI 消息同步工具')
    parser.add_argument('--watch', '-w', action='store_true', help='持续监听模式')
    parser.add_argument('--interval', '-i', type=int, default=30, help='监听间隔 (秒)')
    parser.add_argument('--sync-last', '-s', type=int, help='同步最近 N 条消息')
    parser.add_argument('--gateway', '-g', default=GATEWAY_URL, help='Gateway URL')
    parser.add_argument('--user', '-u', default=FEISHU_USER_ID, help='飞书用户 ID')
    parser.add_argument('--reset', '-r', action='store_true', help='重置同步状态')

    args = parser.parse_args()

    sync = MessageSync(gateway_url=args.gateway, feishu_user_id=args.user)

    if args.reset:
        sync.state = {
            "last_feishu_msg_id": None,
            "last_ui_msg_id": None,
            "last_sync_time": None,
            "synced_count": 0
        }
        sync.save_state()
        print("✅ 同步状态已重置")
        return

    if args.sync_last:
        print(f"🔄 同步最近 {args.sync_last} 条消息...")
        sync.sync_once()
        return

    if args.watch:
        sync.watch(interval=args.interval)
        return

    # 默认执行一次同步
    sync.sync_once()


if __name__ == '__main__':
    main()
