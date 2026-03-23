#!/usr/bin/env python
"""
Stock PRO UI Launcher
Run: python start_ui.py
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dash():
    """Check if Dash is installed"""
    try:
        import dash
        print(f"✓ Dash {dash.__version__} installed")
        return True
    except ImportError:
        print("✗ Dash not installed")
        return False

def install_dash():
    """Install Dash"""
    print("\nInstalling Dash...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'dash', 'plotly'])
    print("\n✓ Dash installed!")

def main():
    print("=" * 50)
    print("  Stock PRO Dashboard Launcher")
    print("=" * 50)

    # Get script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    while True:
        print("\nChoose UI:")
        print("  [1] Simple UI (no install, port 8080)")
        print("  [2] Dash UI (requires install, port 8050)")
        print("  [3] Install Dash")
        print("  [0] Exit")

        choice = input("\nChoice (0-3): ").strip()

        if choice == '1':
            print("\n" + "=" * 50)
            print("Starting Simple UI...")
            print("Open: http://127.0.0.1:8080")
            print("Press Ctrl+C to stop")
            print("=" * 50)
            subprocess.run([sys.executable, 'simple_ui.py'])

        elif choice == '2':
            if not check_dash():
                print("\nDash not installed. Install? (y/n)")
                if input().lower() != 'y':
                    continue
                install_dash()

            print("\n" + "=" * 50)
            print("Starting Dash UI...")
            print("Open: http://127.0.0.1:8050")
            print("Press Ctrl+C to stop")
            print("=" * 50)
            subprocess.run([sys.executable, 'dash_app.py'])

        elif choice == '3':
            install_dash()

        elif choice == '0':
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()
