#!/usr/bin/env python
"""
Install Dash for Stock PRO UI
Run: pip install dash plotly
"""
import subprocess
import sys

def install():
    packages = ['dash', 'plotly']

    print("Installing Dash and dependencies...")
    for pkg in packages:
        print(f"  Installing {pkg}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', pkg],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ {pkg} installed")
        else:
            print(f"  ✗ {pkg} failed: {result.stderr[:100]}")

    print("\nDone! Run:")
    print("  cd 30-scripts-tools/stock_pro")
    print("  python dash_app.py")
    print("  Open: http://127.0.0.1:8050")

if __name__ == '__main__':
    install()
