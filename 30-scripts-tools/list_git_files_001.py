import subprocess

result = subprocess.run(
    ["git", "ls-files", "*.py"],
    capture_output=True,
    text=True,
    encoding="utf-8"
, timeout=60)

files = result.stdout.strip().split("\n")
critic_files = [f for f in files if "critic" in f.lower()]

print(f"Git 跟踪的 Python 文件总数：{len(files)}")
print(f"Critic 相关文件：{len(critic_files)}")
print("\nCritic 文件列表:")
for f in critic_files[:20]:
    print(f"  - {f}")
