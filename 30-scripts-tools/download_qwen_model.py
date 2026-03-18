#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download Qwen model for local sensitive content processing
Downloads GGUF format model from HuggingFace/ModelScope

Usage: python download_qwen_model.py [--model MODEL]

Models:
  - qwen2.5-0.5b (default, legacy, ~0.5GB)
  - qwen3.5-0.8b (recommended, better accuracy, ~0.8GB)
"""

import os
import sys
import argparse
from pathlib import Path

# Workspace root
WORKSPACE = Path(__file__).parent.parent
MODELS_DIR = WORKSPACE / "models"

# Model configurations
MODELS = {
    'qwen2.5-0.5b': {
        'repo': 'Qwen/Qwen2.5-0.5B-Instruct-GGUF',
        'file': 'qwen2.5-0_5b-instruct-q5_k_m.gguf',
        'size_gb': 0.5,
    },
    'qwen2.5-1.5b': {
        'repo': 'Qwen/Qwen2.5-1.5B-Instruct-GGUF',
        'file': 'qwen2.5-1.5b-instruct-q5_k_m.gguf',
        'size_gb': 1.2,
    },
    'qwen3-0.6b': {
        'repo': 'Qwen/Qwen3-0.6B-Instruct-GGUF',
        'file': 'qwen3-0_6b-instruct-q5_k_m.gguf',
        'size_gb': 0.5,
    },
    'qwen3.5-0.8b': {
        'repo': 'unsloth/Qwen3.5-0.8B-GGUF',
        'file': 'Qwen3.5-0.8B-Q5_K_M.gguf',
        'size_gb': 0.6,
    },
}

def check_disk_space(required_gb: int = 2) -> bool:
    """Check if enough disk space is available"""
    import shutil
    total, used, free = shutil.disk_usage(WORKSPACE)
    free_gb = free / (1024 ** 3)
    if free_gb < required_gb:
        print(f"[ERROR] Insufficient disk space: {free_gb:.2f} GB available, need {required_gb} GB")
        return False
    print(f"[OK] Disk space OK: {free_gb:.2f} GB available")
    return True

def download_model(model_name: str) -> bool:
    """Download model using ModelScope or HuggingFace"""
    model_config = MODELS.get(model_name)
    if not model_config:
        print(f"[ERROR] Unknown model: {model_name}")
        print(f"Available: {list(MODELS.keys())}")
        return False
    
    model_dir = MODELS_DIR / model_name
    
    # Try ModelScope first (faster in China)
    try:
        from modelscope import snapshot_download
        
        print(f"[DOWNLOAD] {model_name} via ModelScope...")
        print(f"   Repository: {model_config['repo']}")
        print(f"   File: {model_config['file']}")
        print(f"   Size: ~{model_config['size_gb']} GB")
        print(f"   Target: {model_dir}")
        
        # Create models directory
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Download entire model
        downloaded_dir = snapshot_download(
            model_config['repo'],
            local_dir=model_dir,
            revision="master"
        )
        
        print(f"[OK] Model downloaded: {downloaded_dir}")
        return True
        
    except ImportError:
        print("[INFO] ModelScope not installed, trying HuggingFace mirror...")
    except Exception as e:
        print(f"[WARN] ModelScope failed: {e}")
    
    # Fallback to HuggingFace mirror (for China)
    try:
        import os
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        from huggingface_hub import hf_hub_download
        
        print(f"\n[DOWNLOAD] {model_name} via HuggingFace Mirror (hf-mirror.com)...")
        print(f"   Repository: {model_config['repo']}")
        print(f"   File: {model_config['file']}")
        print(f"   Target: {model_dir}")
        
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Download specific GGUF file
        model_file = hf_hub_download(
            repo_id=model_config['repo'],
            filename=model_config['file'],
            local_dir=model_dir,
            repo_type="model"
        )
        
        print(f"[OK] Model downloaded: {model_file}")
        return True
        
    except Exception as e:
        print(f"[ERROR] HuggingFace mirror download failed: {e}")
        return False

def verify_model(model_name: str) -> bool:
    """Verify model file exists"""
    model_dir = MODELS_DIR / model_name
    gguf_files = list(model_dir.glob("*.gguf"))
    
    if gguf_files:
        model_size = gguf_files[0].stat().st_size / (1024 ** 3)
        print(f"[OK] Model verified: {gguf_files[0].name} ({model_size:.2f} GB)")
        return True
    
    print(f"[ERROR] Model file not found in {model_dir}")
    return False

def list_models():
    """List available models"""
    print("\nAvailable Models:")
    print("-" * 60)
    for name, config in MODELS.items():
        print(f"  {name:20} | {config['size_gb']} GB | {config['repo']}")
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description='Download Qwen GGUF model')
    parser.add_argument('--model', type=str, default='qwen3.5-0.8b',
                        choices=list(MODELS.keys()),
                        help='Model to download (default: qwen3.5-0.8b)')
    parser.add_argument('--list', action='store_true', help='List available models')
    args = parser.parse_args()
    
    if args.list:
        list_models()
        sys.exit(0)
    
    model_name = args.model
    model_config = MODELS[model_name]
    
    print("=" * 60)
    print(f"Qwen Model Downloader - {model_name}")
    print("=" * 60)
    print()
    
    # Check disk space
    if not check_disk_space(2):
        sys.exit(1)
    
    # Download model
    if download_model(model_name):
        if verify_model(model_name):
            print()
            print("=" * 60)
            print("[OK] Download complete!")
            print(f"   Model location: {MODELS_DIR / model_name}")
            print("   Next: Run local_qwen_inference.py to test")
            print("=" * 60)
            sys.exit(0)
    
    print()
    print("=" * 60)
    print("[ERROR] Download failed")
    print("Manual download instructions:")
    print(f"1. Visit: https://huggingface.co/{model_config['repo']}")
    print(f"2. Download: {model_config['file']}")
    print(f"3. Save to: {MODELS_DIR / model_name}")
    print("=" * 60)
    sys.exit(1)

if __name__ == "__main__":
    main()
