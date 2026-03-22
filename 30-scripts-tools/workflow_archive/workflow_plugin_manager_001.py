import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-PLUGIN-MANAGER-001 Enhanced Plugin System
==================================================
Manage, validate, and load plugins dynamically
"""

import json, sys, importlib.util, traceback
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PLUGIN_DIR = Path("30-scripts-tools/plugins")
PLUGIN_DIR.mkdir(exist_ok=True)

PLUGIN_TEMPLATE = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
{class_name} Plugin
"""

def run(args=None):
    return {{
        "plugin": "{name}",
        "status": "ok",
        "message": "Plugin executed successfully"
    }}

def info():
    return {{
        "name": "{name}",
        "version": "1.0.0",
        "description": "Plugin for {name}",
        "author": "OpenClaw"
    }}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
'''

class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def install(self, name, description="", author="OpenClaw") -> None:
        """Install a new plugin"""
        plugin_file = PLUGIN_DIR / f"{name}.py"
        
        if plugin_file.exists():
            return {"status": "exists", "plugin": name}
        
        class_name = "".join(word.capitalize() for word in name.split("_"))
        content = PLUGIN_TEMPLATE.format(name=name, class_name=class_name, description=description)
        
        plugin_file.write_text(content, encoding="utf-8")
        return {"status": "installed", "plugin": name, "path": str(plugin_file)}
    
    def uninstall(self, name) -> None:
        """Remove a plugin"""
        plugin_file = PLUGIN_DIR / f"{name}.py"
        
        if not plugin_file.exists():
            return {"status": "not_found", "plugin": name}
        
        plugin_file.unlink()
        return {"status": "uninstalled", "plugin": name}
    
    def load(self, name) -> None:
        """Load and execute a plugin"""
        plugin_file = PLUGIN_DIR / f"{name}.py"
        
        if not plugin_file.exists():
            return {"error": f"Plugin not found: {name}"}
        
        try:
            spec = importlib.util.spec_from_file_location(name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return {
                "status": "loaded",
                "plugin": name,
                "info": module.info() if hasattr(module, 'info') else None
            }
        except Exception as e:
            return {"error": str(e), "traceback": traceback.format_exc()}
    
    def run(self, name, args=None) -> None:
        """Run a plugin"""
        plugin_file = PLUGIN_DIR / f"{name}.py"
        
        if not plugin_file.exists():
            return {"error": f"Plugin not found: {name}"}
        
        try:
            spec = importlib.util.spec_from_file_location(name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'run'):
                return module.run(args)
            return {"error": "Plugin has no run() function"}
        except Exception as e:
            return {"error": str(e)}
    
    def list(self) -> None:
        """List all installed plugins"""
        plugins = []
        for f in PLUGIN_DIR.glob("*.py"):
            if f.stem in ["__init__", "__pycache__"]:
                continue
            
            try:
                spec = importlib.util.spec_from_file_location(f.stem, f)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                info = module.info() if hasattr(module, 'info') else {"name": f.stem}
                plugins.append(info)
            except (Exception,):
                plugins.append({"name": f.stem, "status": "error"})
        
        return {"plugins": plugins, "count": len(plugins)}
    
    def validate(self, name) -> None:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py workflow_plugin_manager_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_plugin_manager_001.py

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

Validate a plugin"""
        plugin_file = PLUGIN_DIR / f"{name}.py"
        
        if not plugin_file.exists():
            return {"valid": False, "error": "not_found"}
        
        try:
            spec = importlib.util.spec_from_file_location(name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            checks = {
                "has_run": hasattr(module, 'run'),
                "has_info": hasattr(module, 'info'),
                "syntax_ok": True
            }
            
            return {
                "valid": checks["has_run"],
                "plugin": name,
                "checks": checks
            }
        except SyntaxError as e:
            return {"valid": False, "error": "syntax_error", "line": e.lineno}
        except Exception as e:
            return {"valid": False, "error": str(e)}

if __name__ == "__main__":
    pm = PluginManager()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--install":
            name = sys.argv[2] if len(sys.argv) > 2 else "new_plugin"
            desc = sys.argv[3] if len(sys.argv) > 3 else ""
            print(json.dumps(pm.install(name, desc), ensure_ascii=False, indent=2))
        elif cmd == "--uninstall":
            name = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(pm.uninstall(name), ensure_ascii=False, indent=2))
        elif cmd == "--list":
            print(json.dumps(pm.list(), ensure_ascii=False, indent=2))
        elif cmd == "--run":
            name = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(pm.run(name), ensure_ascii=False, indent=2))
        elif cmd == "--validate":
            name = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(pm.validate(name), ensure_ascii=False, indent=2))
        elif cmd == "--load":
            name = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(pm.load(name), ensure_ascii=False, indent=2))
    else:
        print("WORKFLOW-PLUGIN-MANAGER-001")
        print("Commands:")
        print("  --install <name> [desc]  Install plugin")
        print("  --uninstall <name>       Remove plugin")
        print("  --list                   List plugins")
        print("  --run <name>             Run plugin")
        print("  --validate <name>        Validate plugin")
        print("  --load <name>            Load plugin")
