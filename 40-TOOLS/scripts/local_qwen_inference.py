#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Local Qwen2.5 0.5B Inference Engine for Sensitive Content Processing
Zero cloud API calls - 100% local processing

Usage:
    python local_qwen_inference.py --prompt "Your sensitive content here"
    python local_qwen_inference.py --file sensitive_text.txt
    python local_qwen_inference.py --test
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Workspace root
WORKSPACE = Path(__file__).parent.parent
MODELS_DIR = WORKSPACE / "models"

# Ensure UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class LocalQwenInference:
    """Local Qwen2.5 0.5B inference engine"""
    
    def __init__(self, model_path: Optional[Path] = None):
        """Initialize local Qwen model"""
        self.model_path = model_path or self._find_model()
        self.model = None
        self.n_gpu_layers = 0  # CPU only by default
        
    def _find_model(self) -> Path:
        """Find GGUF model file"""
        # Try multiple model paths (priority: proven compatibility first)
        model_paths = [
            MODELS_DIR / "qwen2.5-1.5b",  # Qwen2.5-1.5B (proven compatibility)
            MODELS_DIR / "qwen2.5-0.5b-instruct",  # Qwen2.5-0.5B (legacy)
            MODELS_DIR / "qwen3.5-0.8b",  # Qwen3.5-0.8B (experimental)
        ]
        
        for model_path in model_paths:
            if model_path.exists():
                gguf_files = list(model_path.glob("*.gguf"))
                if gguf_files:
                    print(f"[OK] Model found: {model_path}")
                    return gguf_files[0]
        
        raise FileNotFoundError(
            f"Model not found. Please run download_qwen_model.py first.\n"
            f"Expected locations:\n"
            f"  - {MODELS_DIR / 'qwen2.5-1.5b'} (recommended)\n"
            f"  - {MODELS_DIR / 'qwen2.5-0.5b-instruct'}\n"
            f"  - {MODELS_DIR / 'qwen3.5-0.8b'} (experimental)"
        )
    
    def load_model(self, n_gpu_layers: int = 0):
        """Load model into memory"""
        try:
            from llama_cpp import Llama
            
            print(f"📦 Loading model: {self.model_path.name}")
            print(f"   Size: {self.model_path.stat().st_size / (1024**3):.2f} GB")
            
            self.model = Llama(
                model_path=str(self.model_path),
                n_ctx=2048,  # Context window
                n_batch=512,  # Batch size
                n_gpu_layers=n_gpu_layers,  # GPU offloading
                verbose=False
            )
            
            print(f"[OK] Model loaded successfully")
            return True
            
        except ImportError:
            print("[FAIL] llama-cpp-python not installed")
            print("   Install: pip install llama-cpp-python")
            print("   Or with BLAS: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
            return False
        except Exception as e:
            print(f"[FAIL] Failed to load model: {e}")
            return False
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generate response locally"""
        if self.model is None:
            if not self.load_model():
                return ""
        
        # Qwen instruction format
        formatted_prompt = f"<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        try:
            output = self.model(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|im_end|>", "</s>"]
            )
            
            return output["choices"][0]["text"].strip()
            
        except Exception as e:
            print(f"[FAIL] Inference failed: {e}")
            return ""
    
    def classify_sensitive(self, text: str) -> Dict[str, Any]:
        """Classify if content is sensitive and should be processed locally"""
        sensitive_keywords = [
            "密码", "password", "密钥", "secret", "token", "凭证", "credential",
            "私钥", "private key", "API 密钥", "API key", "访问令牌", "access token",
            "身份证", "ID card", "护照", "passport", "银行卡", "bank card",
            "医疗", "medical", "健康", "health", "诊断", "diagnosis",
            "财务", "financial", "收入", "income", "资产", "asset",
            "生物识别", "biometric", "指纹", "fingerprint", "面部", "face"
        ]
        
        is_sensitive = any(keyword in text.lower() for keyword in sensitive_keywords)
        
        return {
            "is_sensitive": is_sensitive,
            "confidence": 0.9 if is_sensitive else 0.1,
            "reason": "Contains sensitive keywords" if is_sensitive else "No sensitive content detected",
            "processing": "local" if is_sensitive else "cloud"
        }


def test_inference():
    """Test local inference"""
    print("=" * 60)
    print("Local Qwen Inference Test")
    print("=" * 60)
    print()
    
    inference = LocalQwenInference()
    
    if not inference.load_model():
        print("\n[FAIL] Test failed - model not loaded")
        return False
    
    # Test prompts
    test_prompts = [
        "什么是量子计算？",
        "Explain machine learning in simple terms.",
        "如何保护个人隐私数据？"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Test {i}/3]")
        print(f"Prompt: {prompt}")
        response = inference.generate(prompt, max_tokens=100)
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
    
    print("\n" + "=" * 60)
    print("[OK] Test complete - 100% local processing")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(description="Local Qwen Inference Engine")
    parser.add_argument("--prompt", type=str, help="Text to process locally")
    parser.add_argument("--file", type=str, help="File to process locally")
    parser.add_argument("--classify", type=str, help="Classify if text is sensitive")
    parser.add_argument("--test", action="store_true", help="Run test inference")
    parser.add_argument("--gpu", type=int, default=0, help="GPU layers to offload")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_inference()
        sys.exit(0 if success else 1)
    
    if args.classify:
        inference = LocalQwenInference()
        result = inference.classify_sensitive(args.classify)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[FAIL] File not found: {file_path}")
            sys.exit(1)
        text = file_path.read_text(encoding='utf-8')
        args.prompt = text
    
    if args.prompt:
        inference = LocalQwenInference()
        if not inference.load_model(n_gpu_layers=args.gpu):
            sys.exit(1)
        
        print("\n🔒 Local Processing (0% cloud API calls)")
        print("-" * 60)
        response = inference.generate(args.prompt)
        print(response)
        print("-" * 60)
        print("[OK] Complete - No data sent to cloud")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
