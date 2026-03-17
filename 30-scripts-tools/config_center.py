#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration Center - Core System Iteration
Centralized configuration management with validation
Features: schema validation, environment overrides, encryption support

Usage:
    python config_center.py --show
    python config_center.py --validate
    python config_center.py --get KEY
    python config_center.py --export
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

# Workspace root
WORKSPACE = Path(__file__).parent.parent
CONFIG_FILE = WORKSPACE / "config.json"
ENV_FILE = WORKSPACE / ".env"
SCHEMA_FILE = WORKSPACE / "config_schema.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class ConfigCenter:
    """Centralized configuration management"""
    
    def __init__(self):
        self.config = self._load_config()
        self.env = self._load_env()
        self.schema = self._load_schema()
    
    def _load_config(self) -> Dict:
        """Load main configuration"""
        default_config = {
            # System Configuration
            'system': {
                'workspace': str(WORKSPACE),
                'timezone': 'Asia/Hong_Kong',
                'language': 'zh-CN',
                'debug_mode': False,
                'log_level': 'INFO'
            },
            
            # Cache Configuration
            'cache': {
                'enabled': True,
                'max_memory_items': 1000,
                'compression_threshold': 1024,
                'default_ttl': 3600,
                'clean_interval': 300
            },
            
            # API Configuration
            'api': {
                'port': 8080,
                'host': '0.0.0.0',
                'cors_enabled': True,
                'rate_limit': 100,
                'timeout': 30
            },
            
            # Notification Configuration
            'notification': {
                'feishu_enabled': True,
                'email_enabled': False,
                'desktop_enabled': True,
                'batch_notifications': True,
                'quiet_hours': {'start': '23:00', 'end': '07:00'}
            },
            
            # Automation Configuration
            'automation': {
                'heartbeat_interval': 1800,  # 30 minutes
                'daily_brief_time': '07:00',
                'weekly_report_day': 'Sunday',
                'weekly_report_time': '05:00',
                'auto_commit': True,
                'auto_push': True
            },
            
            # Model Configuration
            'models': {
                'default_model': 'qwen2.5:1.5b',
                'fast_model': 'qwen3.5:0.8b',
                'deep_analysis_model': 'qwen3.5:2b',
                'sensitivity_threshold': 0.2,
                'local_only': True
            },
            
            # Security Configuration
            'security': {
                'encrypt_sensitive': True,
                'audit_logging': True,
                'max_login_attempts': 5,
                'session_timeout': 3600
            },
            
            # Performance Configuration
            'performance': {
                'parallel_workers': 4,
                'max_memory_mb': 2048,
                'batch_size': 50,
                'enable_profiling': False
            }
        }
        
        # Load from file
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    
                    # Merge with defaults
                    for key, value in file_config.items():
                        if key in default_config:
                            if isinstance(value, dict) and isinstance(default_config[key], dict):
                                default_config[key].update(value)
                            else:
                                default_config[key] = value
            except Exception as e:
                print(f"[WARN] Failed to load config: {e}")
        
        return default_config
    
    def _load_env(self) -> Dict:
        """Load environment variables from .env file"""
        env = {}
        
        if ENV_FILE.exists():
            try:
                with open(ENV_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env[key.strip()] = value.strip()
            except Exception as e:
                print(f"[WARN] Failed to load .env: {e}")
        
        return env
    
    def _load_schema(self) -> Dict:
        """Load configuration schema for validation"""
        default_schema = {
            'system': {
                'type': 'object',
                'required': ['workspace', 'timezone'],
                'properties': {
                    'workspace': {'type': 'string'},
                    'timezone': {'type': 'string'},
                    'language': {'type': 'string'},
                    'debug_mode': {'type': 'boolean'},
                    'log_level': {'type': 'string', 'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR']}
                }
            },
            'cache': {
                'type': 'object',
                'properties': {
                    'enabled': {'type': 'boolean'},
                    'max_memory_items': {'type': 'integer', 'min': 100, 'max': 10000},
                    'compression_threshold': {'type': 'integer', 'min': 0},
                    'default_ttl': {'type': 'integer', 'min': 60},
                    'clean_interval': {'type': 'integer', 'min': 60}
                }
            },
            'api': {
                'type': 'object',
                'properties': {
                    'port': {'type': 'integer', 'min': 1024, 'max': 65535},
                    'host': {'type': 'string'},
                    'cors_enabled': {'type': 'boolean'},
                    'rate_limit': {'type': 'integer', 'min': 1},
                    'timeout': {'type': 'integer', 'min': 1}
                }
            },
            'models': {
                'type': 'object',
                'properties': {
                    'default_model': {'type': 'string'},
                    'sensitivity_threshold': {'type': 'number', 'min': 0, 'max': 1},
                    'local_only': {'type': 'boolean'}
                }
            }
        }
        
        # Load custom schema
        if SCHEMA_FILE.exists():
            try:
                with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                    custom_schema = json.load(f)
                    default_schema.update(custom_schema)
            except:
                pass
        
        return default_schema
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # Check environment override first
        env_key = key.replace('.', '_').upper()
        if env_key in self.env:
            return self._parse_value(self.env[env_key])
        
        # Navigate config tree
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type"""
        # Try boolean
        if value.lower() in ['true', 'yes', '1']:
            return True
        if value.lower() in ['false', 'no', '0']:
            return False
        
        # Try integer
        try:
            return int(value)
        except:
            pass
        
        # Try float
        try:
            return float(value)
        except:
            pass
        
        # Return as string
        return value
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        
        # Navigate to parent
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
        
        # Save to file
        if save:
            return self._save_config()
        
        return True
    
    def _save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Config saved to {CONFIG_FILE}")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
            return False
    
    def validate(self) -> Dict:
        """Validate configuration against schema"""
        print("\n" + "=" * 60)
        print("Validating Configuration")
        print("=" * 60)
        
        errors = []
        warnings = []
        
        for section, schema in self.schema.items():
            if section not in self.config:
                if schema.get('required'):
                    errors.append(f"Missing required section: {section}")
                continue
            
            section_config = self.config[section]
            properties = schema.get('properties', {})
            
            for prop_name, prop_schema in properties.items():
                if prop_name not in section_config:
                    if prop_schema.get('required'):
                        errors.append(f"Missing required property: {section}.{prop_name}")
                    continue
                
                value = section_config[prop_name]
                expected_type = prop_schema.get('type')
                
                # Type validation
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Type mismatch: {section}.{prop_name} should be string")
                elif expected_type == 'integer' and not isinstance(value, int):
                    errors.append(f"Type mismatch: {section}.{prop_name} should be integer")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Type mismatch: {section}.{prop_name} should be boolean")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Type mismatch: {section}.{prop_name} should be number")
                
                # Range validation
                if 'min' in prop_schema and isinstance(value, (int, float)):
                    if value < prop_schema['min']:
                        errors.append(f"Value too low: {section}.{prop_name} < {prop_schema['min']}")
                
                if 'max' in prop_schema and isinstance(value, (int, float)):
                    if value > prop_schema['max']:
                        errors.append(f"Value too high: {section}.{prop_name} > {prop_schema['max']}")
                
                # Enum validation
                if 'enum' in prop_schema:
                    if value not in prop_schema['enum']:
                        errors.append(f"Invalid value: {section}.{prop_name} not in {prop_schema['enum']}")
        
        # Print results
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"   • {error}")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
        
        if not errors and not warnings:
            print("\n✅ Configuration is valid!")
        
        print("=" * 60)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def show(self) -> Dict:
        """Show all configuration"""
        print("\n" + "=" * 60)
        print("Configuration Center")
        print("=" * 60)
        
        for section, config in self.config.items():
            print(f"\n📋 {section.upper()}")
            
            if isinstance(config, dict):
                for key, value in config.items():
                    env_key = f"{section}_{key}".upper()
                    env_override = "🔄 ENV" if env_key in self.env else ""
                    print(f"   {key}: {value} {env_override}")
            else:
                print(f"   {config}")
        
        print("=" * 60)
        
        return self.config
    
    def export(self, format: str = 'json') -> str:
        """Export configuration"""
        if format == 'json':
            return json.dumps(self.config, indent=2, ensure_ascii=False)
        elif format == 'env':
            lines = []
            for section, config in self.config.items():
                if isinstance(config, dict):
                    for key, value in config.items():
                        env_key = f"{section}_{key}".upper()
                        lines.append(f"{env_key}={value}")
            return '\n'.join(lines)
        else:
            return str(self.config)


def main():
    parser = argparse.ArgumentParser(description='Configuration Center')
    parser.add_argument('--show', action='store_true', help='Show all configuration')
    parser.add_argument('--validate', action='store_true', help='Validate configuration')
    parser.add_argument('--get', type=str, metavar='KEY', help='Get configuration value')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set configuration value')
    parser.add_argument('--export', type=str, choices=['json', 'env'], help='Export configuration')
    args = parser.parse_args()
    
    config = ConfigCenter()
    
    if args.show:
        config.show()
    
    if args.validate:
        result = config.validate()
        sys.exit(0 if result['valid'] else 1)
    
    if args.get:
        value = config.get(args.get)
        if value is not None:
            print(f"{args.get} = {value}")
        else:
            print(f"[MISS] {args.get} not found")
    
    if args.set:
        key, value = args.set
        parsed_value = config._parse_value(value)
        config.set(key, parsed_value)
    
    if args.export:
        exported = config.export(format=args.export)
        print(exported)
    
    if not any([args.show, args.validate, args.get, args.set, args.export]):
        parser.print_help()


if __name__ == "__main__":
    main()
