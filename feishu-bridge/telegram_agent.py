"""
Telegram Agent — 持久化对话 Agent 服务
- Long polling 获取消息
- MiniMax API 快速响应
- CLI 备用（需要插件时）
- 对话历史按 chat_id 隔离

依赖: pip install lark-oapi (仅飞书相关)

用法: python telegram_agent.py
"""

import json
import logging
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# ============ 配置 ============
TELEGRAM_BOT_TOKEN = "8795362409:AAFO7a3nIYnkLcLeAoLN0DqkTv0aFcHiDhc"
MINIMAX_API_KEY = "sk-cp-zNNt30MolJOgSwdsdgA8BJbLoKmiV3Zttz_IgZkapeyjoPPq-qYFSw-XiMZIIUyeH4PTB4Y86QXu_wKR8JvmZ9PbkkMmMwDTC6QgHznXopDTl0nBZ9AQHQ8"
MINIMAX_API_URL = "https://api.minimaxi.com/v1/chat/completions"
WORKSPACE = Path("D:/OpenClaw/workspace")
HISTORY_DIR = WORKSPACE / "feishu-bridge" / "conversations"
LOG_FILE = WORKSPACE / "feishu-bridge" / "telegram.log"
LOCK_FILE = WORKSPACE / "feishu-bridge" / "telegram.lock"
CLAUDE_EXE = "C:/Users/adm/.claude/downloads/claude-2.1.81-win32-x64.exe"
MAX_TOKENS = 1500
MAX_RETRIES = 3
RETRY_DELAY = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("telegram_agent")

# ============ 对话历史管理 ============
def load_history(chat_id: str) -> list:
    """加载对话历史"""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    f = HISTORY_DIR / f"{chat_id}.json"
    if f.exists():
        with open(f, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(chat_id: str, history: list):
    """保存对话历史"""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_DIR / f"{chat_id}.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(chat_id: str, role: str, content: str):
    """添加消息到历史"""
    history = load_history(chat_id)
    history.append({"role": role, "content": content, "time": datetime.now().isoformat()})
    if len(history) > 50:
        history = history[-50:]
    save_history(chat_id, history)

def format_history_for_prompt(history: list) -> str:
    """格式化历史为可读字符串"""
    if not history:
        return ""
    lines = []
    for msg in history[-20:]:
        role = "用户" if msg["role"] == "user" else "助手"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)

# ============ Telegram API ============
def send_message(chat_id: str, text: str):
    """发送消息到 Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        logger.error(f"发送失败: {e}")
        return False

def get_updates(offset: int = None, timeout: int = 30) -> list:
    """获取 Telegram 更新（long polling）"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": timeout}
    if offset:
        params["offset"] = offset
    url_with_params = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url_with_params, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout + 10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                return result.get("result", [])
    except Exception as e:
        logger.error(f"获取更新失败: {e}")
    return []

