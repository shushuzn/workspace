import json
from datetime import datetime

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

d['tools']['workflow-cache'] = {
    'name': 'Workflow Cache',
    'description': '工作流缓存系统 - TTL、命中率、自动清理',
    'file': 'workflow_cache.py',
    'category': 'workflow',
    'parameters': ['--get', '--set', '--clear', '--stats'],
    'examples': ['py workflow_cache.py --stats'],
    'added_at': datetime.now().isoformat(),
    'status': 'active'
}

d['version'] = '1.6.2'

with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print('✅ 已注册 workflow-cache')
