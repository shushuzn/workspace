from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkspaceSetup:
    python_version: str = '3.13+'
    test_command: str = 'python3 -m unittest discover -s tests -v'
