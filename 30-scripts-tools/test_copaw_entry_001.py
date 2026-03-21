import logging
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, '30-scripts-tools')

from copaw_entry import CopawEntry

print("创建 CopawEntry 实例...")
e = CopawEntry("测试会话")
print(f"Session ID: {e.session_id}")
print(f"Flow ID: {e.flow_id}")
print(f"State file: {e.state_file}")

print("\n初始化状态...")
state = e.initialize_state()
print(f"状态：{state.get('status')}")

print("\n验证上下文...")
result = e.verify_context()
print(f"验证结果：{result}")
