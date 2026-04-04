"""Python port of the `review` command group."""

from __future__ import annotations

import sys

ARCHIVE_NAME = 'review'
MODULE_COUNT = 5
SAMPLE_FILES = (
    'commands/review.ts',
    'commands/review/ultrareviewCommand.tsx',
    'commands/review/ultrareviewEnabled.ts',
    'commands/review/reviewRemote.ts',
    'commands/security-review.ts',
)
PORTING_NOTE = 'Python port of the review command group'


def run(argv: list[str] | None = None) -> int:
    """Run a review subcommand."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print('review: a code review command group')
        print('subcommands: ultrareviewCommand, ultrareviewEnabled, reviewRemote, security-review, UltrareviewOverageDialog')
        return 0

    subcommand = argv[0]
    sub_name = subcommand.replace('-', '_')
    sub_module = f'.subcommands.{sub_name}'
    args = argv[1:]

    try:
        from . import subcommands
        mod = getattr(subcommands, sub_name, None)
        if mod is None or not hasattr(mod, 'run'):
            raise AttributeError(f'no run in {sub_name}')
        return mod.run(args)
    except (ImportError, AttributeError):
        print(f'review: unknown subcommand: {subcommand}', file=sys.stderr)
        return 1


__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES', 'run']
