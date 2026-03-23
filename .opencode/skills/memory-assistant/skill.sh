#!/bin/bash
cd "$(dirname "$0")/../../ai_memory_system" && python3 -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')
from agent_tool import MemoryAgentTool
import json

tool = MemoryAgentTool()
action = sys.argv[1] if len(sys.argv) > 1 else 'status'
params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

result = tool.run(action, **params)
print(result)
" "$@"
