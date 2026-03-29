"""
飞书 Webhook 服务 — 双向实时对话
轻量版，不依赖 WebSocket，直接用 HTTP 回调

依赖: pip install flask anthropic
"""

import json
import os
import subprocess
import threading
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify

# ============ 配置 ============
APP_ID = "cli_a93a6936eff81bcd"
APP_SECRET = "vWIWGFZPYBi6clKb1IV5JfDGnWrT1bra"
WORKSPACE = Path("D:/OpenClaw/workspace")
HISTORY_DIR = WORKSPACE / "feishu-bridge" / "conversations"
PORT = 8080

# ============ Flask App ============
app = Flask(__name__)

def get_token():
    """获取 tenant_access_token"""
    import urllib.request
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["tenant_access_token"]


def send_reply(chat_id: str, text: str, token: str):
    """发送回复到飞书"""
    import urllib.request
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("code") == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False


def load_conversation(chat_id: str) -> list:
    """加载对话历史"""
    history_file = HISTORY_DIR / f"{chat_id}.json"
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_conversation(chat_id: str, history: list):
    """保存对话历史"""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    history_file = HISTORY_DIR / f"{chat_id}.json"
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def build_prompt(messages: list, new_message: str) -> str:
    """构建带上下文的 prompt"""
    history_text = ""
    if messages:
        history_text = "\n\n=== 对话历史 ===\n"
        for msg in messages[-10:]:  # 最近10条
            role = "用户" if msg["role"] == "user" else "助手"
            history_text += f"{role}: {msg['content']}\n"
        history_text += "==================\n\n"

    return (
        f"你是 Claude Code，通过飞书与用户对话。\n"
        f"{history_text}"
        f"用户最新消息: {new_message}\n\n"
        f"请用中文回复。如果需要执行命令或操作，完成后告诉用户结果。"
        f"保持简洁，回复不要超过500字。"
    )


def run_claude(prompt: str) -> str:
    """调用 Claude Code 处理"""
    env = os.environ.copy()
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    exe = "C:/Users/adm/.claude/downloads/claude-2.1.81-win32-x64.exe"
    cmd = f'"{exe}" --print {prompt}'

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            shell=True,
            cwd=WORKSPACE,
            env=env,
        )
        output = result.stdout.strip() if result.stdout else ""
        if not output:
            output = result.stderr.strip() if result.stderr else "处理完成"
        return output[:1000]  # 限制长度
    except subprocess.TimeoutExpired:
        return "处理超时，请稍后再试。"
    except Exception as e:
        return f"处理失败: {e}"


def process_message(chat_id: str, text: str, msg_id: str):
    """处理消息 - 在后台线程运行"""
    # 加载历史
    history = load_conversation(chat_id)

    # 添加用户消息
    history.append({
        "role": "user",
        "content": text,
        "time": datetime.now().isoformat(),
        "msg_id": msg_id
    })

    # 构建 prompt
    prompt = build_prompt(history, text)

    # 发送"正在思考"
    try:
        token = get_token()
        send_reply(chat_id, "正在思考...", token)
    except:
        pass

    # 调用 Claude
    response = run_claude(prompt)

    # 添加助手回复
    history.append({
        "role": "assistant",
        "content": response,
        "time": datetime.now().isoformat()
    })

    # 保存历史
    save_conversation(chat_id, history)

    # 发回飞书
    try:
        token = get_token()
        send_reply(chat_id, response, token)
    except Exception as e:
        print(f"发送回复失败: {e}")


@app.route("/webhook/feishu", methods=["POST"])
def webhook():
    """飞书 Webhook 入口"""
    try:
        data = request.get_json()
        print(f"收到消息: {json.dumps(data, ensure_ascii=False)[:200]}")

        # 解析消息
        event = data.get("event", {})
        message = event.get("message", {})
        sender = event.get("sender", {})

        chat_id = message.get("chat_id", "")
        msg_id = message.get("message_id", "")
        content_str = message.get("content", "{}")

        # 解析文本
        try:
            content = json.loads(content_str)
            text = content.get("text", "").strip()
        except:
            text = content_str.strip()

        # 忽略空消息和 bot 自己的消息
        sender_id = sender.get("sender_id", {}).get("open_id", "")
        if not text or sender_id == APP_ID or sender_id == "cli_a93a6936eff81bcd":
            return jsonify({"code": 0})

        print(f"处理消息: chat_id={chat_id}, text={text[:50]}...")

        # 后台处理（不阻塞响应）
        thread = threading.Thread(
            target=process_message,
            args=(chat_id, text, msg_id)
        )
        thread.daemon = True
        thread.start()

        return jsonify({"code": 0})

    except Exception as e:
        print(f"Webhook 异常: {e}")
        return jsonify({"code": 1, "msg": str(e)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})


if __name__ == "__main__":
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    print(f"飞书 Webhook 服务启动，端口 {PORT}")
    print(f"Webhook URL: http://localhost:{PORT}/webhook/feishu")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
