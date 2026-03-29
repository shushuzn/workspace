"""
飞书 Bridge — 实时接收飞书消息，触发 Claude Code 处理，结果发回飞书

依赖安装: pip install lark-oapi anthropic

用法: python feishu_bridge.py
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
import signal
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# 配置
APP_ID = "cli_a93a6936eff81bcd"
APP_SECRET = "vWIWGFZPYBi6clKb1IV5JfDGnWrT1bra"
MINIMAX_API_KEY = "sk-cp-zNNt30MolJOgSwdsdgA8BJbLoKmiV3Zttz_IgZkapeyjoPPq-qYFSw-XiMZIIUyeH4PTB4Y86QXu_wKR8JvmZ9PbkkMmMwDTC6QgHznXopDTl0nBZ9AQHQ8"
MINIMAX_API_URL = "https://api.minimaxi.com/v1/chat/completions"
WORKSPACE = Path("D:/OpenClaw/workspace")
QUEUE_FILE = WORKSPACE / "feishu-bridge" / "queue.json"
LOG_FILE = WORKSPACE / "feishu-bridge" / "bridge.log"
HISTORY_DIR = WORKSPACE / "feishu-bridge" / "conversations"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("feishu_bridge")

# 全局消息队列
msg_queue: queue.Queue = queue.Queue()
processing = threading.Event()
processing.set()  # 初始为空闲状态

# Claude CLI 进程池（预热）
claude_process = None
process_lock = threading.Lock()
CLAUDE_EXE = "C:/Users/adm/.claude/downloads/claude-2.1.81-win32-x64.exe"
WARMUP_PROMPT = "你是 Claude Code，通过飞书与用户对话。请用中文回复，保持简洁。"


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


def send_reply(chat_id: str, text: str, token: str, root_id: str = None):
    """通过 Feishu API 发送回复（reply 模式或新消息模式）"""
    import urllib.request

    if root_id:
        # 回复特定消息（thread 内）
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{root_id}/reply"
        payload = {
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        }
    else:
        # 统一用 chat_id 发消息
        receive_id = chat_id
        receive_id_type = "chat_id"
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}, ensure_ascii=False),
        }
        logger.info(f"发送消息: receive_id_type={receive_id_type}, receive_id={receive_id}, text={text[:30]}...")

    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("code") == 0:
                logger.info(f"消息发送成功: chat_id={chat_id}, reply={'是' if root_id else '否'}")
            else:
                logger.error(f"发送失败: code={result.get('code')}, msg={result.get('msg')}")
    except Exception as e:
        logger.error(f"发送异常: {e}")


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


def run_minimax(messages: list) -> str:
    """直接调用 MiniMax API，比 CLI 快很多"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MINIMAX_API_KEY}"
    }

    # 构建消息格式
    api_messages = []
    for msg in messages[:-1]:  # 历史消息
        api_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    # 最新用户消息
    api_messages.append({
        "role": "user",
        "content": messages[-1]["content"]
    })

    payload = {
        "model": "MiniMax-M2.7-highspeed",
        "messages": api_messages,
        "max_tokens": 500,
        "temperature": 0.7
    }

    req = urllib.request.Request(
        MINIMAX_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        logger.error(f"MiniMax API 错误: {e.code} {e.reason} {error_body[:200]}")
        return f"API 错误: {e.code}"
    except Exception as e:
        logger.error(f"MiniMax 请求失败: {e}")
        return f"请求失败: {e}"


def run_claude(message_text: str, chat_id: str = None, thread_id: str = None) -> str:
    """调用 Claude CLI 处理消息（带对话历史）"""
    env = os.environ.copy()
    env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    # 加载历史上下文
    history = []
    if chat_id:
        history = load_conversation(chat_id)

    # 构建 prompt
    prompt = build_prompt([], message_text)  # 历史已在 prompt 中

    exe = "C:/Users/adm/.claude/downloads/claude-2.1.81-win32-x64.exe"
    cmd = f'"{exe}" --print {prompt}'
    if thread_id:
        cmd += f" --resume {thread_id}"

    try:
        logger.info(f"调用 Claude CLI (chat_id={chat_id})...")
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
            output = result.stderr.strip() if result.stderr else "处理完成，无输出"

        # 保存对话历史
        if chat_id:
            history.append({"role": "user", "content": message_text, "time": datetime.now().isoformat()})
            history.append({"role": "assistant", "content": output, "time": datetime.now().isoformat()})
            save_conversation(chat_id, history)

        logger.info(f"Claude 返回: {output[:100]}...")
        return output[:1000]
    except subprocess.TimeoutExpired:
        logger.error("Claude 处理超时")
        return "处理超时，请稍后再试。"
    except Exception as e:
        logger.error(f"Claude 调用失败: {e}")
        return f"处理失败: {e}"


def process_queue():
    """后台线程：逐条处理消息队列"""
    global processing
    while True:
        try:
            item = msg_queue.get(timeout=1)
            if item is None:
                break

            chat_id = item["chat_id"]
            sender_id = item["sender_id"]
            text = item["text"]
            root_id = item.get("root_id")
            thread_id = item.get("thread_id")

            logger.info(f"处理消息: chat_id={chat_id}, text={text[:50]}...")
            processing.set()

            # 先回复"正在思考"
            try:
                token = get_token()
                send_reply(chat_id, "正在思考...", token)
            except Exception as e:
                logger.warning(f"无法发送'正在思考': {e}")

            # 调用 Claude Code 处理（带 chat_id 用于历史上下文）
            response = run_claude(text, chat_id, thread_id)

            # 发回飞书
            try:
                token = get_token()
                send_reply(chat_id, response, token)
            except Exception as e:
                logger.error(f"发送回复失败: {e}")

            processing.clear()
            msg_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            logger.exception(f"处理异常: {e}")
            processing.clear()


def on_message(data):
    """飞书 WebSocket 消息回调 — data 是 P2ImMessageReceiveV1 对象"""
    try:
        # data 是 lark-oapi 的 P2ImMessageReceiveV1EventContext 对象
        event_obj = data.event
        if not event_obj:
            return

        message = event_obj.message
        sender = event_obj.sender
        if not message or not sender:
            return

        chat_id = message.chat_id or ""
        msg_id = message.message_id or ""
        root_id = message.root_id or ""  # 用于 threading 回复
        content_str = message.content or ""

        # 解析消息文本
        text_content = ""
        if content_str:
            try:
                parsed = json.loads(content_str)
                text_content = parsed.get("text", "")
            except json.JSONDecodeError:
                text_content = content_str

        if not text_content:
            return

        # 获取发送者 open_id
        sender_id = ""
        if sender.sender_id:
            sender_id = sender.sender_id.open_id or ""

        # 忽略空消息和 bot 自己发的消息
        if sender_id == APP_ID:
            return

        # 忽略仅含"OK"等 emoji 反馈的消息
        if text_content.strip() in ("OK", "👍", "✅", "收到"):
            return

        logger.info(f"收到飞书消息: chat_id={chat_id}, sender={sender_id}, text={text_content[:50]}...")

        # root_id 用于在 thread 内回复；若无 thread 则用当前消息 ID
        thread_root = root_id if root_id else msg_id

        item = {
            "chat_id": chat_id,
            "sender_id": sender_id,
            "text": text_content,
            "root_id": thread_root,
            "timestamp": time.time(),
        }
        msg_queue.put(item)

    except Exception as e:
        logger.exception(f"消息解析异常: {e}")


def run_websocket():
    """在独立线程中运行飞书 WebSocket"""
    import lark_oapi as lark
    import lark_oapi.ws.client as _ws_mod

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        event_handler = (
            lark.EventDispatcherHandler.builder("", "")
            .register_p2_im_message_receive_v1(on_message)
            .build()
        )

        ws_client = lark.ws.Client(
            app_id=APP_ID,
            app_secret=APP_SECRET,
            event_handler=event_handler,
            log_level=lark.LogLevel.INFO,
        )
        ws_client.start()
    except Exception as e:
        logger.exception(f"WebSocket 错误: {e}")


def main():
    logger.info("=" * 50)
    logger.info("飞书 Bridge 启动")
    logger.info(f"APP_ID: {APP_ID}")
    logger.info(f"工作目录: {WORKSPACE}")
    logger.info("=" * 50)

    # 初始化目录
    bridge_dir = WORKSPACE / "feishu-bridge"
    bridge_dir.mkdir(exist_ok=True)
    LOG_FILE.parent.mkdir(exist_ok=True)

    # 启动消息处理线程
    processor = threading.Thread(target=process_queue, daemon=True)
    processor.start()

    # 启动 WebSocket
    ws_thread = threading.Thread(target=run_websocket, daemon=True)
    ws_thread.start()

    logger.info("Bridge 运行中，按 Ctrl+C 停止")

    try:
        while True:
            time.sleep(10)
            if not processing.is_set():
                logger.debug("空闲中...")
    except KeyboardInterrupt:
        logger.info("收到停止信号")
        msg_queue.put(None)
        ws_thread.join(timeout=5)
        processor.join(timeout=5)
        logger.info("Bridge 已停止")


if __name__ == "__main__":
    main()
