"""Fix wiki.mjs by rebuilding from scratch with all commands intact."""
import re, os

os.chdir(r'D:\OpenClaw\workspace\knowledge\wikipedia')

# Read current broken file to extract generateSceneCode
with open('wiki.mjs', 'r', encoding='utf-8') as f:
    current = f.read()

# Extract generateSceneCode if present
gen_scene_match = re.search(r'(function generateSceneCode[^{]+{[^}]+(?:{[^}]+}[^}]+)*})', current, re.DOTALL)
gen_scene_code = gen_scene_match.group(1) if gen_scene_match else None
print(f"Extracted generateSceneCode: {'YES' if gen_scene_code else 'NO'}")

# Find the end of the current content - where does it break?
lines = current.splitlines()
print("\nLast 20 lines:")
for i, l in enumerate(lines[-20:], len(lines)-19):
    print(f"{i}: {l[:80]}")
