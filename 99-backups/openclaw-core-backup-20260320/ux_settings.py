#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Settings Toggle - Brief/Detailed Mode
"""

import json
from pathlib import Path
from datetime import datetime

class UXSettings:
    """User Experience Settings Manager"""

    def __init__(self):
        self.config_file = Path("03-config/ux_settings.json")
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load settings from config file"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Default settings
        return {
            "version": "1.0",
            "verbosity": "detailed",  # "brief" or "detailed"
            "show_emojis": True,
            "show_progress": True,
            "auto_compress": True,
            "updated_at": datetime.now().isoformat()
        }

    def _save_settings(self):
        """Save settings to config file"""
        self.settings["updated_at"] = datetime.now().isoformat()

        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def set_verbosity(self, mode: str) -> bool:
        """
        Set verbosity mode
        
        Args:
            mode: "brief" or "detailed"
            
        Returns:
            True if successful, False otherwise
        """
        if mode not in ["brief", "detailed"]:
            return False

        old_mode = self.settings["verbosity"]
        self.settings["verbosity"] = mode
        self._save_settings()

        return True

    def get_verbosity(self) -> str:
        """Get current verbosity mode"""
        return self.settings["verbosity"]

    def toggle_verbosity(self) -> str:
        """
        Toggle between brief and detailed mode
        
        Returns:
            New verbosity mode
        """
        current = self.settings["verbosity"]
        new_mode = "brief" if current == "detailed" else "detailed"
        self.settings["verbosity"] = new_mode
        self._save_settings()

        return new_mode

    def get_setting(self, key: str, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value):
        """Set a specific setting value"""
        self.settings[key] = value
        self._save_settings()

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = {
            "version": "1.0",
            "verbosity": "detailed",
            "show_emojis": True,
            "show_progress": True,
            "auto_compress": True,
            "updated_at": datetime.now().isoformat()
        }
        self._save_settings()

    def get_status(self) -> dict:
        """Get current settings status"""
        return {
            "verbosity": self.settings["verbosity"],
            "show_emojis": self.settings["show_emojis"],
            "show_progress": self.settings["show_progress"],
            "auto_compress": self.settings["auto_compress"],
            "updated_at": self.settings["updated_at"]
        }

    def display_status(self) -> str:
        """Display current settings"""
        status = self.get_status()

        output = []
        output.append("\n" + "=" * 60)
        output.append(" " * 18 + "UX Settings Status")
        output.append("=" * 60)

        output.append(f"\n  Verbosity:      {status['verbosity'].upper()}")
        output.append(f"  Show Emojis:    {'Yes' if status['show_emojis'] else 'No'}")
        output.append(f"  Show Progress:  {'Yes' if status['show_progress'] else 'No'}")
        output.append(f"  Auto Compress:  {'Yes' if status['auto_compress'] else 'No'}")
        output.append(f"  Last Updated:   {status['updated_at']}")

        output.append("\n" + "-" * 60)
        output.append("  Commands:")
        output.append("    /brief   - Switch to brief mode")
        output.append("    /detailed - Switch to detailed mode")
        output.append("    /toggle  - Toggle between modes")
        output.append("    /status  - Show current settings")
        output.append("    /reset   - Reset to defaults")
        output.append("=" * 60 + "\n")

        return "\n".join(output)

def main():
    """Test entry point"""
    settings = UXSettings()

    print("UX Settings Test")
    print("=" * 60)

    # Display current status
    print(settings.display_status())

    # Test toggle
    print("\n[Testing Toggle]")
    for i in range(3):
        new_mode = settings.toggle_verbosity()
        print(f"  Toggle {i +1}: Mode = {new_mode}")

    # Test set_verbosity
    print("\n[Testing Set Verbosity]")
    test_modes = ["brief", "detailed", "invalid"]
    for mode in test_modes:
        success = settings.set_verbosity(mode)
        print(f"  Set '{mode}': {'OK' if success else 'Failed'}")

    # Test get_setting
    print("\n[Testing Get Settings]")
    print(f"  Current verbosity: {settings.get_verbosity()}")
    print(f"  Show emojis: {settings.get_setting('show_emojis')}")

    # Reset to defaults
    print("\n[Resetting to Defaults]")
    settings.reset_to_defaults()
    print(f"  Reset complete. New verbosity: {settings.get_verbosity()}")

    print("\n[OK] UX settings test completed")

if __name__ == "__main__":
    main()
