import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('symbols', nargs='*')
parser.add_argument('--summary', nargs='*')
parser.add_argument('--technical', action='store_true')
parser.add_argument('--compare', nargs='*')

# 模拟命令行参数
sys.argv = ['main.py', 'NVDA', 'META', 'JPM', '--summary']
args = parser.parse_args()

print(f'symbols: {args.symbols}')
print(f'summary: {args.summary}')
print(f'technical: {args.technical}')
print(f'compare: {args.compare}')

print()
print('Condition checks:')
print(f'  args.symbols: {bool(args.symbols)} (truthy: {args.symbols if args.symbols else "empty"})')
print(f'  args.summary: {args.summary} (bool: {bool(args.summary)})')
