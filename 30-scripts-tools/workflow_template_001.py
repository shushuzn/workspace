import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-TEMPLATE-001 Template Generator
"""

import json, sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TEMPLATES = {
    "basic": {
        "name": "Basic Tool",
        "template": '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{name} - {description}
"""

import json, sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class {class_name}:
    def run(self):
        return {{"status": "ok"}}

if __name__ == "__main__":
    tool = {class_name}()
    print(json.dumps(tool.run(), ensure_ascii=False, indent=2))
'''
    },
    "cli": {
        "name": "CLI Tool",
        "template": '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{name} - {description}
"""

import json, sys, argparse

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO)
def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--input", help="Input file")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()
    
    result = {{"status": "ok", "args": vars(args)}}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
'''
    }
}

class WorkflowTemplate:
    def generate(self, template_name, name, description=""):
        if template_name not in TEMPLATES:
            return {"error": f"Unknown template: {template_name}"}
        
        template = TEMPLATES[template_name]["template"]
        class_name = "".join(word.capitalize() for word in name.split("_"))
        
        content = template.format(
            name=name,
            description=description or name,
            class_name=class_name
        )
        
        return {
            "status": "generated",
            "template": template_name,
            "class_name": class_name,
            "preview": content[:200] + "..."
        }

if __name__ == "__main__":
    tmpl = WorkflowTemplate()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--list":
            print(json.dumps({k: v["name"] for k, v in TEMPLATES.items()}, ensure_ascii=False, indent=2))
        elif cmd == "--generate":
            name = sys.argv[2] if len(sys.argv) > 2 else "my_tool"
            desc = sys.argv[3] if len(sys.argv) > 3 else ""
            print(json.dumps(tmpl.generate("basic", name, desc), ensure_ascii=False, indent=2))
    else:
        print("Usage: workflow_template_001.py --list | --generate <name> [description]")
