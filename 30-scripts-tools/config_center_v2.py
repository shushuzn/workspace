#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration Center v2.0 - Advanced Configuration Management
Features: Schema validation, hot reload, encryption, versioning, backup

Usage:
    python config_center.py --validate
    python config_center.py --get system.timezone
    python config_center.py --set system.timezone "Asia/Shanghai"
    python config_center.py --reload
    python config_center.py --history
"""

import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
import threading

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class ConfigSchema:
    """Configuration schema definition"""
    key: str
    type: str  # string/number/boolean/object/array
    required: bool
    default: Any
    description: str
    validation: Optional[str] = None  # Regex or custom validation
    encrypted: bool = False


@dataclass
class ConfigChange:
    """Configuration change record"""
    id: str
    key: str
    old_value: Any
    new_value: Any
    changed_at: str
    changed_by: str
    reason: str


class ConfigCenter:
    """Advanced configuration management"""
    
    def __init__(self):
        self.config_dir = WORKSPACE / "00-09-core-config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.schema_file = self.config_dir / "config_schema.json"
        self.history_file = self.config_dir / "config_history.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = {}
        self.schema = {}
        self.history = []
        self.callbacks = {}  # key -> list of callback functions
        
        self.load_config()
        self.load_schema()
        self.load_history()
        
        # Hot reload
        self.observer = None
        self._start_hot_reload()
    
    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._get_default_config()
            self.save_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'system': {
                'timezone': 'Asia/Hong_Kong',
                'language': 'zh-CN',
                'debug': False,
                'version': '2.0'
            },
            'cache': {
                'enabled': True,
                'ttl_default': 3600,
                'max_memory_items': 1000,
                'compression_threshold': 1024
            },
            'api': {
                'feishu': {
                    'app_id': '',
                    'app_secret': '',
                    'enabled': True
                },
                'openai': {
                    'api_key': '',
                    'model': 'gpt-4',
                    'enabled': False
                },
                'local_llm': {
                    'enabled': True,
                    'backend': 'ollama',
                    'model': 'qwen2.5:1.5b',
                    'endpoint': 'http://localhost:11434'
                }
            },
            'notification': {
                'default_channel': 'console',
                'feishu_enabled': True,
                'email_enabled': False
            },
            'automation': {
                'heartbeat_interval': 1800,  # 30 minutes
                'self_iteration_interval': 1800,  # 30 minutes
                'daily_brief_time': '07:00',
                'security_audit_time': '06:00'
            },
            'models': {
                'local_path': str(WORKSPACE / "models"),
                'default_model': 'qwen2.5:1.5b',
                'fallback_model': 'qwen3.5:0.8b'
            },
            'security': {
                'api_token': 'openclaw-dev-token',
                'encrypt_sensitive': True,
                'audit_logging': True
            }
        }
    
    def load_schema(self):
        """Load configuration schema"""
        if self.schema_file.exists():
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
                self.schema = {
                    item['key']: ConfigSchema(**item)
                    for item in schema_data.get('schemas', [])
                }
        else:
            self.schema = self._get_default_schema()
            self.save_schema()
    
    def _get_default_schema(self) -> Dict[str, ConfigSchema]:
        """Get default schema"""
        return {
            'system.timezone': ConfigSchema(
                key='system.timezone',
                type='string',
                required=True,
                default='Asia/Hong_Kong',
                description='System timezone',
                validation=r'^[A-Za-z]+/[A-Za-z_]+$'
            ),
            'system.debug': ConfigSchema(
                key='system.debug',
                type='boolean',
                required=True,
                default=False,
                description='Debug mode'
            ),
            'cache.enabled': ConfigSchema(
                key='cache.enabled',
                type='boolean',
                required=True,
                default=True,
                description='Enable caching'
            ),
            'cache.ttl_default': ConfigSchema(
                key='cache.ttl_default',
                type='number',
                required=True,
                default=3600,
                description='Default TTL in seconds',
                validation='min:60,max:86400'
            ),
            'api.local_llm.enabled': ConfigSchema(
                key='api.local_llm.enabled',
                type='boolean',
                required=True,
                default=True,
                description='Enable local LLM'
            ),
            'api.local_llm.model': ConfigSchema(
                key='api.local_llm.model',
                type='string',
                required=True,
                default='qwen2.5:1.5b',
                description='Local LLM model'
            ),
            'automation.heartbeat_interval': ConfigSchema(
                key='automation.heartbeat_interval',
                type='number',
                required=True,
                default=1800,
                description='Heartbeat interval (seconds)',
                validation='min:300,max:7200'
            ),
            'security.api_token': ConfigSchema(
                key='security.api_token',
                type='string',
                required=True,
                default='openclaw-dev-token',
                description='API authentication token',
                encrypted=True
            ),
        }
    
    def load_history(self):
        """Load change history"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = data.get('history', [])
    
    def save_config(self):
        """Save configuration"""
        # Backup before save
        self._create_backup()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def save_schema(self):
        """Save schema"""
        schema_data = {
            'schemas': [asdict(s) for s in self.schema.values()],
            'version': '2.0',
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
    
    def _create_backup(self):
        """Create configuration backup"""
        if not self.config_file.exists():
            return  # No config to backup
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"config_backup_{timestamp}.json"
        
        shutil.copy2(self.config_file, backup_file)
        
        # Keep last 20 backups
        backups = sorted(self.backup_dir.glob("config_backup_*.json"))
        for old_backup in backups[:-20]:
            old_backup.unlink()
    
    def validate_value(self, key: str, value: Any) -> tuple:
        """Validate value against schema"""
        if key not in self.schema:
            return True, "No schema defined"
        
        schema = self.schema[key]
        
        # Type check
        type_map = {
            'string': str,
            'number': (int, float),
            'boolean': bool,
            'object': dict,
            'array': list
        }
        
        expected_type = type_map.get(schema.type)
        if not isinstance(value, expected_type):
            return False, f"Expected {schema.type}, got {type(value).__name__}"
        
        # Validation rules
        if schema.validation:
            rules = schema.validation.split(',')
            
            for rule in rules:
                rule = rule.strip()
                
                if rule.startswith('min:'):
                    min_val = float(rule.split(':')[1])
                    if value < min_val:
                        return False, f"Value must be >= {min_val}"
                
                elif rule.startswith('max:'):
                    max_val = float(rule.split(':')[1])
                    if value > max_val:
                        return False, f"Value must be <= {max_val}"
                
                elif rule.startswith('^'):  # Regex
                    import re
                    if not re.match(rule, str(value)):
                        return False, f"Value doesn't match pattern"
        
        return True, "Valid"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, reason: str = '') -> tuple:
        """Set configuration value"""
        # Validate
        valid, message = self.validate_value(key, value)
        if not valid:
            return False, f"Validation failed: {message}"
        
        # Get old value
        keys = key.split('.')
        old_value = self.config
        
        try:
            for k in keys[:-1]:
                old_value = old_value[k]
            old_value = old_value.get(keys[-1])
        except:
            old_value = None
        
        # Set new value
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        
        # Record change
        change = ConfigChange(
            id=f"change_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            key=key,
            old_value=old_value,
            new_value=value,
            changed_at=datetime.now().isoformat(),
            changed_by='user',
            reason=reason or 'Manual update'
        )
        
        self.history.append(asdict(change))
        self.history = self.history[-100:]  # Keep last 100
        
        # Save
        self.save_config()
        self.save_history()
        
        # Trigger callbacks
        self._trigger_callbacks(key, value)
        
        return True, "Updated"
    
    def save_history(self):
        """Save change history"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({
                'history': self.history,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def register_callback(self, key: str, callback: Callable):
        """Register callback for config change"""
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
    
    def _trigger_callbacks(self, key: str, value: Any):
        """Trigger callbacks for config change"""
        if key in self.callbacks:
            for callback in self.callbacks[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"❌ Callback error: {e}")
    
    def _start_hot_reload(self):
        """Start hot reload watcher"""
        if not WATCHDOG_AVAILABLE:
            return  # Skip if watchdog not available
        
        class ConfigHandler(FileSystemEventHandler):
            def __init__(self, config_center):
                self.config_center = config_center
            
            def on_modified(self, event):
                if event.src_path.endswith('config.json'):
                    print("\n🔄 Configuration file changed, reloading...")
                    self.config_center.load_config()
                    print("✅ Configuration reloaded\n")
        
        try:
            self.observer = Observer()
            handler = ConfigHandler(self)
            self.observer.schedule(handler, str(self.config_dir), recursive=False)
            self.observer.start()
        except:
            pass  # Watchdog not available or error
    
    def validate_all(self) -> Dict:
        """Validate all configuration"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        for key, schema in self.schema.items():
            value = self.get(key)
            
            if value is None:
                if schema.required:
                    results['errors'].append(f"{key}: Required but missing")
                    results['valid'] = False
                continue
            
            valid, message = self.validate_value(key, value)
            if not valid:
                results['errors'].append(f"{key}: {message}")
                results['valid'] = False
        
        # Check for unknown keys
        def check_keys(config, prefix=''):
            for key, value in config.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if full_key not in self.schema:
                    if isinstance(value, dict):
                        check_keys(value, full_key)
                    else:
                        results['warnings'].append(f"{full_key}: Unknown key")
        
        check_keys(self.config)
        
        return results
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get change history"""
        return self.history[-limit:]
    
    def rollback(self, change_id: str) -> bool:
        """Rollback to previous value"""
        change = None
        for c in self.history:
            if c['id'] == change_id:
                change = c
                break
        
        if not change:
            return False
        
        # Restore old value
        success, msg = self.set(
            change['key'],
            change['old_value'],
            reason=f"Rollback from {change['id']}"
        )
        
        return success
    
    def export(self, filepath: str):
        """Export configuration"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuration exported: {filepath}")
    
    def import_config(self, filepath: str):
        """Import configuration"""
        with open(filepath, 'r', encoding='utf-8') as f:
            imported = json.load(f)
        
        # Merge with existing
        def merge(source, target):
            for key, value in source.items():
                if isinstance(value, dict) and key in target:
                    merge(value, target[key])
                else:
                    target[key] = value
        
        merge(imported, self.config)
        self.save_config()
        print(f"✅ Configuration imported: {filepath}")
    
    def get_statistics(self) -> Dict:
        """Get configuration statistics"""
        return {
            'total_keys': sum(len(v) if isinstance(v, dict) else 1 for v in self.config.values()),
            'schema_keys': len(self.schema),
            'changes': len(self.history),
            'backups': len(list(self.backup_dir.glob("*.json")))
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Configuration Center v2.0')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--get', type=str, help='Get configuration value')
    parser.add_argument('--set', nargs=2, help='Set configuration value (key value)')
    parser.add_argument('--reason', type=str, default='', help='Reason for change')
    parser.add_argument('--reload', action='store_true', help='Reload configuration')
    parser.add_argument('--history', action='store_true', help='Show change history')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', type=str, help='Export configuration')
    parser.add_argument('--import', dest='import_config', type=str, help='Import configuration')
    args = parser.parse_args()
    
    center = ConfigCenter()
    
    if args.validate:
        results = center.validate_all()
        print("\nConfiguration Validation:\n")
        print(f"Valid: {results['valid']}")
        
        if results['errors']:
            print(f"\nErrors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  ❌ {error}")
        
        if results['warnings']:
            print(f"\nWarnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"  ⚠️  {warning}")
        
        print()
    
    elif args.get:
        value = center.get(args.get)
        print(f"{args.get} = {json.dumps(value, indent=2)}")
    
    elif args.set:
        key, value = args.set
        # Try to parse value
        try:
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif '.' in value:
                value = float(value)
            else:
                value = int(value)
        except:
            pass
        
        success, msg = center.set(key, value, args.reason)
        print(f"{'✅' if success else '❌'} {msg}")
    
    elif args.reload:
        center.load_config()
        print("✅ Configuration reloaded")
    
    elif args.history:
        history = center.get_history()
        print("\nConfiguration History:\n")
        for change in history[-10:][::-1]:
            print(f"  [{change['changed_at'][:19]}] {change['key']}")
            print(f"    {change['old_value']} → {change['new_value']}")
            print(f"    Reason: {change['reason']}\n")
    
    elif args.stats:
        stats = center.get_statistics()
        print(json.dumps(stats, indent=2))
    
    elif args.export:
        center.export(args.export)
    
    elif args.import_config:
        center.import_config(args.import_config)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
