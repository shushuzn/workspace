import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ai_memory = Path(__file__).parent.parent.parent.parent / "ai_memory_system"
sys.path.insert(0, str(ai_memory))

from ai_memory_system.agent_tool import MemoryAgentTool
import json

tool = MemoryAgentTool()
action = sys.argv[1] if len(sys.argv) > 1 else "status"
params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

result = tool.run(action, **params)
print(result)
