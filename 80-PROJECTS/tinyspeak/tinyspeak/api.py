"""
TinySpeak API - REST API Server with Streaming Support
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json
from tinyspeak import TTSEngine
from tinyspeak.converter import AudioConverter


app = FastAPI(
    title="TinySpeak API",
    description="Lightweight Local-First TTS Tool - Now with Streaming!",
    version="0.2.0"
)

engine = TTSEngine()


# ============== Web UI ==============

WEB_UI_HTML = """<!DOCTYPE html>
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
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        h1 span { color: #667eea; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        textarea, select, input { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 16px; }
        textarea:focus, select:focus, input:focus { outline: none; border-color: #667eea; }
        textarea { min-height: 120px; resize: vertical; }
        .controls { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
        .slider-group { display: flex; flex-direction: column; }
        .slider-group input[type="range"] { padding: 0; border: none; }
        .slider-value { text-align: center; font-size: 14px; color: #888; margin-top: 5px; }
        .btn {
            width: 100%; padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 10px;
            font-size: 18px; font-weight: 600; cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s; margin-top: 10px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .result { margin-top: 20px; padding: 20px; background: #f5f5f5; border-radius: 10px; display: none; }
        .result.show { display: block; }
        .result audio { width: 100%; margin-top: 15px; }
        .status { text-align: center; margin-top: 10px; color: #666; }
        .preset-btns { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; }
        .preset-btn { padding: 8px 16px; background: #f0f0f0; border: none; border-radius: 20px; cursor: pointer; font-size: 14px; }
        .preset-btn:hover { background: #667eea; color: white; }
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
                <option value="en-US-AriaNeural">English - Aria</option>
                <option value="en-US-GuyNeural">English - Guy</option>
                <option value="ja-JP-NanamiNeural">日本語</option>
                <option value="ko-KR-SunHiNeural">한국어</option>
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
            <audio id="audioPlayer" controls></audio>
        </div>
    </div>
    <script>
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
            const presets = { fast: {rate:50,pitch:0,volume:0}, slow: {rate:-50,pitch:0,volume:0}, news: {rate:10,pitch:0,volume:0}, happy: {rate:10,pitch:20,volume:10}, sad: {rate:-10,pitch:-20,volume:-10} };
            const p = presets[name];
            document.getElementById('rate').value = p.rate;
            document.getElementById('pitch').value = p.pitch;
            document.getElementById('volume').value = p.volume;
            document.getElementById('rateValue').textContent = (p.rate>=0?'+':'') + p.rate + '%';
            document.getElementById('pitchValue').textContent = (p.pitch>=0?'+':'') + p.pitch + 'Hz';
            document.getElementById('volumeValue').textContent = (p.volume>=0?'+':'') + p.volume + '%';
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
            if (!text.trim()) { alert('请输入文字'); return; }
            btn.disabled = true; btn.textContent = '⏳ 生成中...';
            status.textContent = '正在生成语音...'; result.classList.remove('show');
            try {
                const streamResponse = await fetch('/speak/stream', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, voice, rate, pitch, volume })
                });
                const blob = await streamResponse.blob();
                audioPlayer.src = URL.createObjectURL(blob);
                await audioPlayer.play();
                result.classList.add('show'); status.textContent = '';
            } catch (error) { status.textContent = '❌ 错误: ' + error.message; }
            btn.disabled = false; btn.textContent = '🔊 生成语音';
        }
    </script>
</body>
</html>"""


# ============== Request Models ==============

class TTSRequest(BaseModel):
    """TTS synthesis request"""
    text: str
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"


class SSMLRequest(BaseModel):
    """SSML synthesis request"""
    ssml: str
    output_file: Optional[str] = None


class MultiVoiceRequest(BaseModel):
    """Multi-voice synthesis request"""
    segments: List[dict]
    output_file: Optional[str] = None


class PresetRequest(BaseModel):
    """Preset configuration"""
    name: str
    voice: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"


class ConvertRequest(BaseModel):
    """Audio conversion request"""
    input_file: str
    output_file: str
    format: Optional[str] = None
    bitrate: str = "128k"
    sample_rate: Optional[int] = None


# ============== Response Models ==============

class TTSResponse(BaseModel):
    """TTS synthesis response"""
    audio_file: str
    text: str
    voice: str


class VoiceInfo(BaseModel):
    """Voice information"""
    name: str
    short_name: str
    gender: str
    locale: str


class PresetInfo(BaseModel):
    """Preset information"""
    name: str
    voice: str
    rate: str
    pitch: str
    volume: str


# ============== Routes ==============

@app.get("/")
def root():
    """Web UI or Health check"""
    accept = ""  # You might want to check request headers here
    return HTMLResponse(WEB_UI_HTML)


# ---------- TTS Endpoints ----------

@app.post("/speak", response_model=TTSResponse)
async def speak(request: TTSRequest):
    """
    Convert text to speech (standard mode)
    
    Returns audio file path
    """
    try:
        audio_file = await engine.synthesize(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            pitch=request.pitch,
            volume=request.volume
        )

        return TTSResponse(
            audio_file=audio_file,
            text=request.text,
            voice=request.voice
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak/stream")
async def speak_stream(request: TTSRequest):
    """
    Stream audio directly (for real-time playback)
    
    Returns audio stream
    """
    try:
        async def generate():
            async for chunk in engine.synthesize_stream(
                text=request.text,
                voice=request.voice,
                rate=request.rate,
                pitch=request.pitch,
                volume=request.volume
            ):
                yield chunk

        return StreamingResponse(
            generate(),
            media_type="audio/mpeg",
            headers={
                "Accept-Ranges": "bytes"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak/ssml")
async def speak_ssml(request: SSMLRequest):
    """
    Synthesize SSML markup
    
    Full SSML control over speech synthesis
    """
    try:
        audio_file = await engine.synthesize_ssml(
            ssml_text=request.ssml,
            output_file=request.output_file
        )

        return {"audio_file": audio_file, "type": "ssml"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/speak/multi-voice")
async def speak_multi_voice(request: MultiVoiceRequest):
    """
    Synthesize with multiple voices
    
    Each segment can have different voice settings
    """
    try:
        audio_file = await engine.synthesize_multi_voice(
            segments=request.segments,
            output_file=request.output_file
        )

        return {"audio_file": audio_file, "type": "multi-voice"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Voice Endpoints ----------

@app.get("/voices", response_model=List[VoiceInfo])
async def list_voices(locale: Optional[str] = None):
    """List available voices"""
    try:
        voices = await engine.list_voices(locale)
        return [
            VoiceInfo(
                name=v.name,
                short_name=v.short_name,
                gender=v.gender,
                locale=v.locale
            )
            for v in voices
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voices/common")
def common_voices():
    """Get common voice shortcuts"""
    return engine.COMMON_VOICES


# ---------- Preset Endpoints ----------

@app.get("/presets", response_model=List[PresetInfo])
def list_presets():
    """List all available presets"""
    presets = engine.list_presets()
    return [PresetInfo(**asdict(p)) for p in presets.values()]


@app.post("/presets")
def save_preset(request: PresetRequest):
    """Save a custom preset"""
    from dataclasses import asdict
    preset = PresetInfo(**asdict(request))
    engine.save_preset(preset)
    return {"status": "ok", "preset": request.name}


# ---------- Converter Endpoints ----------

@app.post("/convert")
async def convert(request: ConvertRequest):
    """Convert audio file to different format"""
    try:
        result = AudioConverter.convert(
            input_file=request.input_file,
            output_file=request.output_file,
            format=request.format,
            bitrate=request.bitrate,
            sample_rate=request.sample_rate
        )

        return {"output_file": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/info/{file_path}")
def get_info(file_path: str):
    """Get audio file information"""
    try:
        return AudioConverter.get_info(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Server ==============

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()