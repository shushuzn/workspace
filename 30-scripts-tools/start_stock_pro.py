#!/usr/bin/env python
"""
Stock PRO - One-Click Launcher
Run: python start_stock_pro.py
"""
import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent / "stock_pro"

def check_dash():
    try:
        import dash
        return True
    except:
        return False

def install_dash():
    print("\nInstalling Dash...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'dash', 'plotly'], check=True)
    print("Done!")

def main():
    print("=" * 50)
    print("  Stock PRO - One-Click Launcher")
    print("=" * 50)
    print("\nOptions:")
    print("  [1] Simple UI (no install, port 8080)")
    print("  [2] Dash UI (needs install, port 8050)")
    print("  [3] Install Dash")
    print("  [4] Run tests")
    print("  [0] Exit")

    choice = input("\nChoice: ").strip()

    if choice == '1':
        print("\nStarting Simple UI...")
        print("Open: http://127.0.0.1:8080\n")
        subprocess.run([sys.executable, 'simple_ui.py'], cwd=SCRIPT_DIR)

    elif choice == '2':
        if not check_dash():
            print("\nDash not installed. Installing...")
            install_dash()
        print("\nStarting Dash UI...")
        print("Open: http://127.0.0.1:8050\n")
        subprocess.run([sys.executable, 'dash_app.py'], cwd=SCRIPT_DIR)

    elif choice == '3':
        install_dash()

    elif choice == '4':
        print("\nRunning tests...\n")
        subprocess.run([sys.executable, 'test_all.py'], cwd=SCRIPT_DIR)

    elif choice == '0':
        return

    else:
        print("Invalid choice")

if __name__ == '__main__':
    main()
