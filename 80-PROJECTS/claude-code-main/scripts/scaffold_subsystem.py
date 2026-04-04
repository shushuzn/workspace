#!/usr/bin/env python3
"""Scaffold a new subsystem package: creates __init__.py + porting_status.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent / 'src'
SUBSYSTEMS_DIR = SRC_ROOT / 'reference_data' / 'subsystems'


def load_ref(name: str) -> dict | None:
    path = SUBSYSTEMS_DIR / f'{name}.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return None


def scaffold(name: str, dry_run: bool = False) -> None:
    if not name.isidentifier():
        print(f'Error: "{name}" is not a valid Python identifier.', file=sys.stderr)
        sys.exit(1)

    subsystem_dir = SRC_ROOT / name
    if subsystem_dir.exists() and any(subsystem_dir.glob('*.py')):
        print(f'Warning: {subsystem_dir}/ already has Python files — skipping.', file=sys.stderr)
        return

    ref = load_ref(name)
    archive_name = ref.get('archive_name', name) if ref else name
    module_count = ref.get('module_count', 0) if ref else 0
    sample_files = ref.get('sample_files', []) if ref else []

    init_content = f'''"""Python package placeholder for the archived `{archive_name}` subsystem."""

from __future__ import annotations

import json
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / 'reference_data' / 'subsystems' / '{name}.json'
_SNAPSHOT = json.loads(SNAPSHOT_PATH.read_text())

ARCHIVE_NAME = _SNAPSHOT.get('archive_name', '{archive_name}')
MODULE_COUNT = _SNAPSHOT.get('module_count', {module_count})
SAMPLE_FILES = tuple(_SNAPSHOT.get('sample_files', {sample_files}))
PORTING_NOTE = f"Python placeholder package for '{{ARCHIVE_NAME}}' with {{MODULE_COUNT}} archived module references."

__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES']
'''

    status_content = json.dumps({
        'subsystem': name,
        'status': 'stub',
        'progress': 5,
        'total_files': 0,
        'stub_files': [],
        'non_stub_count': 0,
        'expected_modules': module_count,
        'files': [],
    }, indent=2)

    if dry_run:
        print(f'=== {subsystem_dir}/__init__.py ===')
        print(init_content)
        print(f'=== {subsystem_dir}/porting_status.json ===')
        print(status_content)
        return

    subsystem_dir.mkdir(parents=True, exist_ok=True)
    (subsystem_dir / '__init__.py').write_text(init_content, encoding='utf-8')
    (subsystem_dir / 'porting_status.json').write_text(status_content, encoding='utf-8')
    print(f'Created {subsystem_dir}/')
    print(f'  __init__.py — metadata stub (ARCHIVE_NAME, MODULE_COUNT, SAMPLE_FILES)')
    print(f'  porting_status.json — stub status')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Scaffold a new subsystem package')
    parser.add_argument('name', help='Subsystem name (must be valid Python identifier)')
    parser.add_argument('--dry-run', action='store_true', help='Print without writing files')
    args = parser.parse_args()
    scaffold(args.name, dry_run=args.dry_run)
