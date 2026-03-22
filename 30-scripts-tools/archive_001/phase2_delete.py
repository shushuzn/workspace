#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2 删除"""

import shutil
from pathlib import Path
from datetime import datetime

archive_dir = Path('cleanup_archive/20260322')
archive_dir.mkdir(parents=True, exist_ok=True)

safe_delete = [
    'reg_auto_critic_v_001.py',
    'reg_fix_state_v_001.py',
    'reg_v_001.py',
    'smart_compress_002.py',
    'sa_backtest_optimizer_001.py',
    'sa_backtesting_001.py',
]

for f in safe_delete:
    p = Path(f)
    if p.exists():
        shutil.move(str(p), str(archive_dir / f))
        print(f'[DELETED] {f}')
    else:
        print(f'[SKIP] {f} - not found')

print(f'\nArchived to: {archive_dir}')

# 统计剩余
total = len(list(Path('.').glob('*.py')))
print(f'Total tools remaining: {total}')
