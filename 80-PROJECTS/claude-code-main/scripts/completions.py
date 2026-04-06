#!/usr/bin/env python3
"""Generate shell completions for claude-code-main CLI."""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

COMMANDS = [
    'summary', 'manifest', 'parity-audit', 'subsystems',
    'commands', 'tools', 'route', 'show-command', 'show-tool',
    'snapshot-diff', 'docs',
]

SUB_ARGS = {
    'commands': ['--limit', '--query'],
    'tools': ['--limit', '--query'],
    'route': ['--limit'],
    'show-command': [],
    'show-tool': [],
    'docs': ['--surface', '--query'],
    'subsystems': ['--limit'],
    'snapshot-diff': ['--surface'],
}


def bash_completions() -> str:
    cmds_str = ' '.join(COMMANDS)
    lines = [
        '# bash completion for claude-code-main',
        '_claude_code_main() {',
        '    local cur prev words cword',
        '    _init_completion || return',
        '',
        '    if [[ $cword -eq 1 ]]; then',
        '        COMPREPLY=($(compgen -W "' + cmds_str + '" -- "$cur"))',
        '        return',
        '    fi',
        '',
        '    prev="${words[1]}"',
        '    case "$prev" in',
    ]
    for cmd, args in SUB_ARGS.items():
        if args:
            args_str = ' '.join(args)
            lines.append('        ' + cmd + ')')
            lines.append('            COMPREPLY=($(compgen -W "' + args_str + '" -- "$cur"))')
            lines.append('            return;;')
    lines.extend([
        '    esac',
        '}',
        'complete -F _claude_code_main claude-code-main',
        'complete -F _claude_code_main ccm',
    ])
    return '\n'.join(lines)


def zsh_completions() -> str:
    cmds_str = ' '.join(COMMANDS)
    lines = [
        '# zsh completion for claude-code-main',
        'local -a commands=(' + cmds_str + ')',
        '',
        '_claude_code_main() {',
        '    _arguments \\',
        '        "1: :->command" \\',
        '        "*: :->args"',
        '',
        '    case "$state" in',
        '        command)',
        '            _describe "command" commands',
        '            ;;',
        '        args)',
        '            case "${words[1]}" in',
    ]
    for cmd, args in SUB_ARGS.items():
        if args:
            opts = ' '.join('--' + a[2:] for a in args)
            lines.append('                ' + cmd + ')')
            lines.append('                    _describe "args" (' + opts + ')')
            lines.append('                    ;;')
    lines.extend([
        '            esac',
        '            ;;',
        '    esac',
        '}',
        'compdef _claude_code_main claude-code-main',
        'compdef _claude_code_main ccm',
    ])
    return '\n'.join(lines)


def fish_completions() -> str:
    cmds_str = ' '.join(COMMANDS)
    lines = [
        '# fish completion for claude-code-main',
        'complete -c claude-code-main -f',
        'complete -c ccm -f',
        'complete -c claude-code-main -n "__fish_use_subcommand" -a "' + cmds_str + '"',
        'complete -c ccm -n "__fish_use_subcommand" -a "' + cmds_str + '"',
    ]
    for cmd, args in SUB_ARGS.items():
        if args:
            for a in args:
                opt = '--' + a[2:]
                lines.append('complete -c claude-code-main -n "__fish_seen_subcommand_from ' + cmd + '" -l ' + opt)
                lines.append('complete -c ccm -n "__fish_seen_subcommand_from ' + cmd + '" -l ' + opt)
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate shell completions')
    parser.add_argument('--bash', action='store_true')
    parser.add_argument('--zsh', action='store_true')
    parser.add_argument('--fish', action='store_true')
    args = parser.parse_args()

    if args.bash:
        print(bash_completions())
    elif args.zsh:
        print(zsh_completions())
    elif args.fish:
        print(fish_completions())
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
