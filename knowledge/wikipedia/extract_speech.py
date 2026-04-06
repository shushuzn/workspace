# Extract speech text from video script
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\articles\AI\01-detection-of-spin-valley-polarized-states\01-Detection-of-spin-valley-polarized-states论文解读.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove frontmatter
import re
content = re.sub(r'^---\n[\s\S]+?\n---\n', '', content)

# Remove [画面：...] annotations
content = re.sub(r'\[画面：[^\]]+\]\n?', '', content)

# Replace math symbols for TTS
replacements = [
    ('σ', 'sigma'),
    ('λ', 'lambda'),
    ('₂', ' 2'),
    ('₁', ' 1'),
    ('ᵢ', ' i'),
    ('ᵢ', ' i'),
    ('NbSe', 'NbSe'),
    ('MoS', 'MoS'),
    ('Andreev', 'Andreev'),
    ('Ising', 'Ising'),
    ('TMDC', 'TMDC'),
    ('IAM', 'IAM'),
    ('Burau', 'Burau'),
]

for old, new in replacements:
    content = content.replace(old, new)

# Write speech text
speech_file = r'D:\OpenClaw\workspace\knowledge\wikipedia\articles\AI\01-detection-of-spin-valley-polarized-states\01-Detection-of-spin-valley-polarized-states论文解读-speech.txt'
with open(speech_file, 'w', encoding='utf-8') as f:
    f.write(content.strip())

print(f"Written: {len(content)} chars")

# Also create the version for TTS (same as speech for now)
tts_file = speech_file.replace('-speech.txt', '-speech-tts.txt')
with open(tts_file, 'w', encoding='utf-8') as f:
    f.write(content.strip())
print(f"Written TTS: {tts_file}")
