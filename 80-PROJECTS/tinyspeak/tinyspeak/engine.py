"""
TTS Engine - Edge TTS wrapper with local cache
"""
import asyncio
import aiofiles
import sys
import os
from pathlib import Path
from typing import Optional, List, Union
import edge_tts
from dataclasses import dataclass, asdict

# Windows 兼容模式: 使用 SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class Voice:
    """Voice metadata"""
    name: str
    short_name: str
    gender: str
    locale: str


@dataclass
class VoicePreset:
    """Voice preset configuration"""
    name: str
    voice: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"


class TTSEngine:
    """Edge TTS Engine with local caching"""

    VOICES_URL = "https://speech.platform.bing.com/common/speech/synthesizer/voices/databatch"

    # Common voices for quick access
    COMMON_VOICES = {
        "en-us": ["en-US-AriaNeural", "en-US-GuyNeural", "en-US-JennyNeural"],
        "zh-cn": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-YunyangNeural"],
        "ja-jp": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
        "ko-kr": ["ko-KR-SunHiNeural", "ko-KR-InJoonNeural"],
    }

    # Built-in presets
    DEFAULT_PRESETS = {
        "fast": VoicePreset(name="fast", voice="zh-CN-XiaoxiaoNeural", rate="+50%", pitch="+0Hz", volume="+0%"),
        "slow": VoicePreset(name="slow", voice="zh-CN-XiaoxiaoNeural", rate="-50%", pitch="+0Hz", volume="+0%"),
        "news": VoicePreset(name="news", voice="zh-CN-YunyangNeural", rate="+10%", pitch="+0Hz", volume="+0%"),
        "happy": VoicePreset(name="happy", voice="zh-CN-XiaoxiaoNeural", rate="+10%", pitch="+20Hz", volume="+10%"),
        "sad": VoicePreset(name="sad", voice="zh-CN-XiaoxiaoNeural", rate="-10%", pitch="-20Hz", volume="-10%"),
    }

    def __init__(self, cache_dir: str = ".tinyspeak_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self._voices_cache = None
        self.custom_presets = {}

    async def list_voices(self, locale: Optional[str] = None) -> List[Voice]:
        """List available voices"""
        if self._voices_cache is not None:
            voices = self._voices_cache
        else:
            voices = await edge_tts.list_voices()
            self._voices_cache = voices

        result = []
        for v in voices:
            if locale and not v["Locale"].startswith(locale):
                continue
            result.append(Voice(
                name=v["Name"],
                short_name=v["ShortName"],
                gender=v["Gender"],
                locale=v["Locale"]
            ))
        return result

    async def synthesize(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        output_file: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        ssml: bool = False
    ) -> str:
        """
        Synthesize text to speech
        
        Args:
            text: Text to synthesize
            voice: Voice name (default: zh-CN-XiaoxiaoNeural)
            output_file: Output file path (auto-generated if None)
            rate: Speaking rate (e.g., "+10%", "-20%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
            volume: Volume adjustment (e.g., "+10%", "-20%")
            ssml: Treat text as SSML markup
            
        Returns:
            Path to generated audio file
        """
        if not output_file:
            # Auto-generate filename
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_file = f"tts_{text_hash}.mp3"

        output_path = self.cache_dir / output_file

        # Edge TTS communicate
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )

        await communicate.save(str(output_path))

        return str(output_path)

    async def synthesize_ssml(
        self,
        ssml_text: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Synthesize SSML to speech with full control
        
        SSML Example:
        <speak>
            <voice name="zh-CN-XiaoxiaoNeural">
                <prosody rate="+10%" pitch="+5Hz">
                    你好，这是一个测试。
                </prosody>
            </voice>
            <voice name="en-US-AriaNeural">
                Hello, this is a test.
            </voice>
        </speak>
        """
        if not output_file:
            import hashlib
            text_hash = hashlib.md5(ssml_text.encode()).hexdigest()[:8]
            output_file = f"tts_ssml_{text_hash}.mp3"

        output_path = self.cache_dir / output_file

        # For SSML, use submaker to avoid voice validation
        communicate = edge_tts.Communicate(ssml_text)
        await communicate.save(str(output_path))

        return str(output_path)

    async def synthesize_multi_voice(
        self,
        segments: List[dict],
        output_file: Optional[str] = None
    ) -> str:
        """
        Synthesize text with multiple voices
        
        Args:
            segments: List of dicts with 'text', 'voice', 'rate', 'pitch', 'volume'
            output_file: Output file path
            
        Returns:
            Path to generated audio file
        """
        # Build SSML
        ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">\n'

        for seg in segments:
            voice = seg.get('voice', 'zh-CN-XiaoxiaoNeural')
            rate = seg.get('rate', '+0%')
            pitch = seg.get('pitch', '+0Hz')
            volume = seg.get('volume', '+0%')

            ssml += f'''    <voice name="{voice}">
        <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
            {seg['text']}
        </prosody>
    </voice>\n'''

        ssml += '</speak>'

        return await self.synthesize_ssml(ssml, output_file)

    async def synthesize_stream(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%"
    ):
        """
        Stream audio directly (for real-time playback)
        
        Yields chunks of audio data
        """
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    def synthesize_sync(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        output_file: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        ssml: bool = False
    ) -> str:
        """Synchronous version of synthesize"""
        if ssml:
            return asyncio.run(self.synthesize_ssml(text, output_file))
        return asyncio.run(self.synthesize(text, voice, output_file, rate, pitch, volume))

    # Preset management
    def save_preset(self, preset: VoicePreset):
        """Save a custom preset"""
        self.custom_presets[preset.name] = preset

    def get_preset(self, name: str) -> Optional[VoicePreset]:
        """Get a preset by name (built-in or custom)"""
        if name in self.DEFAULT_PRESETS:
            return self.DEFAULT_PRESETS[name]
        return self.custom_presets.get(name)

    def list_presets(self) -> dict:
        """List all available presets"""
        return {**self.DEFAULT_PRESETS, **self.custom_presets}


# Quick usage
if __name__ == "__main__":
    engine = TTSEngine()

    # Test basic
    audio_file = engine.synthesize_sync("你好，这是 TinySpeak 测试！")
    print(f"Generated: {audio_file}")

    # Test multi-voice
    import json
    segments = [
        {"text": "你好，我是中文语音。", "voice": "zh-CN-XiaoxiaoNeural"},
        {"text": "Hello, I am English voice.", "voice": "en-US-AriaNeural"},
    ]
    multi_file = engine.synthesize_sync("")
    print(f"Multi-voice: Use synthesize_multi_voice()")