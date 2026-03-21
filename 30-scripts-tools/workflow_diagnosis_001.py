#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WORKFLOW-DIAGNOSIS-001 Workflow Bottleneck Analyzer
"""

import json, sys, re
from pathlib import Path
from collections import Counter

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path("30-scripts-tools")

class WorkflowDiagnosis:
    def analyze(self):
        results = {
            "tools": self._analyze_tools(),
            "patterns": self._analyze_patterns(),
            "duplicates": self._find_duplicates(),
            "bottlenecks": self._find_bottlenecks()
        }
        return results
    
    def _analyze_tools(self):
        tools = list(TOOLS_DIR.glob("*_001.py"))
        return {
            "total": len(tools),
            "categories": self._categorize(tools)
        }
    
    def _categorize(self, tools):
        cats = {"brainstorm": [], "workflow": [], "tool": [], "data": [], "other": []}
        for t in tools:
            name = t.stem.lower()
            if "brainstorm" in name or "scamper" in name or "hats" in name:
                cats["brainstorm"].append(t.name)
            elif "workflow" in name or "chain" in name or "runner" in name:
                cats["workflow"].append(t.name)
            elif "tool" in name or "validator" in name or "namer" in name:
                cats["tool"].append(t.name)
            elif "data" in name or "cache" in name or "storage" in name:
                cats["data"].append(t.name)
            else:
                cats["other"].append(t.name)
        return {k: len(v) for k, v in cats.items()}
    
    def _analyze_patterns(self):
        issues = []
        for f in TOOLS_DIR.glob("*_001.py"):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                if "subprocess.run" in content and "timeout=" not in content:
                    issues.append({"file": f.name, "issue": "no_timeout"})
                if "json.loads" in content and 'encoding="utf-8"' not in content:
                    issues.append({"file": f.name, "issue": "no_encoding"})
            except (IOError, OSError, UnicodeDecodeError):
                pass
        return issues
    
    def _find_duplicates(self):
        base_names = {}
        for f in TOOLS_DIR.glob("*_001.py"):
            base = re.sub(r'_\d+$', '', f.stem)
            if base not in base_names:
                base_names[base] = []
            base_names[base].append(f.name)
        return [{"base": k, "files": v} for k, v in base_names.items() if len(v) > 1][:10]
    
    def _find_bottlenecks(self):
        return [
            {"type": "manual_dispatch", "description": "工具需要手动选择执行顺序"},
            {"type": "no_cache", "description": "相同任务无缓存机制"},
            {"type": "isolated", "description": "工具之间无状态共享"}
        ]

if __name__ == "__main__":
    d = WorkflowDiagnosis()
    result = d.analyze()
    print(json.dumps(result, ensure_ascii=False, indent=2))
