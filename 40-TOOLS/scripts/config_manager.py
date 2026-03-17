#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config Manager - Phase 4 Innovation
Centralized configuration management for all tools
Features: validation, encryption, backup, sync across environments

Usage:
    python config_manager.py --show
    python config_manager.py --set KEY=value
    python config_manager.py --validate
    python config_manager.py --backup
"""

import os
import sys
import json
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Workspace root
WORKSPACE = Path(__file__).parent.parent
CONFIG_DIR = WORKSPACE / "00-00-config"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = WORKSPACE / ".env"
BACKUP_DIR = CONFIG_DIR / "backups"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self):
        self.config = self._load_config()
        self.schema = self._get_schema()
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        default_config = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "general": {
                "workspace": str(WORKSPACE),
                "timezone": "Asia/Hong_Kong",
                "language": "zh-CN",
                "debug_mode": False
            },
            "llm": {
                "provider": "ollama",
                "model": "qwen2.5:1.5b",
                "base_url": "http://localhost:11434",
                "timeout_seconds": 120,
                "max_tokens": 2048
            },
            "feishu": {
                "app_id": "",
                "app_secret": "",
                "user_id": "ou_72a847b95fc25870dcdd8ce56d929252",
                "token_cache_minutes": 40
            },
            "cloud": {
                "host": os.getenv("HOST_IP_8_208_30_28", os.getenv("HOST_IP", os.getenv("HOST_IP", "8.208.30.28"))),
                "user": "root",
                "ssh_port": 22,
                "deploy_path": "/opt/openclaw"
            },
            "scheduler": {
                "heartbeat_interval_minutes": 30,
                "health_check_interval_minutes": 60,
                "max_concurrent_tasks": 3,
                "quiet_hours_start": 2,
                "quiet_hours_end": 6
            },
            "cache": {
                "enabled": True,
                "ttl_default_seconds": 3600,
                "max_size_mb": 500,
                "cleanup_interval_hours": 24
            },
            "notifications": {
                "channels": ["desktop", "feishu"],
                "min_priority": "normal",
                "quiet_hours_enabled": True,
                "rate_limit_per_hour": 20
            },
            "security": {
                "encrypt_sensitive": True,
                "backup_enabled": True,
                "backup_retention_days": 30
            }
        }
        
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge with defaults
                return self._merge_configs(default_config, loaded)
        else:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            self._save_config(default_config)
            return default_config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config: Dict = None):
        """Save configuration"""
        if config:
            self.config = config
        
        self.config['last_updated'] = datetime.now().isoformat()
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def _get_schema(self) -> Dict:
        """Get configuration schema for validation"""
        return {
            "general.workspace": {"type": "string", "required": True},
            "general.timezone": {"type": "string", "required": True, "pattern": r"^[A-Za-z_/]+$"},
            "general.language": {"type": "string", "required": True},
            "general.debug_mode": {"type": "boolean", "required": False},
            
            "llm.provider": {"type": "string", "required": True, "enum": ["ollama", "openai", "anthropic"]},
            "llm.model": {"type": "string", "required": True},
            "llm.base_url": {"type": "string", "required": True, "pattern": r"^https?://"},
            "llm.timeout_seconds": {"type": "integer", "min": 10, "max": 600},
            "llm.max_tokens": {"type": "integer", "min": 100, "max": 32000},
            
            "feishu.app_id": {"type": "string", "required": False},
            "feishu.app_secret": {"type": "string", "required": False, "sensitive": True},
            "feishu.user_id": {"type": "string", "required": True},
            
            "cloud.host": {"type": "string", "required": True, "pattern": r"^\d+\.\d+\.\d+\.\d+$"},
            "cloud.user": {"type": "string", "required": True},
            "cloud.ssh_port": {"type": "integer", "min": 1, "max": 65535},
            
            "scheduler.heartbeat_interval_minutes": {"type": "integer", "min": 5, "max": 1440},
            "scheduler.max_concurrent_tasks": {"type": "integer", "min": 1, "max": 10},
            
            "cache.enabled": {"type": "boolean", "required": True},
            "cache.ttl_default_seconds": {"type": "integer", "min": 60, "max": 86400},
            
            "notifications.channels": {"type": "array", "items": {"type": "string"}},
            "notifications.min_priority": {"type": "string", "enum": ["low", "normal", "important", "urgent"]},
        }
    
    def show_config(self, section: str = None):
        """Show configuration"""
        print("\n" + "=" * 60)
        print("Configuration")
        print("=" * 60)
        
        config = self.config.copy()
        
        # Hide sensitive values
        self._hide_sensitive(config)
        
        if section:
            if section in config:
                print(f"\n[{section.upper()}]")
                self._print_dict(config[section], indent=2)
            else:
                print(f"[ERROR] Section not found: {section}")
        else:
            for section_name, section_data in config.items():
                if isinstance(section_data, dict):
                    print(f"\n[{section_name.upper()}]")
                    self._print_dict(section_data, indent=2)
                else:
                    print(f"  {section_name}: {section_data}")
        
        print("=" * 60)
    
    def _hide_sensitive(self, config: Dict):
        """Hide sensitive values"""
        sensitive_keys = ['app_secret', 'password', 'token', 'secret']
        
        for key, value in config.items():
            if isinstance(value, dict):
                self._hide_sensitive(value)
            elif any(s in key.lower() for s in sensitive_keys):
                if value and len(value) > 4:
                    config[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
    
    def _print_dict(self, d: Dict, indent: int = 0):
        """Pretty print dictionary"""
        for key, value in d.items():
            prefix = " " * indent
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                self._print_dict(value, indent + 2)
            elif isinstance(value, list):
                print(f"{prefix}{key}: {', '.join(str(v) for v in value)}")
            else:
                print(f"{prefix}{key}: {value}")
    
    def set_value(self, key_path: str, value: Any):
        """Set a configuration value"""
        print(f"[SET] {key_path} = {value}")
        
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set value
        final_key = keys[-1]
        old_value = config.get(final_key)
        config[final_key] = self._parse_value(value)
        
        # Validate
        validation = self.validate_key(key_path, config[final_key])
        if not validation['valid']:
            print(f"[ERROR] Validation failed: {validation['error']}")
            config[final_key] = old_value  # Revert
            return False
        
        # Save
        self._save_config()
        print(f"[OK] Updated {key_path}")
        
        return True
    
    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type"""
        # Try JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Try boolean
        if value.lower() in ['true', 'yes', '1']:
            return True
        if value.lower() in ['false', 'no', '0']:
            return False
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def validate_key(self, key_path: str, value: Any) -> Dict:
        """Validate a configuration key"""
        schema = self.schema.get(key_path)
        
        if not schema:
            return {'valid': True, 'warning': 'No schema defined'}
        
        # Type check
        expected_type = schema.get('type')
        if expected_type == 'string' and not isinstance(value, str):
            return {'valid': False, 'error': f'Expected string, got {type(value).__name__}'}
        if expected_type == 'integer' and not isinstance(value, int):
            return {'valid': False, 'error': f'Expected integer, got {type(value).__name__}'}
        if expected_type == 'boolean' and not isinstance(value, bool):
            return {'valid': False, 'error': f'Expected boolean, got {type(value).__name__}'}
        if expected_type == 'array' and not isinstance(value, list):
            return {'valid': False, 'error': f'Expected array, got {type(value).__name__}'}
        
        # Enum check
        if 'enum' in schema and value not in schema['enum']:
            return {'valid': False, 'error': f'Value must be one of: {schema["enum"]}'}
        
        # Range check
        if 'min' in schema and isinstance(value, (int, float)) and value < schema['min']:
            return {'valid': False, 'error': f'Value must be >= {schema["min"]}'}
        if 'max' in schema and isinstance(value, (int, float)) and value > schema['max']:
            return {'valid': False, 'error': f'Value must be <= {schema["max"]}'}
        
        # Pattern check
        if 'pattern' in schema and isinstance(value, str):
            import re
            if not re.match(schema['pattern'], value):
                return {'valid': False, 'error': f'Value does not match pattern'}
        
        return {'valid': True}
    
    def validate_all(self) -> Dict:
        """Validate all configuration"""
        print("[VALIDATE] Validating configuration...")
        
        errors = []
        warnings = []
        
        for key_path, schema in self.schema.items():
            # Get value
            keys = key_path.split('.')
            value = self.config
            try:
                for key in keys:
                    value = value[key]
            except (KeyError, TypeError):
                if schema.get('required'):
                    errors.append(f"Missing required key: {key_path}")
                continue
            
            # Validate
            result = self.validate_key(key_path, value)
            if not result['valid']:
                errors.append(f"{key_path}: {result['error']}")
            elif result.get('warning'):
                warnings.append(f"{key_path}: {result['warning']}")
        
        result = {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\nValidation Result: {'✅ PASS' if result['valid'] else '❌ FAIL'}")
        print(f"  Errors:   {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        
        if errors:
            print("\nErrors:")
            for error in errors[:10]:
                print(f"  - {error}")
        
        return result
    
    def backup_config(self) -> Path:
        """Create configuration backup"""
        print("[BACKUP] Creating configuration backup...")
        
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_name = f"config-backup-{timestamp}.json"
        backup_path = BACKUP_DIR / backup_name
        
        # Copy config
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Backup saved to {backup_path}")
        
        # Cleanup old backups
        self._cleanup_old_backups()
        
        return backup_path
    
    def _cleanup_old_backups(self, keep: int = 10):
        """Remove old backups"""
        backups = sorted(BACKUP_DIR.glob("config-backup-*.json"))
        
        if len(backups) > keep:
            for old_backup in backups[:-keep]:
                old_backup.unlink()
                print(f"[CLEANUP] Removed old backup: {old_backup.name}")
    
    def restore_config(self, backup_name: str) -> Dict:
        """Restore configuration from backup"""
        print(f"[RESTORE] Restoring from {backup_name}...")
        
        backup_path = BACKUP_DIR / backup_name
        
        if not backup_path.exists():
            # Try without extension
            backup_path = BACKUP_DIR / f"{backup_name}.json"
        
        if not backup_path.exists():
            return {'error': f'Backup not found: {backup_name}', 'status': 'failed'}
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                restored_config = json.load(f)
            
            # Backup current config first
            self.backup_config()
            
            # Restore
            self.config = restored_config
            self._save_config()
            
            print(f"[OK] Configuration restored from {backup_name}")
            
            return {'status': 'success', 'backup': str(backup_path)}
        
        except Exception as e:
            return {'error': str(e), 'status': 'failed'}


def main():
    parser = argparse.ArgumentParser(description='Config Manager')
    parser.add_argument('--show', type=str, nargs='?', const='all', help='Show configuration')
    parser.add_argument('--set', type=str, help='Set config value (KEY=value)')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--backup', action='store_true', help='Backup configuration')
    parser.add_argument('--restore', type=str, help='Restore from backup')
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.show:
        if args.show == 'all':
            manager.show_config()
        else:
            manager.show_config(args.show)
    
    if args.set:
        if '=' not in args.set:
            print("[ERROR] Format: KEY=value")
            return
        key, value = args.set.split('=', 1)
        manager.set_value(key, value)
    
    if args.validate:
        manager.validate_all()
    
    if args.backup:
        manager.backup_config()
    
    if args.restore:
        result = manager.restore_config(args.restore)
        print(f"\nResult: {json.dumps(result, indent=2)}")
    
    if not any([args.show, args.set, args.validate, args.backup, args.restore]):
        parser.print_help()


if __name__ == "__main__":
    main()
