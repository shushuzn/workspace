import sys
sys.path.insert(0, 'D:/OpenClaw/workspace/30-scripts-tools')

from stock_pro.core import fetch, A
print('Testing fetch...')
try:
    price, source, fetched, expires = fetch('NVDA')
    print(f'NVDA: {price}, source={source}, fetched={fetched}')
except Exception as e:
    print(f'Error: {e}')
