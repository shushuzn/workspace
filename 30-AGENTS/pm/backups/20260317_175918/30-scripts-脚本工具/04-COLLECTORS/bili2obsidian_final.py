import os
import re
import subprocess
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# ==================== 代理已固定为你的Clash 7897端口，无需修改 ====================
PROXY = "http://127.0.0.1:7897"
# ==================================================================================

# 加载环境变量
load_dotenv()

# 全局代理设置（确保所有请求走Clash）
os.environ["HTTP_PROXY"] = PROXY
os.environ["HTTPS_PROXY"] = PROXY
os.environ["ALL_PROXY"] = PROXY

# OpenAI客户端（强制走代理，解决连接超时问题）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=httpx.Client(proxy=PROXY, follow_redirects=True)
)

# Obsidian笔记库路径
OBSIDIAN_FOLDER = os.getenv("OBSIDIAN_FOLDER")

# ==================== 1. 优先获取CC字幕，无字幕再下载音频 ====================
def get_bilibili_content(url):
    print("🔍 正在检查视频CC字幕...")
    # 先尝试下载CC字幕
    subtitle_result = subprocess.run([
        "yt-dlp",
        "--proxy", PROXY,
        "--write-auto-sub",
        "--sub-lang", "zh-CN,zh",
        "--sub-format", "vtt",
        "--skip-download",
        "-o", "temp_sub",
        url
    ], capture_output=True, text=True)

    # 检查字幕是否下载成功
    subtitle_files = [f for f in os.listdir() if f.startswith("temp_sub") and f.endswith(".vtt")]
    if subtitle_files:
        print("✅ 找到CC字幕，优先使用字幕内容")
        with open(subtitle_files[0], "r", encoding="utf-8") as f:
            subtitle_text = f.read()
        # 清理字幕格式，去除时间轴和标签
        clean_text = re.sub(r'<.*?>', '', subtitle_text)
        clean_text = re.sub(r'^\d+:\d+:\d+.*$', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'\n+', '\n', clean_text).strip()
        # 清理临时字幕文件
        for f in subtitle_files:
            os.remove(f)
        return clean_text

    # 无字幕，下载音频转文字
    print("⚠️  未找到CC字幕，自动下载音频转文字")
    print("🎵 正在下载视频音频...")
    subprocess.run([
        "yt-dlp",
        "--proxy", PROXY,
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "64k",
        "-o", "temp_audio.mp3",
        url
    ], check=True)
    return "temp_audio.mp3"

# ==================== 2. 音频转文字（Whisper API） ====================
def audio_to_text(audio_path):
    print("🗣️ 正在通过Whisper转文字...")
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="zh",
            prompt="这是一个中文学习视频的音频，请准确转写内容，保留专业术语和关键信息"
        )
    # 清理临时音频文件
    os.remove(audio_path)
    return transcript.text

# ==================== 3. GPT生成Obsidian结构化笔记 ====================
def generate_obsidian_note(content, source_url):
    print("🧠 正在生成结构化学习笔记...")
    # 获取视频标题作为笔记文件名
    title_result = subprocess.run([
        "yt-dlp",
        "--proxy", PROXY,
        "--get-title",
        source_url
    ], capture_output=True, text=True)
    video_title = title_result.stdout.strip() if title_result.returncode == 0 else "B站学习笔记"
    # 清理标题中的非法字符
    safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title)

    prompt = f"""
你是专业的知识整理助手，将以下B站视频内容整理成符合Obsidian规范的Markdown结构化学习笔记，逻辑清晰、重点突出，适合后续复习和二次编辑。
严格按照以下格式输出，不要添加额外无关内容：

---
title: {video_title}
tags: [B站, 学习笔记, 自动化整理]
source: {source_url}
create_time: {os.popen('date +"%Y-%m-%d %H:%M:%S"').read().strip()}
---

## 核心主旨
一句话概括本视频的核心内容和学习价值

## 核心要点
- 分点列出视频的核心内容，不遗漏关键信息
- 每个要点简洁明了，逻辑递进

## 关键知识点
- 专业术语/核心概念：对应的详细解释
- 按重要程度排序

## 重点结论/金句
- 视频中的核心结论、关键观点或值得记录的金句

## 可执行行动项（如有）
- 从视频内容中提炼的可落地执行的步骤
- 无则写「无」

以下是视频完整内容：
{content}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content, safe_title

# ==================== 4. 自动保存到Obsidian笔记库 ====================
def save_to_obsidian(md_content, file_name):
    if not os.path.exists(OBSIDIAN_FOLDER):
        raise FileNotFoundError(f"Obsidian库路径不存在，请检查.env配置：{OBSIDIAN_FOLDER}")
    file_path = os.path.join(OBSIDIAN_FOLDER, f"{file_name}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"✅ 笔记已成功保存到Obsidian！路径：{file_path}")

# ==================== 主程序全自动化流程 ====================
if __name__ == "__main__":
    try:
        # 输入B站链接
        bili_url = input("🔗 请输入B站视频链接：").strip()
        if not bili_url:
            raise ValueError("请输入有效的B站视频链接")

        # 第一步：获取内容（字幕优先，无字幕走音频）
        content = get_bilibili_content(bili_url)

        # 第二步：如果是音频，转文字
        if content == "temp_audio.mp3":
            content = audio_to_text(content)

        # 第三步：生成Obsidian笔记
        note_content, note_title = generate_obsidian_note(content, bili_url)

        # 第四步：保存到Obsidian
        save_to_obsidian(note_content, note_title)

        print("🎉 全自动化流程执行完成！打开Obsidian即可查看整理好的笔记")

    except Exception as e:
        print(f"❌ 程序运行出错：{str(e)}")
        # 清理残留临时文件
        temp_files = ["temp_audio.mp3"] + [f for f in os.listdir() if f.startswith("temp_sub") and f.endswith(".vtt")]
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
