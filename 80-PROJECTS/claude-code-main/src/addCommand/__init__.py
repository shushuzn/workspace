"""Python port of the `addCommand` tool — adds MCP tool commands."""

from __future__ import annotations

import sys
from pathlib import Path

ARCHIVE_NAME = 'addCommand'
MODULE_COUNT = 1
SAMPLE_FILES = ('commands/mcp/addCommand.ts',)
PORTING_NOTE = 'Python port of the addCommand command'


def run(argv: list[str] | None = None) -> int:
    """Add a command via MCP."""
    if argv is None:
        argv = sys.argv[1:]
    print(f'addCommand: {argv}')
    return 0


__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES', 'run']
