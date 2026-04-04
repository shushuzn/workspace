from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class SnapshotDiff:
    added: tuple[str, ...]
    removed: tuple[str, ...]
    unchanged: int

    def to_markdown(self, surface: str) -> str:
        lines = [f'## {surface}', '']
        if not self.added and not self.removed:
            lines.append('No changes.')
        if self.added:
            lines.append(f'**Added** ({len(self.added)}):')
            for name in sorted(self.added):
                lines.append(f'- `{name}`')
            lines.append('')
        if self.removed:
            lines.append(f'**Removed** ({len(self.removed)}):')
            for name in sorted(self.removed):
                lines.append(f'- `{name}`')
            lines.append('')
        lines.append(f'Unchanged: {self.unchanged}')
        return '\n'.join(lines)


def diff_snapshots(old_path: str, new_path: str, key: str = 'name') -> SnapshotDiff:
    with open(old_path, encoding='utf-8') as f:
        old_entries = json.load(f)
    with open(new_path, encoding='utf-8') as f:
        new_entries = json.load(f)

    old_names = {entry[key] for entry in old_entries}
    new_names = {entry[key] for entry in new_entries}

    added = tuple(sorted(new_names - old_names))
    removed = tuple(sorted(old_names - new_names))
    unchanged = len(old_names & new_names)

    return SnapshotDiff(added=added, removed=removed, unchanged=unchanged)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Diff two JSON snapshot files and output a Markdown report')
    parser.add_argument('old_snapshot', help='Path to the older snapshot JSON')
    parser.add_argument('new_snapshot', help='Path to the newer snapshot JSON')
    parser.add_argument('--surface', default='Snapshot Diff', help='Name of the surface being compared')
    args = parser.parse_args(argv)

    try:
        diff = diff_snapshots(args.old_snapshot, args.new_snapshot)
    except FileNotFoundError as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON — {e}', file=sys.stderr)
        return 1

    print(diff.to_markdown(args.surface))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
