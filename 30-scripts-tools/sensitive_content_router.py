#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Sensitive Content Router - Auto-route sensitive content to local Qwen model
Zero cloud API calls for sensitive data

Usage:
    python sensitive_content_router.py --text "Your content"
    python sensitive_content_router.py --file input.txt
    python sensitive_content_router.py --config
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Workspace root
WORKSPACE = Path(__file__).parent.parent
REPORTS_DIR = WORKSPACE / "20-data-reports"

# Ensure UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class SensitiveContentRouter:
    """Auto-route content to local or cloud processing"""
    
    # Sensitive content patterns (high priority - always local)
    SENSITIVE_PATTERNS = [
        # Authentication
        (r'password', 'password'),
        (r'passwd', 'password'),
        (r'密码', 'password'),
        (r'密钥', 'secret_key'),
        (r'token', 'token'),
        (r'secret', 'secret'),
        (r'credential', 'credential'),
        (r'凭证', 'credential'),
        
        # Personal Information
        (r'\d{17}[\dXx]', 'chinese_id'),  # Chinese ID
        (r'\d{16}', 'credit_card'),  # Credit card
        (r'passport', 'passport'),
        (r'护照', 'passport'),
        (r'身份证', 'chinese_id'),
        
        # Financial
        (r'银行', 'bank_card'),
        (r'银行卡', 'bank_card'),
        (r'收入', 'income'),
        (r'资产', 'asset'),
        (r'财务', 'financial'),
        
        # Medical
        (r'诊断', 'diagnosis'),
        (r'病历', 'medical_record'),
        (r'处方', 'prescription'),
        (r'医疗', 'medical'),
        (r'健康', 'health'),
        
        # Biometric
        (r'指纹', 'fingerprint'),
        (r'面部', 'face_recognition'),
        (r'DNA', 'dna'),
        (r'生物', 'biometric'),
        
        # API Keys
        (r'api', 'api_key'),
        (r'API', 'api_key'),
        (r'access.?token', 'access_token'),
        (r'private.?key', 'private_key'),
        (r'私钥', 'private_key'),
    ]
    
    # Cloud-allowed content patterns
    CLOUD_SAFE_PATTERNS = [
        r'general\s+knowledge',
        r'学术\s+研究',
        r'公开\s+数据',
        r'新闻\s+报道',
    ]
    
    def __init__(self):
        self.stats = {
            "total_processed": 0,
            "local_processed": 0,
            "cloud_processed": 0,
            "sensitive_detected": 0
        }
    
    def classify_content(self, text: str) -> Dict[str, Any]:
        """Classify content sensitivity"""
        matches = []
        sensitivity_score = 0.0
        
        # Check sensitive patterns
        for pattern, category in self.SENSITIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(category)
                sensitivity_score += 0.2
        
        # Cap at 1.0
        sensitivity_score = min(1.0, sensitivity_score)
        
        # Determine processing route
        if sensitivity_score >= 0.2:
            route = "local"
            confidence = 0.95
        else:
            route = "cloud"
            confidence = 0.8
        
        result = {
            "route": route,
            "sensitivity_score": sensitivity_score,
            "confidence": confidence,
            "matched_categories": list(set(matches)),
            "timestamp": datetime.now().isoformat(),
            "processing": {
                "local": route == "local",
                "cloud": route == "cloud"
            }
        }
        
        self.stats["total_processed"] += 1
        if route == "local":
            self.stats["local_processed"] += 1
            self.stats["sensitive_detected"] += 1
        else:
            self.stats["cloud_processed"] += 1
        
        return result
    
    def process(self, text: str, force_local: bool = False) -> Dict[str, Any]:
        """Process content with automatic routing"""
        # Classify
        classification = self.classify_content(text)
        
        # Force local if specified
        if force_local:
            classification["route"] = "local"
            classification["forced"] = True
        
        result = {
            "classification": classification,
            "processing": {
                "status": "routed",
                "engine": "local_qwen" if classification["route"] == "local" else "cloud_api",
                "zero_cloud": classification["route"] == "local"
            }
        }
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total = self.stats["total_processed"]
        return {
            **self.stats,
            "local_percentage": round(self.stats["local_processed"] / total * 100, 2) if total > 0 else 0,
            "cloud_percentage": round(self.stats["cloud_processed"] / total * 100, 2) if total > 0 else 0,
            "zero_cloud_policy": "100% sensitive content processed locally"
        }


def create_router_config():
    """Create router configuration file"""
    config = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "policy": {
            "sensitive_content": "local_only",
            "cloud_allowed": "non_sensitive_only",
            "zero_cloud_for_sensitive": True
        },
        "local_model": {
            "name": "Qwen2.5-0.5B-Instruct",
            "format": "GGUF",
            "location": "models/qwen2.5-0.5b-instruct/",
            "inference_engine": "llama-cpp-python"
        },
        "sensitive_categories": [
            "authentication",
            "personal_information",
            "financial",
            "medical",
            "biometric",
            "api_keys"
        ],
        "routing_rules": {
            "sensitivity_threshold": 0.2,
            "auto_detect": True,
            "force_local_flag": "--force-local"
        }
    }
    
    config_path = WORKSPACE / "30-scripts-tools" / "sensitive_router_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Config created: {config_path}")
    return config_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sensitive Content Router")
    parser.add_argument("--text", type=str, help="Text to classify and route")
    parser.add_argument("--file", type=str, help="File to classify and route")
    parser.add_argument("--force-local", action="store_true", help="Force local processing")
    parser.add_argument("--config", action="store_true", help="Create/show config")
    parser.add_argument("--stats", action="store_true", help="Show processing stats")
    
    args = parser.parse_args()
    
    router = SensitiveContentRouter()
    
    if args.config:
        config_path = create_router_config()
        print(f"\nConfig file: {config_path}")
        sys.exit(0)
    
    if args.stats:
        stats = router.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[FAIL] File not found: {file_path}")
            sys.exit(1)
        text = file_path.read_text(encoding='utf-8')
        args.text = text
    
    if args.text:
        result = router.process(args.text, force_local=args.force_local)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Visual indicator
        route = result["classification"]["route"]
        if route == "local":
            print("\n🔒 ROUTED TO LOCAL QWEN (0% cloud API calls)")
        else:
            print("\n☁️ ROUTED TO CLOUD API (non-sensitive content)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
