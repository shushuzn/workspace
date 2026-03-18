import py_compile
import sys

filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

try:
    py_compile.compile(filePath, doraise=True)
    print("SUCCESS: File compiles correctly!")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
