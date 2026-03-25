"""
TinySpeak Web UI - Browser-based TTS Player
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path


# HTML Template
WEB_UI_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinySpeak - Web TTS Player</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            width: 100%;
            max-width: 600px;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        
        h1 span {
            color: #667eea;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        
        textarea, select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        textarea:focus, select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
        }
        
        .slider-group {
            display: flex;
            flex-direction: column;
        }
        
        .slider-group input[type="range"] {
            padding: 0;
            border: none;
        }
        
        .slider-value {
            text-align: center;
            font-size: 14px;
            color: #888;
            margin-top: 5px;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
            display: none;
        }
        
        .result.show {
            display: block;
        }
        
        .result audio {
            width: 100%;
            margin-top: 15px;
        }
        
        .status {
            text-align: center;
            margin-top: 10px;
            color: #666;
        }
        
        .voices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            max-height: 200px;
            overflow-y: auto;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin-top: 10px;
        }
        
        .voice-item {
            padding: 8px 12px;
            background: #f5f5f5;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 14px;
        }
        
        .voice-item:hover {
            background: #667eea;
            color: white;
        }
        
        .voice-item.selected {
            background: #667eea;
            color: white;
        }
        
        .preset-btns {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        
        .preset-btn {
            padding: 8px 16px;
            background: #f0f0f0;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .preset-btn:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔊 TinySpeak <span>Web</span></h1>
        
        <div class="form-group">
            <label>输入文字</label>
            <textarea id="text" placeholder="在这里输入要转换的文字...">你好，欢迎使用 TinySpeak！</textarea>
        </div>
        
        <div class="form-group">
            <label>选择语音</label>
            <select id="voice">
                <option value="zh-CN-XiaoxiaoNeural">中文 - 晓晓 (女声)</option>
                <option value="zh-CN-YunxiNeural">中文 - 云希 (男声)</option>
                <option value="zh-CN-YunyangNeural">中文 - 云扬 (新闻)</option>
                <option value="en-US-AriaNeural">English - Aria (Female)</option>
                <option value="en-US-GuyNeural">English - Guy (Male)</option>
                <option value="en-US-JennyNeural">English - Jenny</option>
                <option value="ja-JP-NanamiNeural">日本語 - ななみ</option>
                <option value="ko-KR-SunHiNeural">한국어 - 선희</option>
            </select>
        </div>
        
        <div class="form-group">
            <label>预设</label>
            <div class="preset-btns">
                <button class="preset-btn" onclick="setPreset('fast')">快速</button>
                <button class="preset-btn" onclick="setPreset('slow')">慢速</button>
                <button class="preset-btn" onclick="setPreset('news')">新闻</button>
                <button class="preset-btn" onclick="setPreset('happy')">开心</button>
                <button class="preset-btn" onclick="setPreset('sad')">悲伤</button>
            </div>
        </div>
        
        <div class="form-group">
            <label>参数调节</label>
            <div class="controls">
                <div class="slider-group">
                    <input type="range" id="rate" min="-50" max="50" value="0">
                    <span class="slider-value">语速: <span id="rateValue">0%</span></span>
                </div>
                <div class="slider-group">
                    <input type="range" id="pitch" min="-20" max="20" value="0">
                    <span class="slider-value">音调: <span id="pitchValue">0Hz</span></span>
                </div>
                <div class="slider-group">
                    <input type="range" id="volume" min="-50" max="50" value="0">
                    <span class="slider-value">音量: <span id="volumeValue">0%</span></span>
                </div>
            </div>
        </div>
        
        <button class="btn" id="speakBtn" onclick="speak()">🔊 生成语音</button>
        
        <div class="status" id="status"></div>
        
        <div class="result" id="result">
            <strong>✅ 语音已生成！</strong>
            <audio id="audioPlayer" controls>
                您的浏览器不支持 audio 元素。
            </audio>
            <p style="margin-top: 10px; font-size: 14px; color: #666;" id="fileInfo"></p>
        </div>
    </div>
    
    <script>
        // Update slider values
        document.getElementById('rate').oninput = function() {
            document.getElementById('rateValue').textContent = (this.value >= 0 ? '+' : '') + this.value + '%';
        };
        document.getElementById('pitch').oninput = function() {
            document.getElementById('pitchValue').textContent = (this.value >= 0 ? '+' : '') + this.value + 'Hz';
        };
        document.getElementById('volume').oninput = function() {
            document.getElementById('volumeValue').textContent = (this.value >= 0 ? '+' : '') + this.value + '%';
        };
        
        function setPreset(name) {
            const presets = {
                fast: { rate: 50, pitch: 0, volume: 0 },
                slow: { rate: -50, pitch: 0, volume: 0 },
                news: { rate: 10, pitch: 0, volume: 0 },
                happy: { rate: 10, pitch: 20, volume: 10 },
                sad: { rate: -10, pitch: -20, volume: -10 }
            };
            
            const p = presets[name];
            document.getElementById('rate').value = p.rate;
            document.getElementById('pitch').value = p.pitch;
            document.getElementById('volume').value = p.volume;
            
            document.getElementById('rateValue').textContent = (p.rate >= 0 ? '+' : '') + p.rate + '%';
            document.getElementById('pitchValue').textContent = (p.pitch >= 0 ? '+' : '') + p.pitch + 'Hz';
            document.getElementById('volumeValue').textContent = (p.volume >= 0 ? '+' : '') + p.volume + '%';
        }
        
        async function speak() {
            const text = document.getElementById('text').value;
            const voice = document.getElementById('voice').value;
            const rate = document.getElementById('rate').value + '%';
            const pitch = document.getElementById('pitch').value + 'Hz';
            const volume = document.getElementById('volume').value + '%';
            
            const btn = document.getElementById('speakBtn');
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            const audioPlayer = document.getElementById('audioPlayer');
            const fileInfo = document.getElementById('fileInfo');
            
            if (!text.trim()) {
                alert('请输入文字');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = '⏳ 生成中...';
            status.textContent = '正在生成语音...';
            result.classList.remove('show');
            
            try {
                const response = await fetch('/speak', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice, rate, pitch, volume })
                });
                
                const data = await response.json();
                
                // Use stream endpoint for direct playback
                const streamResponse = await fetch('/speak/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice, rate, pitch, volume })
                });
                
                const blob = await streamResponse.blob();
                const url = URL.createObjectURL(blob);
                
                audioPlayer.src = url;
                await audioPlayer.play();
                
                fileInfo.textContent = `语音: ${voice} | 语速: ${rate} | 音调: ${pitch} | 音量: ${volume}`;
                result.classList.add('show');
                status.textContent = '';
                
            } catch (error) {
                status.textContent = '❌ 错误: ' + error.message;
                console.error(error);
            }
            
            btn.disabled = false;
            btn.textContent = '🔊 生成语音';
        }
    </script>
</body>
</html>
"""


def create_web_app() -> FastAPI:
    """Create FastAPI app with Web UI"""
    app = FastAPI(title="TinySpeak Web UI")

    @app.get("/", response_class=HTMLResponse)
    async def home():
        return WEB_UI_HTML

    return app


# Standalone runner
if __name__ == "__main__":
    import uvicorn
    from tinyspeak.api import app as tts_app

    # Create combined app
    combined_app = FastAPI()

    @combined_app.get("/")
    async def home():
        return HTMLResponse(WEB_UI_HTML)

    # Mount TTS routes
    from fastapi import APIRouter
    router = APIRouter()

    # Copy routes from TTS app
    # (simplified - just run separate servers for now)

    print("Starting TinySpeak Web UI...")
    print("Open http://localhost:8080 in your browser")

    uvicorn.run(combined_app, host="0.0.0.0", port=8080)