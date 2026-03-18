#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Ollama Qwen2.5 Local Inference Test
Usage: python ollama_qwen_test.py "Your prompt here"
"""

import subprocess
import sys
import json

OLLAMA_PATH = r"D:\Ollama\ollama.exe"
MODEL = "qwen3.5:0.8b"

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "--version"],
            capture_output=True, text=True, timeout=10
        )
        print(f"[OK] Ollama version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"[FAIL] Ollama not found: {e}")
        return False

def check_model():
    """Check if model is downloaded"""
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "list"],
            capture_output=True, text=True, timeout=10
        )
        if MODEL in result.stdout:
            print(f"[OK] Model found: {MODEL}")
            return True
        else:
            print(f"[WARN]  Model not found: {MODEL}")
            print("   Run: D:\\OpenClaw\\workspace\\30-scripts-tools\\download-qwen-model.bat")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking model: {e}")
        return False

def generate(prompt):
    """Generate response using Ollama"""
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", MODEL, prompt],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[WARN]  Timeout - model may still be downloading"
    except Exception as e:
        return f"[FAIL] Error: {e}"

def main():
    print("=" * 60)
    print("Ollama Qwen2.5 Local Inference Test")
    print("=" * 60)
    print()
    
    # Check Ollama
    if not check_ollama():
        sys.exit(1)
    
    # Check model
    model_ready = check_model()
    print()
    
    # Get prompt
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Hello! Introduce yourself in 2 sentences."
    
    print(f"Prompt: {prompt}")
    print("-" * 60)
    
    # Generate
    response = generate(prompt)
    print(response)
    print("-" * 60)
    
    if model_ready:
        print("[OK] Test complete!")
    else:
        print("[WARN]  Model not ready - download in progress")
        print("   Wait for download to complete, then run again")

if __name__ == "__main__":
    main()
