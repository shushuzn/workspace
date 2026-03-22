#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 3 - 删除无用 reg_ 文件"""

import shutil
from pathlib import Path

archive = Path('cleanup_archive/20260322')

orphan = [
    'reg_guardian_fix_001.py', 
    'reg_task_analyzer_001.py'
]

for f in orphan:
    p = Path(f)
    if p.exists():
        shutil.move(str(p), str(archive / f))
        print(f'[DELETED] {f}')
    else:
        print(f'[SKIP] {f}')

total = len(list(Path('.').glob('*.py')))
print(f'\nTotal remaining: {total}')
