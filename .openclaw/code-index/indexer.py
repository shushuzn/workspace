#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""代码索引和搜索工具"""
import os, json, re, sys
from pathlib import Path

WORKSPACE = Path(r"D:\OpenClaw\workspace")
INDEX_FILE = WORKSPACE / ".openclaw" / "code-index" / "index.json"
EXT = ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json']
IGNORE = ['node_modules', '.git', '__pycache__', 'venv', '80-PROJECTS', '.copaw']

def index():
    data = {"files": [], "functions": [], "classes": [], "updated": ""}
    for f in WORKSPACE.rglob('*'):
        if f.is_file() and f.suffix in EXT and not any(i in str(f) for i in IGNORE):
            try:
                rel = str(f.relative_to(WORKSPACE))
                data["files"].append(rel)
                with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                    c = fp.read()
                # 函数
                for m in re.findall(r'(?:def|function)\s+(\w+)', c):
                    if not m.startswith('_'):
                        data["functions"].append({"name": m, "file": rel})
                # 类
                for m in re.findall(r'class\s+(\w+)', c):
                    data["classes"].append({"name": m, "file": rel})
            except: pass
    from datetime import datetime
    data["updated"] = datetime.now().isoformat()
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(data['files'])} files, {len(data['functions'])} functions, {len(data['classes'])} classes")

def search(q):
    if not INDEX_FILE.exists():
        print("[INFO] No index, run: py indexer.py")
        return
    with open(INDEX_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
    q = q.lower()
    for func in data["functions"]:
        if q in func["name"].lower():
            print(f"  [func] {func['name']} @ {func['file']}")
    for cls in data["classes"]:
        if q in cls["name"].lower():
            print(f"  [class] {cls['name']} @ {cls['file']}")
    for f in data["files"]:
        if q in f.lower():
            print(f"  [file] {f}")

if __name__ == "__main__":
    if len(sys.argv) > 1: search(sys.argv[1])
    else: index()
