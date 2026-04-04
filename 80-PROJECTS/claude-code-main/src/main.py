from __future__ import annotations

import argparse

from .commands import find_commands, get_command, render_command_index
from .parity_audit import run_parity_audit
from .port_manifest import build_port_manifest
from .query_engine import QueryEnginePort
from .runtime import PortRuntime
from .snapshot_diff import diff_snapshots
from .tools import find_tools, get_tool, render_tool_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Python porting workspace for the Claude Code rewrite effort')
    subparsers = parser.add_subparsers(dest='command', required=True)
    subparsers.add_parser('summary', help='render a Markdown summary of the Python porting workspace')
    subparsers.add_parser('manifest', help='print the current Python workspace manifest')
    subparsers.add_parser('parity-audit', help='compare the Python workspace against the local ignored TypeScript archive when available')
    list_parser = subparsers.add_parser('subsystems', help='list the current Python modules in the workspace')
    list_parser.add_argument('--limit', type=int, default=32)
    commands_parser = subparsers.add_parser('commands', help='list mirrored command entries from the archived snapshot')
    commands_parser.add_argument('--limit', type=int, default=20)
    commands_parser.add_argument('--query')
    tools_parser = subparsers.add_parser('tools', help='list mirrored tool entries from the archived snapshot')
    tools_parser.add_argument('--limit', type=int, default=20)
    tools_parser.add_argument('--query')
    route_parser = subparsers.add_parser('route', help='route a prompt across mirrored command/tool inventories')
    route_parser.add_argument('prompt')
    route_parser.add_argument('--limit', type=int, default=5)
    show_command = subparsers.add_parser('show-command', help='show one mirrored command entry by exact name')
    show_command.add_argument('name')
    show_tool = subparsers.add_parser('show-tool', help='show one mirrored tool entry by exact name')
    show_tool.add_argument('name')
    diff_parser = subparsers.add_parser('snapshot-diff', help='diff two JSON snapshot files')
    diff_parser.add_argument('old_snapshot')
    diff_parser.add_argument('new_snapshot')
    diff_parser.add_argument('--surface', default='Snapshot Diff')
    docs_parser = subparsers.add_parser('docs', help='generate Markdown CLI reference')
    docs_parser.add_argument('--surface', default='all', choices=['all', 'commands', 'tools'])
    docs_parser.add_argument('--query')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manifest = build_port_manifest()
    if args.command == 'summary':
        print(QueryEnginePort(manifest).render_summary())
        return 0
    if args.command == 'manifest':
        print(manifest.to_markdown())
        return 0
    if args.command == 'parity-audit':
        print(run_parity_audit().to_markdown())
        return 0
    if args.command == 'subsystems':
        for subsystem in manifest.top_level_modules[: args.limit]:
            print(f'{subsystem.name}\t{subsystem.file_count}\t{subsystem.notes}')
        return 0
    if args.command == 'commands':
        print(render_command_index(limit=args.limit, query=args.query))
        return 0
    if args.command == 'tools':
        print(render_tool_index(limit=args.limit, query=args.query))
        return 0
    if args.command == 'route':
        matches = PortRuntime().route_prompt(args.prompt, limit=args.limit)
        if not matches:
            print('No mirrored command/tool matches found.')
            return 0
        for match in matches:
            print(f'{match.kind}\t{match.name}\t{match.score}\t{match.source_hint}')
        return 0
    if args.command == 'show-command':
        module = get_command(args.name)
        if module is None:
            print(f'Command not found: {args.name}')
            return 1
        print(f'{module.name}\n{module.source_hint}\n{module.responsibility}')
        return 0
    if args.command == 'show-tool':
        module = get_tool(args.name)
        if module is None:
            print(f'Tool not found: {args.name}')
            return 1
        print(f'{module.name}\n{module.source_hint}\n{module.responsibility}')
        return 0
    if args.command == 'snapshot-diff':
        diff = diff_snapshots(args.old_snapshot, args.new_snapshot)
        print(diff.to_markdown(args.surface))
        return 0
    if args.command == 'docs':
        lines = ['# CLI Reference', '']
        surface = args.surface
        if surface in ('all', 'commands'):
            cmds = find_commands(args.query) if args.query else list(PORTED_COMMANDS)
            lines.append(f'## Commands ({len(cmds)})')
            lines.append('')
            for m in cmds:
                lines.append(f'`/{m.name}` — {m.responsibility}')
                lines.append(f'> Source: `{m.source_hint}`')
                lines.append('')
        if surface in ('all', 'tools'):
            tools = find_tools(args.query) if args.query else list(PORTED_TOOLS)
            lines.append(f'## Tools ({len(tools)})')
            lines.append('')
            for m in tools:
                lines.append(f'`/{m.name}` — {m.responsibility}')
                lines.append(f'> Source: `{m.source_hint}`')
                lines.append('')
        print('\n'.join(lines))
        return 0
    parser.error(f'unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
