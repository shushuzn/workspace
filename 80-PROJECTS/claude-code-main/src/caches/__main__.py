"""Entry point: python -m src.caches"""

from __future__ import annotations

import sys

from . import run

if __name__ == '__main__':
    raise SystemExit(run(sys.argv[1:]))
