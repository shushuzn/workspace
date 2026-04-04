#!/usr/bin/env python3
"""Porting tracker: generates per-subsystem porting_status.json files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent / 'src'
SUBSYSTEMS_DIR = SRC_ROOT / 'reference_data' / 'subsystems'


def stub_files(py_files: list[Path]) -> list[str]:
    """Files considered stubs (empty or near-empty)."""
    stubs = []
    for f in py_files:
        if f.name == '__init__.py':
            content = f.read_text(encoding='utf-8').strip()
            # __init__.py is a stub if it's empty or only has docstring/imports
            lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith('#')]
            if len(lines) <= 2:
                stubs.append(f.name)
    return stubs


def assess_subsystem(name: str, py_files: list[Path]) -> dict:
    """Assess the porting status of a single subsystem."""
    stub_names = stub_files(py_files)
    # Non-stub = files not in stub_names (metadata __init__.py counts as non-stub)
    non_stub = [f for f in py_files if f.name not in stub_names]

    if not py_files:
        status = 'missing'
        progress = 0
    elif len(non_stub) == 0:
        status = 'stub'
        progress = 5
    elif len(non_stub) <= 2:
        status = 'minimal'
        progress = 25
    elif len(non_stub) <= len(py_files) // 2 + 1:
        status = 'partial'
        progress = 50
    else:
        status = 'substantial'
        progress = 75

    # Check reference data for expected module count
    ref_file = SUBSYSTEMS_DIR / f'{name}.json'
    expected_modules = None
    if ref_file.exists():
        try:
            ref = json.loads(ref_file.read_text(encoding='utf-8'))
            expected_modules = ref.get('module_count')
        except Exception:
            pass

    return {
        'subsystem': name,
        'status': status,
        'progress': progress,
        'total_files': len(py_files),
        'stub_files': stub_names,
        'non_stub_count': len(non_stub),
        'expected_modules': expected_modules,
        'files': [f.name for f in py_files],
    }


def scan_all_subsystems() -> dict:
    """Scan all subsystem directories and generate status reports."""
    results = []
    for ref_file in sorted(SUBSYSTEMS_DIR.glob('*.json')):
        name = ref_file.stem
        subsystem_dir = SRC_ROOT / name
        py_files = sorted(subsystem_dir.glob('*.py')) if subsystem_dir.is_dir() else []
        status = assess_subsystem(name, py_files)
        results.append(status)

        # Write status file inside subsystem dir
        out_path = subsystem_dir / 'porting_status.json'
        out_path.write_text(json.dumps(status, indent=2), encoding='utf-8')

    return {
        'generated': str(Path(__file__).name),
        'total': len(results),
        'subsystems': results,
    }


def render_summary(all_status: dict) -> str:
    lines = ['# Subsystem Porting Status', '']
    status_order = ['complete', 'substantial', 'partial', 'minimal', 'stub', 'missing']
    order_idx = {s: i for i, s in enumerate(status_order)}

    sorted_subsystems = sorted(
        all_status['subsystems'], key=lambda x: (order_idx.get(x['status'], 99), x['subsystem'])
    )

    current_section = None
    for s in sorted_subsystems:
        section = s['status'].upper()
        if section != current_section:
            current_section = section
            lines.append(f'## {section}')
            lines.append('')
        bar = '█' * (s['progress'] // 10) + '░' * (10 - s['progress'] // 10)
        lines.append(f"- `{s['subsystem']:<30}` {bar} {s['progress']:3d}%  ({s['total_files']} files)")
    return '\n'.join(lines)


if __name__ == '__main__':
    all_status = scan_all_subsystems()
    if '--json' in sys.argv:
        print(json.dumps(all_status, indent=2))
    else:
        print(render_summary(all_status))
