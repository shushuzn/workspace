#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News to QQ - QQ机器人新闻推送 (QQ Bot API v2)

用法:
    py news_to_qq.py send <title> <url>
    py news_to_qq.py test
    py news_to_qq.py digest <count>

配置:
    修改下方的 CONFIG
"""

import sys
import json
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置
# ============================================================

CONFIG = {
    "app_id": "1903639310",
    "client_secret": "vHe1PnCb1StLnGjDhChDjGnLtS1bCnP1",
    "token": "ERk8j8L4ykbNtGWlmmdO9FulQMETJbBS",
    "group_id": "597818978",  # 这是群号，需要转换成 group_openid
}

# API 端点
QQ_API_BASE = "https://api.sgroup.qq.com"  # 正式环境
# QQ_API_BASE = "https://sandbox.api.sgroup.qq.com"  # 沙箱环境
GET_TOKEN_URL = "https://bots.qq.com/app/getAppAccessToken"

BASE_DIR = Path(r'D:\OpenClaw\workspace\30-scripts-tools')
QQ_HISTORY_FILE = BASE_DIR / "qq_news_history.json"


# ============================================================
# 工具函数
# ============================================================

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def api_request(url, data=None, headers=None, method='POST'):
    """发送 API 请求"""
    req_headers = headers or {}
    req_headers['Content-Type'] = 'application/json'
    
    req_data = json.dumps(data).encode('utf-8') if data else None
    
    req = urllib.request.Request(
        url,
        data=req_data,
        headers=req_headers,
        method=method
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15, context=get_ssl_context()) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"HTTP {e.code}: {error_body[:500]}")


def get_access_token():
    """获取 Access Token"""
    data = {
        "appId": CONFIG['app_id'],
        "clientSecret": CONFIG['client_secret']
    }
    
    result = api_request(GET_TOKEN_URL, data=data)
    
    if result.get('code') != 0 and 'access_token' not in result:
        raise Exception(f"Token error: {result}")
    
    return result.get('access_token')


def send_group_message(access_token, group_openid, content, msg_type=0):
    """发送消息到群"""
    url = f"{QQ_API_BASE}/v2/groups/{group_openid}/messages"
    
    headers = {
        'Authorization': f"QQBot {access_token}",
        'Content-Type': 'application/json'
    }
    
    data = {
        "content": content,
        "msg_type": msg_type  # 0=文本, 2=markdown
    }
    
    result = api_request(url, data=data, headers=headers)
    
    if result.get('code') != 0:
        raise Exception(f"Send error: {result.get('message', result)}")
    
    return result


# ============================================================
# 历史记录管理
# ============================================================

def load_history():
    """加载发送历史"""
    if QQ_HISTORY_FILE.exists():
        try:
            return json.load(open(QQ_HISTORY_FILE, 'r', encoding='utf-8'))
        except:
            pass
    return {"sent": [], "count": 0}


def save_history(history):
    """保存发送历史"""
    json.dump(history, open(QQ_HISTORY_FILE, 'w', encoding='utf-8'), 
              ensure_ascii=False, indent=2)


def is_duplicate(history, title):
    """检查是否重复"""
    for item in history.get('sent', []):
        if item.get('title') == title:
            return True
    return False


def add_to_history(history, title, url):
    """添加到历史"""
    history['sent'].append({
        "title": title,
        "url": url,
        "time": datetime.now().isoformat()
    })
    history['count'] = len(history['sent'])
    
    # 只保留最近 500 条
    if len(history['sent']) > 500:
        history['sent'] = history['sent'][-500:]
    
    save_history(history)


# ============================================================
# 命令实现
# ============================================================

def cmd_send(args):
    """发送单条新闻"""
    if len(args) < 2:
        print("[ERROR] 用法: py news_to_qq.py send <title> <url>")
        return
    
    title = args[0]
    url = args[1]
    
    # 检查重复
    history = load_history()
    if is_duplicate(history, title):
        print(f"[SKIP] Duplicate: {title[:30]}...")
        return
    
    try:
        token = get_access_token()
        
        # 构造消息内容
        content = f"📰 {title}\n\n{url}"
        
        # 注意：需要使用 group_openid，不是群号
        # 这里先用群号，如果报错需要获取 group_openid
        send_group_message(token, CONFIG['group_id'], content)
        
        # 记录历史
        add_to_history(history, title, url)
        
        print(f"[OK] Sent: {title[:40]}...")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        # 如果报错 group_openid，提示用户
        if "group" in str(e).lower() or "openid" in str(e).lower():
            print("[HINT] 可能需要使用 group_openid 而不是群号")
            print("[HINT] 在 QQ 开放平台查看群聊的 openid")


def cmd_test(args):
    """测试发送"""
    try:
        token = get_access_token()
        print(f"[OK] Token obtained: {token[:30]}...")
        
        # 发送测试消息
        test_msg = f"🤖 OpenClaw QQ Bot Test\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        result = send_group_message(token, CONFIG['group_id'], test_msg)
        
        print(f"[OK] Test message sent")
        print(f"[INFO] Message ID: {result.get('id', 'N/A')}")
        
    except Exception as e:
        print(f"[ERROR] {e}")


def cmd_digest(args):
    """发送新闻摘要"""
    # 从新闻历史读取今日新闻
    hist_file = BASE_DIR / "news_history.json"
    if not hist_file.exists():
        print("[ERROR] 新闻历史文件不存在")
        return
    
    try:
        news_data = json.load(open(hist_file, 'r', encoding='utf-8'))
        all_news = news_data.get('sent', [])
        
        # 取最近的新闻
        count = int(args[0]) if args else 5
        recent = all_news[-count:] if len(all_news) > count else all_news
        
        if not recent:
            print("[INFO] 没有新闻")
            return
        
        # 构造摘要
        lines = [f"📰 新闻摘要 ({datetime.now().strftime('%m-%d %H:%M')})\n"]
        for i, n in enumerate(recent, 1):
            title = n.get('title', '无标题')[:25]
            lines.append(f"{i}. {title}")
        
        msg = '\n'.join(lines)
        
        token = get_access_token()
        send_group_message(token, CONFIG['group_id'], msg)
        
        print(f"[OK] Digest sent: {len(recent)} items")
        
    except Exception as e:
        print(f"[ERROR] {e}")


def cmd_status(args):
    """查看状态"""
    history = load_history()
    print(f"\n📊 QQ 推送统计")
    print(f"  总发送: {history.get('count', 0)}")
    print(f"  今日: {len([x for x in history.get('sent', []) if datetime.now().strftime('%Y-%m-%d') in x.get('time', '')])}")
    print(f"  目标群: {CONFIG['group_id']}")
    print(f"  App ID: {CONFIG['app_id']}")


# ============================================================
# 主入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    
    commands = {
        'send': cmd_send,
        'test': cmd_test,
        'digest': cmd_digest,
        'status': cmd_status,
    }
    
    if cmd in ('help', '-h', '--help'):
        print(__doc__)
        print("\n命令:")
        for c in commands:
            print(f"  {c}")
        return
    
    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        print("使用 `py news_to_qq.py help` 查看帮助")


if __name__ == "__main__":
    main()