# ============ MiniMax API ============
def call_minimax(messages: list) -> str:
    """调用 MiniMax API（带重试）"""
    payload = {
        "model": "MiniMax-M2.7-highspeed",
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": 0.7
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MINIMAX_API_KEY}"
    }
    req = urllib.request.Request(
        MINIMAX_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            last_error = e
            logger.warning(f"MiniMax 调用失败（第{attempt+1}次）: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    logger.error(f"MiniMax 最终错误: {last_error}")
    return f"API 错误: {last_error}"

def call_minimax_api(history: list, text: str) -> str:
    """构建消息并调用 MiniMax API"""
    system_msg = {
        "role": "system",
        "content": "你是 Claude Code，通过 Telegram 与用户对话。请用中文回复，保持简洁（不超过500字）。如果需要执行命令或操作，完成后告诉用户结果。认真记住对话历史，保持上下文连贯。"
    }
    messages = [system_msg]
    for msg in history[-20:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": text})
    return call_minimax(messages)

# ============ Claude CLI 备用 ============
def call_claude_cli(prompt: str, chat_id: str) -> str:
    """调用 Claude CLI（需要插件时）"""
    env = os.environ.copy()
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
    exe = CLAUDE_EXE
    cmd = f'"{exe}" --print {prompt}'
    try:
        logger.info(f"调用 Claude CLI (chat_id={chat_id})...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            shell=True,
            cwd=WORKSPACE,
            env=env,
        )
        output = result.stdout.strip() if result.stdout else ""
        if not output:
            output = result.stderr.strip() if result.stderr else ""
        return output if output else None
    except Exception as e:
        logger.error(f"CLI 错误: {e}")
        return None

# ============ 消息处理 ============
msg_queue = queue.Queue()
processed_ids = set()  # 避免重复处理

def process_message(chat_id: str, text: str, msg_id: int):
    """处理单条消息"""
    logger.info(f"处理: chat_id={chat_id}, msg_id={msg_id}, text={text[:50]}...")

    # 加载历史
    history = load_history(chat_id)

    # 快速回复
    send_message(chat_id, "正在思考...")

    start = time.time()
    # 直接用 CLI 执行用户指令
    response = call_claude_cli(text, chat_id)
    if response is None:
        response = "CLI 执行失败"

    elapsed = time.time() - start
    logger.info(f"响应时间: {elapsed:.1f}秒")

    # 保存历史
    add_to_history(chat_id, "user", text)
    add_to_history(chat_id, "assistant", response)

    # 发回复
    send_message(chat_id, response)
    logger.info(f"回复成功: {response[:50]}...")

def process_queue():
    """后台处理队列"""
    while True:
        try:
            item = msg_queue.get(timeout=1)
            if item is None:
                break
            process_message(item["chat_id"], item["text"], item["msg_id"])
            msg_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.exception(f"处理异常: {e}")

# ============ Long Polling 接收 ============
def poll_messages():
    """Long polling 循环"""
    offset = None
    while True:
        try:
            updates = get_updates(offset=offset, timeout=30)
            for update in updates:
                update_id = update.get("update_id")
                message = update.get("message", {})

                # 跳过已处理的
                if update_id in processed_ids:
                    continue
                processed_ids.add(update_id)

                # 忽略非消息更新
                if not message:
                    continue

                chat_id = str(message.get("chat", {}).get("id", ""))
                msg_id = message.get("message_id")
                text = message.get("text", "").strip()

                # 忽略空消息
                if not text:
                    continue

                # 忽略 bot 自己的消息
                # (Telegram bot 不会收到自己发的消息，这里留个钩子)

                logger.info(f"收到消息: chat_id={chat_id}, msg_id={msg_id}, text={text[:50]}...")
                msg_queue.put({"chat_id": chat_id, "text": text, "msg_id": msg_id})

                # 更新 offset
                offset = update_id + 1

        except Exception as e:
            logger.exception(f"Polling 异常: {e}")
            time.sleep(5)

# ============ 启动 ============
def main():
    # Lock file - 确保只有一个实例运行
    if LOCK_FILE.exists():
        with open(LOCK_FILE, "r") as f:
            old_pid = f.read().strip()
        if old_pid:
            try:
                os.kill(int(old_pid), 0)
                logger.error(f"另一个实例正在运行 (PID: {old_pid})，退出")
                sys.exit(1)
            except (OSError, ValueError):
                pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    import atexit
    def cleanup():
        try:
            LOCK_FILE.unlink()
        except:
            pass
    atexit.register(cleanup)

    logger.info("=" * 50)
    logger.info("Telegram Agent 启动")
    logger.info(f"Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    logger.info(f"API: {MINIMAX_API_URL}")
    logger.info("=" * 50)

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    # 先清空之前的 updates（避免处理旧消息）
    logger.info("清空旧 updates...")
    get_updates(offset=0, timeout=0)

    # 启动处理队列
    processor = threading.Thread(target=process_queue, daemon=True)
    processor.start()

    # 启动 polling
    poll_thread = threading.Thread(target=poll_messages, daemon=True)
    poll_thread.start()

    logger.info("Agent 运行中，按 Ctrl+C 停止")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("停止 Agent")
        msg_queue.put(None)
        poll_thread.join(timeout=5)
        processor.join(timeout=5)

if __name__ == "__main__":
    main()
