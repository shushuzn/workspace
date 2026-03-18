#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update remediation log for P1 fix completion"""

import json
import sys
import codecs
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 读取整改台账
with open('30-scripts-tools/remediation_log.json', 'r', encoding='utf-8') as f:
    log = json.load(f)

# 查找并更新 P1 相关任务
p1_tasks = []
for task_id, task in log['tasks'].items():
    title = task.get('title', '').lower()
    if 'os.system' in title or 'eval' in title or 'exec' in title or 'p1' in title:
        p1_tasks.append(task_id)
        task['status'] = 'resolved'
        task['linked_commit'] = 'd38759f'
        task['notes'].append(f"Resolved via workflow - P1 Issue Fixer tool - {datetime.now().isoformat()}")

print(f"Updated {len(p1_tasks)} P1 tasks to 'resolved':")
for tid in p1_tasks:
    print(f"  - {tid}")

# 更新日志
log['last_updated'] = datetime.now().isoformat()

with open('30-scripts-tools/remediation_log.json', 'w', encoding='utf-8') as f:
    json.dump(log, f, indent=2, ensure_ascii=False)

print("\nOK: Remediation log updated")
