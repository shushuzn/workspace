#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OpenClaw 编程能力全增强包"""

import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(r"D:\OpenClaw\workspace")

def main():
    print("=" * 50)
    print("Installing All Programming Enhancements")
    print("=" * 50)

    # 1. 代码片段库
    print("\n[1/6] Creating snippet library...")
    snippets_dir = WORKSPACE / ".openclaw" / "snippets"
    snippets_dir.mkdir(parents=True, exist_ok=True)

    snippets = {
        "python": {
            "function": "def {name}({params}):\n    \"\"\"\"\"\"\n    pass",
            "class": "class {ClassName}:\n    def __init__(self):\n        pass",
        },
        "javascript": {
            "function": "function {name}({params}) {{\n    \n}}",
            "arrow": "const {name} = ({params}) => {{\n    \n}};",
            "class": "class {ClassName} {{\n    constructor() {{\n    }}\n}}",
        }
    }

    with open(snippets_dir / "library.json", 'w', encoding='utf-8') as f:
        json.dump(snippets, f, ensure_ascii=False, indent=2)
    print("  [OK] Snippets library created")

    # 2. 代码索引器
    print("\n[2/6] Creating code indexer...")
    index_dir = WORKSPACE / ".openclaw" / "code-index"
    index_dir.mkdir(parents=True, exist_ok=True)

    indexer = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""代码索引和搜索工具"""
import os, json, re, sys
from pathlib import Path

WORKSPACE = Path(r"D:\\OpenClaw\\workspace")
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
            except Exception: pass
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
    with open(INDEX_FILE) as f: data = json.load(f)
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
'''

    with open(index_dir / "indexer.py", 'w', encoding='utf-8') as f:
        f.write(indexer)
    print("  [OK] Code indexer created")

    # 3. 语法检查配置
    print("\n[3/6] Creating linter configs...")
    linter_dir = WORKSPACE / ".openclaw" / "linters"
    linter_dir.mkdir(parents=True, exist_ok=True)

    configs = {
        "eslintrc.json": {"env": {"browser": True, "es2021": True}, "extends": "eslint:recommended", "rules": {"no-unused-vars": "warn"}},
        "pylintrc": "[MASTER]\ndisable=C0111,R0903\nmax-line-length=120",
    }

    for name, content in configs.items():
        with open(linter_dir / name, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2) if name.endswith('.json') else f.write(content)
    print("  [OK] Linter configs created")

    # 4. 项目模板
    print("\n[4/6] Creating project templates...")
    templates_dir = WORKSPACE / ".openclaw" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    templates = {
        "python-project": {
            "description": "Python 项目",
            "main.py": "def main():\n    pass\n\nif __name__ == '__main__':\n    main()",
        },
        "javascript-module": {
            "description": "JavaScript 模块",
            "index.js": "export function main() {}\n",
        },
        "html-site": {
            "description": "HTML 网站",
            "index.html": "<!DOCTYPE html>\n<html>\n<head><meta charset='UTF-8'><title></title></head>\n<body>\n</body>\n</html>",
        }
    }

    with open(templates_dir / "library.json", 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    print("  [OK] Project templates created")

    # 5. Git 增强
    print("\n[5/6] Creating Git enhancements...")
    git_dir = WORKSPACE / ".openclaw" / "git"
    git_dir.mkdir(parents=True, exist_ok=True)

    with open(git_dir / "commit-msg.py", 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/env python\nimport subprocess\nmsg = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True).stdout\nprint(f"feat: Updated {len(msg.split(chr(10)))-2} files")\n')
    print("  [OK] Git enhancements created")

    # 6. 更新 OpenClaw 配置
    print("\n[6/6] Updating OpenClaw config...")
    config_file = Path.home() / ".copaw" / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config["programming"] = {
            "snippets_dir": str(snippets_dir),
            "index_dir": str(index_dir),
            "templates_dir": str(templates_dir),
            "auto_index": True,
            "auto_lint": True,
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    print("  [OK] Config updated")

    print("\n" + "=" * 50)
    print("All Enhancements Installed!")
    print("=" * 50)
    print("\nTools:")
    print("  py .openclaw/code-index/indexer.py    - 索引项目")
    print("  py .openclaw/code-index/indexer.py <query>  - 搜索代码")
    print("\nSnippets: .openclaw/snippets/library.json")
    print("Templates: .openclaw/templates/library.json")
    print("\nRestart OpenClaw to apply changes.")

if __name__ == "__main__":
    main()
