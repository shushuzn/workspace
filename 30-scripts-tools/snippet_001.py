#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SNIPPET-001 Code Snippet Library
"""

import json, sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SNIPPETS = {
    "header": '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{NAME}
"""

import json, sys
from pathlib import Path
from typing import Dict, List

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
''',

    "safe_arg": '''
    def _arg(self, idx, default=None):
        return sys.argv[idx] if len(sys.argv) > idx else default
''',

    "safe_json": '''
    def _load(self, path):
        return json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))
    
    def _save(self, path, data):
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
''',

    "cli_main": '''
def main():
    if len(sys.argv) < 2:
        print("Usage: py {FILE} <command>")
        return 1
    cmd = sys.argv[1]
    # Add commands
    print(f"Unknown: {cmd}")
    return 1

if __name__ == "__main__": sys.exit(main())
'''
}

def list_snippets():
    for name in SNIPPETS:
        print(f"  {name}")

def get_snippet(name):
    if name in SNIPPETS:
        return SNIPPETS[name]
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_snippets()
        elif sys.argv[1] == "--get":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            if name:
                s = get_snippet(name)
                print(s if s else f"Not found: {name}")
        else:
            print("Usage: py snippet_001.py --list | --get <name>")
    else:
        list_snippets()
