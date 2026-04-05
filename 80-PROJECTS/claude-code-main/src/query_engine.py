from __future__ import annotations

from dataclasses import dataclass

from .commands import PORTED_COMMANDS, build_command_backlog
from .port_manifest import PortManifest, build_port_manifest
from .tools import PORTED_TOOLS, build_tool_backlog


@dataclass
class QueryEnginePort:
    manifest: PortManifest

    @classmethod
    def from_workspace(cls) -> 'QueryEnginePort':
        return cls(manifest=build_port_manifest())

    def render_summary(self) -> str:
        command_backlog = build_command_backlog()
        tool_backlog = build_tool_backlog()
        sections = [
            '# Python Porting Workspace Summary',
            '',
            self.manifest.to_markdown(),
            '',
            f'{command_backlog.title}: {len(PORTED_COMMANDS)} mirrored entries',
            *command_backlog.summary_lines()[:10],
            '',
            f'{tool_backlog.title}: {len(PORTED_TOOLS)} mirrored entries',
            *tool_backlog.summary_lines()[:10],
        ]
        return '\n'.join(sections)
