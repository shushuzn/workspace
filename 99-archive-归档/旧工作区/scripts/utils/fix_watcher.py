import re

path = r"D:\scripts\medium_watcher_event.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_log = r'def log\(msg\):.*?open\(LOG_PATH, "a", encoding="utf-8"\)\.write\(line \+ "\\n"\)\n'
new_log = '''def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        print(line, flush=True)
    except Exception:
        pass
    open(LOG_PATH, "a", encoding="utf-8").write(line + "\\n")
'''

content = re.sub(old_log, new_log, content, flags=re.S)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed!")
