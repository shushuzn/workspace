import os
import re
import time
import requests
import subprocess
from dotenv import load_dotenv

# ==================== 加载配置（新建.env文件） ====================
load_dotenv()
# 豆包API配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_SECRET_KEY = os.getenv("DOUBAO_SECRET_KEY")
# Obsidian配置
OBSIDIAN_FOLDER = os.getenv("OBSIDIAN_FOLDER")
# 代理（仅用于下载B站内容，国内网络可留空）
PROXY = os.getenv("PROXY", "")

# 设置代理环境变量
if PROXY:
    os.environ["HTTP_PROXY"] = PROXY
    os.environ["HTTPS_PROXY"] = PROXY

# ==================== 1. 获取豆包API令牌 ====================
def get_doubao_token():
    """获取豆包API调用令牌（有效期24小时）"""
    print("🔑 正在获取豆包API令牌...")
    url = "https://ark.cn-beijing.volces.com/api/v3/oauth2/token"
    headers = {"Content-Type": "application/json"}
    data = {
        "grant_type": "client_credentials",
        "client_id": DOUBAO_API_KEY,
        "client_secret": DOUBAO_SECRET_KEY
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误
        token = response.json()["access_token"]
        print("✅ 令牌获取成功")
        return token
    except Exception as e:
        raise Exception(f"❌ 令牌获取失败：{e}")

# ==================== 2. 提取B站视频内容 ====================
def get_bilibili_content(url):
    """提取B站视频字幕，无字幕则生成音频提示"""
    print("🔍 正在提取B站视频字幕...")
    
    # 下载字幕
    cmd = [
        "yt-dlp",
        "--write-auto-sub", "--sub-lang", "zh-CN,zh",
        "--sub-format", "vtt", "--skip-download", "-o", "temp_sub", url
    ]
    # 添加代理（如有）
    if PROXY:
        cmd.insert(1, "--proxy")
        cmd.insert(2, PROXY)
    
    subprocess.run(cmd, capture_output=True)

    # 处理字幕文件
    sub_files = [f for f in os.listdir() if f.startswith("temp_sub") and f.endswith(".vtt")]
    if sub_files:
        with open(sub_files[0], "r", encoding="utf-8") as f:
            txt = f.read()
        
        # 清理字幕格式
        txt = re.sub(r'<.*?>', '', txt)  # 移除标签
        txt = re.sub(r'^\d+:\d+:\d+.*$', '', txt, flags=re.MULTILINE)  # 移除时间轴
        txt = re.sub(r'\n+', '\n', txt).strip()  # 清理空行
        
        # 清理临时文件
        for f in sub_files:
            os.remove(f)
        
        print("✅ 字幕提取成功")
        return txt[:15000]  # 限制长度

    # 无字幕，生成音频提示
    print("⚠️ 未找到字幕，生成音频下载提示")
    audio_file = "temp_audio.mp3"
    cmd = [
        "yt-dlp",
        "-f", "bestaudio", "--extract-audio",
        "--audio-format", "mp3", "-o", audio_file, url
    ]
    if PROXY:
        cmd.insert(1, "--proxy")
        cmd.insert(2, PROXY)
    
    try:
        subprocess.run(cmd, check=True)
        return f"该B站视频无字幕，已下载音频文件（{audio_file}），请结合音频内容整理笔记。视频链接：{url}"
    except:
        return f"该B站视频无字幕，视频链接：{url}，请根据视频内容整理学习笔记。"

# ==================== 3. 调用豆包API生成笔记 ====================
def generate_note_with_doubao(content, url):
    """调用豆包API生成Obsidian结构化笔记"""
    # 获取令牌
    token = get_doubao_token()
    
    # 构造请求
    url_api = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 提示词（适配Obsidian）
    messages = [
        {
            "role": "system",
            "content": "你是专业的学习笔记整理助手，擅长将B站视频内容整理成Obsidian结构化笔记，输出标准Markdown格式，内容简洁、逻辑清晰、适合复习。"
        },
        {
            "role": "user",
            "content": f"""
请严格按照以下要求整理内容：
1. 输出格式：标准Markdown，无多余内容
2. 内容结构：
   - 核心主旨（1句话概括视频核心）
   - 核心要点（分点列出，5-8条）
   - 关键概念（术语+简要解释）
   - 重点结论/金句
   - 可执行行动项（如有）
3. 自动添加标签：[B站, 学习笔记]
4. 语言：中文，简洁专业

视频内容：
{content}

视频链接：{url}
"""
        }
    ]
    
    data = {
        "model": "doubao-pro",  # 免费可用的豆包模型
        "messages": messages,
        "temperature": 0.3,     # 低随机性，保证笔记稳定
        "max_tokens": 2000      # 足够生成完整笔记
    }
    
    print("🤖 正在调用豆包API生成笔记...")
    try:
        response = requests.post(url_api, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        note_content = result["choices"][0]["message"]["content"]
        print("✅ 笔记生成成功")
        return note_content
    except Exception as e:
        raise Exception(f"❌ 笔记生成失败：{e}")

# ==================== 4. 保存到Obsidian ====================
def save_to_obsidian(content, url):
    """将笔记保存到Obsidian库"""
    # 获取视频标题作为文件名
    cmd = ["yt-dlp", "--get-title", url]
    if PROXY:
        cmd.insert(1, "--proxy")
        cmd.insert(2, PROXY)
    
    title_result = subprocess.run(cmd, capture_output=True, text=True)
    video_title = title_result.stdout.strip() if title_result.returncode == 0 else "B站学习笔记"
    # 清理非法文件名字符
    safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
    # 生成文件名
    filename = f"{safe_title}_{time.strftime('%Y%m%d_%H%M%S')}.md"
    save_path = os.path.join(OBSIDIAN_FOLDER, filename)
    
    # 写入文件
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"📝 笔记已保存到Obsidian：")
    print(f"   {save_path}")

# ==================== 主程序 ====================
if __name__ == "__main__":
    try:
        # 1. 输入B站链接
        bili_url = input("🔗 请输入B站视频链接：").strip()
        if not bili_url or "bilibili" not in bili_url:
            print("❌ 请输入有效的B站视频链接！")
            exit(1)
        
        # 2. 提取视频内容
        bili_content = get_bilibili_content(bili_url)
        
        # 3. 调用豆包API生成笔记
        note_content = generate_note_with_doubao(bili_content, bili_url)
        
        # 4. 保存到Obsidian
        save_to_obsidian(note_content, bili_url)
        
        # 5. 清理临时文件
        if os.path.exists("temp_audio.mp3"):
            os.remove("temp_audio.mp3")
        
        print("\n🎉 全流程完成！打开Obsidian即可查看整理好的笔记。")
    
    except Exception as e:
        print(f"\n❌ 程序运行出错：{str(e)}")
        # 清理临时文件
        if os.path.exists("temp_audio.mp3"):
            os.remove("temp_audio.mp3")
        for f in os.listdir():
            if f.startswith("temp_sub"):
                os.remove(f)
