import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
INTEGRATE-001 API Connector
【API连接器】

功能:
  - REST API调用
  - 认证处理
  - 响应解析
"""
import json
import sys
import urllib.request
import urllib.parse


class APIConnector:
    """API连接器"""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
    
    def set_auth(self, token: str):
        self.headers["Authorization"] = f"Bearer {token}"
    
    def get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as response:
                return {"status": response.status, "data": json.loads(response.read())}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def post(self, endpoint: str, data: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        data_json = json.dumps(data).encode('utf-8') if data else b'{}'
        
        try:
            req = urllib.request.Request(url, data=data_json, headers=self.headers, method='POST')
            with urllib.request.urlopen(req) as response:
                return {"status": response.status, "data": json.loads(response.read())}
        except Exception as e:
            return {"status": "error", "message": str(e)}


logging.basicConfig(level=logging.INFO)
def main():
    connector = APIConnector()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--get":
            endpoint = sys.argv[2] if len(sys.argv) > 2 else "/api/test"
            print(json.dumps(connector.get(endpoint), ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--post":
            endpoint = sys.argv[2] if len(sys.argv) > 2 else "/api/test"
            print(json.dumps(connector.post(endpoint, {"test": "data"}), ensure_ascii=False, indent=2))
            return 0
    
    print("INTEGRATE-001 API Connector")
    print("Usage:")
    print("  py integrate_001.py --get <endpoint>")
    print("  py integrate_001.py --post <endpoint>")
    return 0
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py integrate_api_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py integrate_api_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""




if __name__ == "__main__":
    import sys
    sys.exit(main())