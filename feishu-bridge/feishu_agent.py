"""
飞书 Agent — 持久化对话 Agent 服务
- 持久进程，不冷启动
- MiniMax API 快速响应
- CLI 备用（需要插件时）
- 对话历史按 chat_id 隔离

依赖: pip install lark-oapi
"""

import asyncio
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
APP_ID = "cli_a93a6936eff81bcd"
APP_SECRET = "vWIWGFZPYBi6clKb1IV5JfDGnWrT1bra"
MINIMAX_API_KEY = "sk-cp-zNNt30MolJOgSwdsdgA8BJbLoKmiV3Zttz_IgZkapeyjoPPq-qYFSw-XiMZIIUyeH4PTB4Y86QXu_wKR8JvmZ9PbkkMmMwDTC6QgHznXopDTl0nBZ9AQHQ8"
MINIMAX_API_URL = "https://api.minimaxi.com/v1/chat/completions"
WORKSPACE = Path("D:/OpenClaw/workspace")
HISTORY_DIR = WORKSPACE / "feishu-bridge" / "conversations"
LOG_FILE = WORKSPACE / "feishu-bridge" / "agent.log"
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
logger = logging.getLogger("feishu_agent")

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
    # 保留最近50条
    if len(history) > 50:
        history = history[-50:]
    save_history(chat_id, history)

def format_history_for_prompt(history: list) -> str:
    """格式化历史为可读字符串（修复换行问题）"""
    if not history:
        return ""
    lines = []
    for msg in history[-20:]:  # 最近20条
        role = "用户" if msg["role"] == "user" else "助手"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)

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

# ============ MiniMax API ============
def call_minimax_api(history: list, text: str) -> str:
    """构建消息并调用 MiniMax API"""
    system_msg = {
        "role": "system",
        "content": "你是 Claude Code，通过飞书与用户对话。请用中文回复，保持简洁（不超过500字）。如果需要执行命令或操作，完成后告诉用户结果。认真记住对话历史，保持上下文连贯。"
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

    # 检查是否需要 CLI（检测是否包含插件关键字）
    plugin_keywords = ["github", "vercel", "git", "file", "search", "web", "mcp", "plugin"]
    needs_cli = any(kw in prompt.lower() for kw in plugin_keywords)

    if not needs_cli:
        return None  # 返回 None 表示用 API

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

# ============ 飞书 API ============
def get_token() -> str:
    """获取 token"""
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["tenant_access_token"]

def send_reply(chat_id: str, text: str, token: str):
    """发送回复"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("code") == 0
    except Exception as e:
        logger.error(f"发送失败: {e}")
        return False

# ============ 消息处理 ============
msg_queue = queue.Queue()

def process_message(chat_id: str, text: str, msg_id: str):
    """处理单条消息"""
    logger.info(f"处理: chat_id={chat_id}, text={text[:50]}...")

    # 加载历史
    history = load_history(chat_id)

    # 快速回复"正在思考..."
    try:
        token = get_token()
        send_reply(chat_id, "正在思考...", token)
    except:
        pass

    # 检测是否需要 CLI
    plugin_keywords = ["github", "vercel", "git", "file", "search", "web", "mcp", "plugin"]
    needs_cli = any(kw in text.lower() for kw in plugin_keywords)

    start = time.time()
    if needs_cli:
        # 使用 CLI（支持插件）
        history_text = format_history_for_prompt(history)
        prompt = f"你是 Claude Code，通过飞书与用户对话。\n\n=== 对话历史 ===\n{history_text}\n==================\n\n用户最新消息: {text}\n\n请用中文回复，保持简洁（不超过500字）。如果需要执行命令或操作，完成后告诉用户结果。"
        response = call_claude_cli(prompt, chat_id)
        if response is None:
            # CLI 返回 None，fallback 到 API
            response = call_minimax_api(history, text)
    else:
        # 使用 MiniMax API（快速）
        response = call_minimax_api(history, text)

    elapsed = time.time() - start
    logger.info(f"响应时间: {elapsed:.1f}秒")

    # 保存历史
    add_to_history(chat_id, "user", text)
    add_to_history(chat_id, "assistant", response)

    # 发回复
    try:
        token = get_token()
        send_reply(chat_id, response, token)
        logger.info(f"回复成功: {response[:50]}...")
    except Exception as e:
        logger.error(f"发送回复失败: {e}")

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

# ============ WebSocket 接收 ============
def on_message(data):
    """飞书消息回调"""
    try:
        event_obj = data.event
        if not event_obj:
            return

        message = event_obj.message
        sender = event_obj.sender
        if not message or not sender:
            return

        chat_id = message.chat_id or ""
        msg_id = message.message_id or ""
        content_str = message.content or ""

        # 解析文本
        try:
            content = json.loads(content_str)
            text = content.get("text", "").strip()
        except:
            text = content_str.strip()

        if not text:
            return

        # 忽略 bot 自己的消息
        sender_id = ""
        if sender.sender_id:
            sender_id = sender.sender_id.open_id or ""
        if sender_id == APP_ID:
            return

        # 忽略 emoji 反馈
        if text.strip() in ("OK", "👍", "✅", "收到"):
            return

        logger.info(f"收到消息: {text[:50]}...")
        msg_queue.put({"chat_id": chat_id, "text": text, "msg_id": msg_id})

    except Exception as e:
        logger.exception(f"消息解析异常: {e}")

def run_websocket():
    """运行飞书 WebSocket"""
    import lark_oapi as lark

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(on_message)
        .build()
    )

    ws_client = lark.ws.Client(
        app_id=APP_ID,
        app_secret=APP_SECRET,
        event_handler=handler,
        log_level=lark.LogLevel.INFO,
    )
    ws_client.start()

# ============ 启动 ============
def main():
    logger.info("=" * 50)
    logger.info("飞书 Agent 启动（持久化）")
    logger.info(f"API: {MINIMAX_API_URL}")
    logger.info("=" * 50)

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    # 启动处理队列
    processor = threading.Thread(target=process_queue, daemon=True)
    processor.start()

    # 启动 WebSocket
    ws_thread = threading.Thread(target=run_websocket, daemon=True)
    ws_thread.start()

    logger.info("Agent 运行中，按 Ctrl+C 停止")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("停止 Agent")
        msg_queue.put(None)
        ws_thread.join(timeout=5)
        processor.join(timeout=5)

if __name__ == "__main__":
    main()
