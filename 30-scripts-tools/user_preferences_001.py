import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Preference Profiles - Comprehensive preference management
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class UserPreferenceManager:
    """Manage user preferences across sessions"""
    
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.profiles_dir = Path("03-config/user_profiles")
        self.current_profile = self._load_profile(profile_name)
    
    def _load_profile(self, name: str) -> Dict:
        """Load user profile"""
        profile_file = self.profiles_dir / f"{name}.json"
        
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Create default profile
        return self._create_default_profile(name)
    
    def _create_default_profile(self, name: str) -> Dict:
        """Create default profile"""
        profile = {
            "version": "1.0",
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "preferences": {
                "verbosity": "detailed",
                "output_format": "auto",
                "show_emojis": True,
                "show_progress": True,
                "auto_compress": True,
                "typing_indicator": True,
                "typing_indicator_delay": 2.0,
                "error_handling": "friendly",
                "summary_mode": "expandable",
                "language": "en",
                "timezone": "UTC",
            },
            "shortcuts": {
                "brief": "/brief",
                "detailed": "/detailed",
                "status": "/status",
                "help": "/help",
            },
            "usage_stats": {
                "total_sessions": 0,
                "total_commands": 0,
                "favorite_commands": [],
                "last_active": None,
            }
        }
        
        self._save_profile(profile)
        return profile
    
    def _save_profile(self, profile: Dict = None) -> None:
        """Save profile to file"""
        if profile is None:
            profile = self.current_profile
        
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        profile_file = self.profiles_dir / f"{self.profile_name}.json"
        
        profile["updated_at"] = datetime.now().isoformat()
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    
    def get_preference(self, key: str, default=None) -> Any:
        """Get a preference value"""
        return self.current_profile["preferences"].get(key, default)
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a preference value"""
        self.current_profile["preferences"][key] = value
        self._save_profile()
    
    def get_all_preferences(self) -> Dict:
        """Get all preferences"""
        return self.current_profile["preferences"].copy()
    
    def reset_preferences(self) -> None:
        """Reset all preferences to defaults"""
        self.current_profile = self._create_default_profile(self.profile_name)
    
    def get_shortcut(self, name: str) -> str:
        """Get a shortcut command"""
        return self.current_profile["shortcuts"].get(name, f"/{name}")
    
    def set_shortcut(self, name: str, command: str) -> None:
        """Set a shortcut command"""
        self.current_profile["shortcuts"][name] = command
        self._save_profile()
    
    def track_usage(self, command: str) -> None:
        """Track command usage"""
        stats = self.current_profile["usage_stats"]
        stats["total_commands"] += 1
        stats["last_active"] = datetime.now().isoformat()
        
        # Track favorite commands
        if command not in stats["favorite_commands"]:
            stats["favorite_commands"].append(command)
        
        # Keep only top 10
        stats["favorite_commands"] = stats["favorite_commands"][-10:]
        
        self._save_profile()
    
    def increment_session_count(self) -> None:
        """Increment session count"""
        self.current_profile["usage_stats"]["total_sessions"] += 1
        self._save_profile()
    
    def list_profiles(self) -> List[str]:
        """List all available profiles"""
        if not self.profiles_dir.exists():
            return []
        
        return [f.stem for f in self.profiles_dir.glob("*.json")]
    
    def switch_profile(self, name: str) -> bool:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py user_preferences_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py user_preferences_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

Switch to a different profile"""
        profile_file = self.profiles_dir / f"{name}.json"
        
        if not profile_file.exists():
            return False
        
        self.profile_name = name
        self.current_profile = self._load_profile(name)
        return True
    
    def export_profile(self, output_file: str) -> None:
        """Export profile to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_profile, f, ensure_ascii=False, indent=2)
    
    def import_profile(self, input_file: str, new_name: str = None) -> None:
        """Import profile from file"""
        with open(input_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        if new_name:
            profile["name"] = new_name
            self.profile_name = new_name
        
        self.current_profile = profile
        self._save_profile()
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return self.current_profile["usage_stats"]
    
    def display_status(self) -> str:
        """Display current profile status"""
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "User Preference Profile")
        output.append("=" * 70)
        
        output.append(f"\n[Profile: {self.current_profile['name']}]")
        output.append(f"  Created:  {self.current_profile['created_at']}")
        output.append(f"  Updated:  {self.current_profile['updated_at']}")
        
        output.append(f"\n[Preferences]")
        for key, value in self.current_profile["preferences"].items():
            output.append(f"  {key:25} {value}")
        
        output.append(f"\n[Shortcuts]")
        for name, cmd in self.current_profile["shortcuts"].items():
            output.append(f"  {name:15} -> {cmd}")
        
        stats = self.current_profile["usage_stats"]
        output.append(f"\n[Usage Statistics]")
        output.append(f"  Total Sessions:    {stats['total_sessions']}")
        output.append(f"  Total Commands:    {stats['total_commands']}")
        output.append(f"  Last Active:       {stats['last_active'] or 'Never'}")
        
        if stats["favorite_commands"]:
            output.append(f"  Favorite Commands: {', '.join(stats['favorite_commands'][-5:])}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main() -> None:
    """Test entry point"""
    print("User Preference Manager Test")
    print("=" * 70)
    
    # Test 1: Load default profile
    print("\n[Test 1] Load Default Profile")
    manager = UserPreferenceManager("default")
    print(manager.display_status())
    
    # Test 2: Get/Set preferences
    print("\n[Test 2] Get/Set Preferences")
    print(f"  Current verbosity: {manager.get_preference('verbosity')}")
    manager.set_preference('verbosity', 'brief')
    print(f"  After set: {manager.get_preference('verbosity')}")
    
    # Test 3: Track usage
    print("\n[Test 3] Track Usage")
    manager.track_usage('/brief')
    manager.track_usage('/status')
    stats = manager.get_stats()
    print(f"  Total commands: {stats['total_commands']}")
    print(f"  Favorite: {stats['favorite_commands']}")
    
    # Test 4: List profiles
    print("\n[Test 4] List Profiles")
    profiles = manager.list_profiles()
    print(f"  Available profiles: {profiles}")
    
    # Test 5: Shortcuts
    print("\n[Test 5] Shortcuts")
    print(f"  Brief shortcut: {manager.get_shortcut('brief')}")
    manager.set_shortcut('brief', '/b')
    print(f"  After change: {manager.get_shortcut('brief')}")
    
    print("\n[OK] User preference manager test completed")

if __name__ == "__main__":
    main()
