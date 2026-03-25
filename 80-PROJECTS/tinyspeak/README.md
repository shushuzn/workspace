# TinySpeak

**Lightweight Local-First TTS Tool** — 隐私优先、离线运行的文字转语音工具。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.1.0-orange)

---

## ✨ 特性

| 特性 | 描述 |
|-----|------|
| 🔒 **隐私优先** | 所有处理在本地完成，不上传数据 |
| 🚀 **轻量快速** | 基于 Edge TTS，无需 GPU |
| 🎵 **多语言支持** | 140+ 语音，中英日韩等 |
| 🔧 **多种接口** | CLI / API / Python 模块 |
| ⚡ **批量处理** | 支持文本文件批量转换 |

---

## 📦 安装

```bash
# Clone or download
cd tinyspeak

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

---

## 🎮 快速开始

### Web UI (推荐)

```bash
# 启动 Web 服务器
python -m tinyspeak.api
```

然后打开浏览器访问：**http://localhost:8000**

可以直接在网页上输入文字、选择语音、调节参数，点击生成即可播放！

---

### CLI 用法

```bash
# 基本用法
python -m tinyspeak.cli speak "你好，世界！"

# 指定语音
python -m tinyspeak.cli speak "Hello!" -v en-US-AriaNeural

# 调整语速/音调
python -m tinyspeak.cli speak "Hello!" -r "+10%" -p "+5Hz"

# 列出可用语音
python -m tinyspeak.cli voices
python -m tinyspeak.cli voices -l zh-CN  # 中文语音

# 批量转换
python -m tinyspeak.cli batch input.txt -o output/
```

### API 用法

```bash
# 启动 API 服务器
python -m tinyspeak.api

# 或指定端口
python -m tinyspeak.api --port 8080
```

```bash
# API 调用示例
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "你好！", "voice": "zh-CN-XiaoxiaoNeural"}'
```

### Python 模块

```python
from tinyspeak import TTSEngine

engine = TTSEngine()

# 生成语音
audio_file = engine.synthesize_sync(
    text="你好，这是 TinySpeak！",
    voice="zh-CN-XiaoxiaoNeural",
    rate="+0%",
    pitch="+0Hz"
)

print(f"Generated: {audio_file}")
```

---

## 🎤 推荐语音

### 中文

| Voice | 风格 |
|-------|------|
| `zh-CN-XiaoxiaoNeural` | 标准女声 |
| `zh-CN-YunxiNeural` | 年轻男声 |
| `zh-CN-YunyangNeural` | 新闻男声 |

### English

| Voice | 风格 |
|-------|------|
| `en-US-AriaNeural` | 标准女声 |
| `en-US-GuyNeural` | 标准男声 |
| `en-US-JennyNeural` | 友好女声 |

### 全部语音

```bash
# 查看所有语音
tinyspeak voices

# 按语言筛选
tinyspeak voices -l ja-JP  # 日语
tinyspeak voices -l ko-KR  # 韩语
```

---

## 📁 项目结构

```
tinyspeak/
├── README.md              # 本文件
├── requirements.txt       # 依赖
├── pyproject.toml         # 项目配置
├── tinyspeak/
│   ├── __init__.py        # 包入口
│   ├── engine.py          # TTS 引擎
│   ├── cli.py             # 命令行工具
│   └── api.py             # REST API
└── tests/                 # 测试目录
```

---

## 🔧 配置

### 环境变量

在 `.env` 文件中设置：

```bash
# 缓存目录
TTS_CACHE_DIR=.tinyspeak_cache

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 📝 License

MIT License — 自由使用，保留作者信息。

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

**Made with ❤️ by OpenClaw**