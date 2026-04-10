from faster_whisper import WhisperModel
import sys

print("Downloading/loading tiny model...")
model = WhisperModel("tiny", compute_type="int8")
print("Model loaded!")

# transcribe the audio file we already downloaded
audio_path = "D:/OpenClaw/workspace/bilibili_audio.m4s"
print(f"Transcribing: {audio_path}")
segments, info = model.transcribe(audio_path, language="zh", beam_size=5)
print(f"Language: {info.language}, duration: {info.duration:.1f}s")
print("Segments:")
for seg in segments:
    print(f"[{seg.start:.1f}s-{seg.end:.1f}s] {seg.text}")
