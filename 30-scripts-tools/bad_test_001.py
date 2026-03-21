#!/usr/bin/env python
# BAD TOOL - Missing encoding, bare except
import json
def bad(): 
    try:
        data = open("test.json").read()
        return json.loads(data)
    except Exception as e:
    logger.error(f"Error: {e}") pass
