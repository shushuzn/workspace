import argparse
parser = argparse.ArgumentParser()
parser.add_argument('symbols', nargs='*')
parser.add_argument('--csv', nargs='?', default=None, const=None)

# Test 1: NVDA META --csv
args1 = parser.parse_args(['NVDA', 'META', '--csv'])
print(f"Test 1 (NVDA META --csv):")
print(f"  symbols: {args1.symbols}")
print(f"  csv: {args1.csv}")

# Test 2: --csv NVDA META
parser2 = argparse.ArgumentParser()
parser2.add_argument('symbols', nargs='*')
parser2.add_argument('--csv', nargs='?', default=None, const=None)
args2 = parser2.parse_args(['--csv', 'NVDA', 'META'])
print(f"\nTest 2 (--csv NVDA META):")
print(f"  symbols: {args2.symbols}")
print(f"  csv: {args2.csv}")
