import subprocess
import json

result = subprocess.run(
    ['py', '30-scripts-tools/issue_scanner.py', '--path', '30-scripts-tools', '--level', 'critical', '--json'],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

data = json.loads(result.stdout)
blocking_issues = [i for i in data['issues'] if i['category'] in ['security', 'unsafe_call']]
print(f"Blocking issues: {len(blocking_issues)}")
for issue in blocking_issues[:10]:
    print(f"  - {issue['category']}: {issue['file']}:{issue['line']} - {issue['message']}")
