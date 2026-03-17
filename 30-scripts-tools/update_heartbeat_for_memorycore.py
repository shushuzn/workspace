#!/usr/bin/env python3
"""
Update HEARTBEAT.md to use Memory Core v2.0 instead of deprecated tools
"""

import re
import sys
from pathlib import Path

# Fix Windows UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

HEARTBEAT_FILE = Path(__file__).parent.parent / 'HEARTBEAT.md'

# Read current content
with open(HEARTBEAT_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacement mappings
replacements = {
    # Memory Distiller v2 → MemoryCore
    r'python 30-scripts-tools/memory_distiller_v2\.py --check-quality': 
        'python -c "from memory_core import MemoryCore; MemoryCore().check_quality()"',
    r'python 30-scripts-tools/memory_distiller_v2\.py --distill':
        'python -c "from memory_core import MemoryCore; MemoryCore().distill(\'FILE\')"',
    r'python 30-scripts-tools/memory_distiller_v2\.py --batch':
        'python -c "from memory_core import MemoryCore; MemoryCore().distill_batch()"',
    r'python 30-scripts-tools/memory_distiller_v2\.py --cleanup':
        'python -c "from memory_core import MemoryCore; MemoryCore().cleanup()"',
    r'python 30-scripts-tools/memory_distiller_v2\.py --density':
        'python -c "from memory_core import MemoryCore; MemoryCore().analyze_density()"',
    r'python 30-scripts-tools/memory_distiller_v2\.py --audit':
        'python -c "from memory_core import MemoryCore; MemoryCore().audit()"',
    
    # Memory Orchestrator → MemoryCore
    r'python 30-scripts-tools/memory_orchestrator\.py run-pipeline quick':
        'python -c "from memory_core import MemoryCore; MemoryCore().process(\'MEMORY.md\', pipeline=\'quick\')"',
    r'python 30-scripts-tools/memory_orchestrator\.py run-pipeline weekly':
        'python -c "from memory_core import MemoryCore; MemoryCore().process(\'MEMORY.md\', pipeline=\'weekly\')"',
    r'python 30-scripts-tools/memory_orchestrator\.py run-pipeline monthly':
        'python -c "from memory_core import MemoryCore; MemoryCore().process(\'MEMORY.md\', pipeline=\'monthly\')"',
    r'python 30-scripts-tools/memory_orchestrator\.py status --brief':
        'python -c "from memory_core import MemoryCore; print(MemoryCore().status())"',
    r'python 30-scripts-tools/memory_orchestrator\.py generate-report':
        'python -c "from memory_core import MemoryCore; MemoryCore().generate_report()"',
    
    # Memory Quality Scorer → MemoryCore
    r'python 30-scripts-tools/memory_quality_scorer\.py --memory':
        'python -c "from memory_core import MemoryCore; MemoryCore().assess_quality(\'FILE\')"',
}

# Count replacements
count = 0
for old, new in replacements.items():
    matches = re.findall(old, content)
    if matches:
        count += len(matches)
        content = re.sub(old, new, content)
        print(f"[OK] Replaced: {old[:50]}... ({len(matches)} occurrences)")

# Write updated content
with open(HEARTBEAT_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[OK] HEARTBEAT.md updated successfully!")
print(f"    Total replacements: {count}")
print(f"\n[WARN] Note: Some placeholders like 'FILE' and 'MEMORY.md' may need manual adjustment")
