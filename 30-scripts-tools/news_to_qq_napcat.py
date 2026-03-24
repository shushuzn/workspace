#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News to QQ (NapCat) - 基于 NapCat 的 QQ 群推送

NapCat: https://github.com/NapNeko/NapCatQQ

用法:
    py news_to_qq_napcat.py send <title> <url>
    py news_to_qq_napcat.py test
    py news_to_qq_napcat.py digest <count>

配置:
    修改下方的 CONFIG
"""

import sys
import subprocess
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
    "base_url": "http://127.0.0.1:3000",  # NapCat 地址
    "token": "",  # 如果有设置 Token，填在这里
    "group_id": "597818978",  # QQ 群号
}

BASE_DIR = Path(r"D:\OpenClaw\workspace\30-scripts-tools")
QQ_HISTORY_FILE = BASE_DIR / "qq_news_history_napcat.json"


# ============================================================
# 工具函数
# ============================================================


def get_headers():
    """获取请求头"""
    headers = {"Content-Type": "application/json"}
    if CONFIG.get("token"):
        headers["Authorization"] = f"Bearer {CONFIG['token']}"
    return headers


def api_request(endpoint, data=None, method="POST"):
    """发送 API 请求到 NapCat"""
    url = f"{CONFIG['base_url']}{endpoint}"
    headers = get_headers()

    req_data = json.dumps(data).encode("utf-8") if data else None

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"HTTP {e.code}: {error_body[:500]}")


# ============================================================
# NapCat API 封装
# ============================================================


def send_group_message(group_id, message, auto_escape=False):
    """
    发送群消息

    Args:
        group_id: QQ 群号
        message: 消息内容（字符串或消息段数组）
        auto_escape: 是否转义 CQ 码
    """
    data = {"group_id": group_id, "message": message, "auto_escape": auto_escape}

    result = api_request("/send_group_msg", data=data)

    if result.get("status") != "ok":
        raise Exception(f"Send failed: {result.get('msg', result)}")

    return result


def get_group_list():
    """获取群列表"""
    return api_request("/get_group_list", data={}, method="POST")


def get_group_info(group_id):
    """获取群信息"""
    return api_request("/get_group_info", data={"group_id": group_id}, method="POST")


def get_login_info():
    """获取登录信息"""
    return api_request("/get_login_info", data={}, method="POST")


# ============================================================
# 消息构造
# ============================================================


def build_text_message(text):
    """构造纯文本消息"""
    return [{"type": "text", "data": {"text": text}}]


def build_news_message(title, url, summary=""):
    """构造新闻消息（图文）"""
    msg = f"📰 {title}\n"
    if summary:
        msg += f"\n{summary}\n"
    msg += f"\n{url}"

    return build_text_message(msg)


def build_cq_message(title, url, image_url=None):
    """构造 CQ 码消息"""
    msg = f"[CQ:share,title={title},url={url}]"
    return msg


# ============================================================
# 历史记录管理
# ============================================================


def load_history():
    """加载发送历史"""
    if QQ_HISTORY_FILE.exists():
        try:
            return json.load(open(QQ_HISTORY_FILE, "r", encoding="utf-8"))
        except:
            pass
    return {"sent": [], "count": 0}


def save_history(history):
    """保存发送历史"""
    json.dump(
        history,
        open(QQ_HISTORY_FILE, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )


def is_duplicate(history, title):
    """检查是否重复"""
    for item in history.get("sent", []):
        if item.get("title") == title:
            return True
    return False


def add_to_history(history, title, url):
    """添加到历史"""
    history["sent"].append(
        {"title": title, "url": url, "time": datetime.now().isoformat()}
    )
    history["count"] = len(history["sent"])

    # 只保留最近 500 条
    if len(history["sent"]) > 500:
        history["sent"] = history["sent"][-500:]

    save_history(history)


# ============================================================
# 命令实现
# ============================================================


def cmd_send(args):
    """发送单条新闻"""
    if len(args) < 2:
        print("[ERROR] 用法: py news_to_qq_napcat.py send <title> <url>")
        return

    title = args[0]
    url = args[1]

    # 检查重复
    history = load_history()
    if is_duplicate(history, title):
        print(f"[SKIP] Duplicate: {title[:30]}...")
        return

    try:
        # 构造消息
        message = build_news_message(title, url)

        # 发送
        result = send_group_message(CONFIG["group_id"], message)

        # 记录历史
        add_to_history(history, title, url)

        print(f"[OK] Sent: {title[:40]}...")
        print(f"[INFO] Message ID: {result.get('data', {}).get('message_id', 'N/A')}")

    except Exception as e:
        print(f"[ERROR] {e}")


def cmd_test(args):
    """测试发送"""
    try:
        # 测试连接
        login_info = get_login_info()
        print(f"[OK] Connected to NapCat")
        print(f"[INFO] QQ: {login_info.get('data', {}).get('user_id', 'N/A')}")
        print(f"[INFO] Nickname: {login_info.get('data', {}).get('nickname', 'N/A')}")

        # 获取群列表
        groups = get_group_list()
        group_list = groups.get("data", [])
        print(f"[INFO] Groups: {len(group_list)}")

        # 检查目标群
        target_found = any(
            str(g.get("group_id")) == CONFIG["group_id"] for g in group_list
        )
        if target_found:
            print(f"[OK] Target group {CONFIG['group_id']} found")
        else:
            print(f"[WARN] Target group {CONFIG['group_id']} not in list")
            print(f"[INFO] Available groups:")
            for g in group_list[:5]:
                print(f"  - {g.get('group_id')}: {g.get('group_name', 'N/A')}")

        # 发送测试消息
        test_msg = f"🤖 OpenClaw NapCat Test\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        message = build_text_message(test_msg)

        result = send_group_message(CONFIG["group_id"], message)
        print(f"[OK] Test message sent")
        print(f"[INFO] Message ID: {result.get('data', {}).get('message_id', 'N/A')}")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("[HINT] 请确认 NapCat 已启动，且地址正确")


def cmd_digest(args):
    """发送新闻摘要"""
    # 从新闻历史读取今日新闻
    hist_file = BASE_DIR / "news_history.json"
    if not hist_file.exists():
        print("[ERROR] 新闻历史文件不存在")
        return

    try:
        news_data = json.load(open(hist_file, "r", encoding="utf-8"))
        all_news = news_data.get("sent", [])

        # 取最近的新闻
        count = int(args[0]) if args else 5
        recent = all_news[-count:] if len(all_news) > count else all_news

        if not recent:
            print("[INFO] 没有新闻")
            return

        # 构造摘要
        lines = [f"📰 新闻摘要 ({datetime.now().strftime('%m-%d %H:%M')})\n"]
        for i, n in enumerate(recent, 1):
            title = n.get("title", "无标题")[:25]
            lines.append(f"{i}. {title}")

        msg = "\n".join(lines)
        message = build_text_message(msg)

        result = send_group_message(CONFIG["group_id"], message)

        print(f"[OK] Digest sent: {len(recent)} items")
        print(f"[INFO] Message ID: {result.get('data', {}).get('message_id', 'N/A')}")

    except Exception as e:
        print(f"[ERROR] {e}")


def cmd_status(args):
    """查看状态"""
    try:
        # 获取登录信息
        login_info = get_login_info()
        qq_id = login_info.get("data", {}).get("user_id", "N/A")
        nickname = login_info.get("data", {}).get("nickname", "N/A")

        # 获取群列表
        groups = get_group_list()
        group_count = len(groups.get("data", []))

        # 获取历史
        history = load_history()

        print(f"\n📊 NapCat QQ 推送状态")
        print(f"  机器人 QQ: {qq_id}")
        print(f"  昵称: {nickname}")
        print(f"  所在群数: {group_count}")
        print(f"  目标群: {CONFIG['group_id']}")
        print(f"  NapCat 地址: {CONFIG['base_url']}")
        print(f"  总发送: {history.get('count', 0)}")
        print(
            f"  今日: {len([x for x in history.get('sent', []) if datetime.now().strftime('%Y-%m-%d') in x.get('time', '')])}"
        )

    except Exception as e:
        print(f"[ERROR] {e}")
        print("[HINT] 请确认 NapCat 已启动")


def cmd_groups(args):
    """列出所有群"""
    try:
        groups = get_group_list()
        group_list = groups.get("data", [])

        print(f"\n👥 群列表 ({len(group_list)} 个)")
        print("-" * 40)

        for g in group_list:
            gid = g.get("group_id", "N/A")
            name = g.get("group_name", "N/A")
            member_count = g.get("member_count", "?")
            print(f"  {gid}: {name} ({member_count}人)")

    except Exception as e:
        print(f"[ERROR] {e}")


# ============================================================
# 主入口
# ============================================================


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return
    print("[OK] Critic Review Passed")

    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        "send": cmd_send,
        "test": cmd_test,
        "digest": cmd_digest,
        "status": cmd_status,
        "groups": cmd_groups,
    }

    if cmd in ("help", "-h", "--help"):
        print(__doc__)
        print("\n命令:")
        for c in commands:
            print(f"  {c}")
        return

    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        print("使用 `py news_to_qq_napcat.py help` 查看帮助")


if __name__ == "__main__":
    main()
