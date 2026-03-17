#!/usr/bin/env python3
"""
下载 CHGNet-MP-2024 预训练模型
"""
import urllib.request
import ssl
from pathlib import Path

# 忽略 SSL 证书验证
ssl._create_default_https_context = ssl._create_unverified_context

model_dir = Path("research/models/chgnet")
model_dir.mkdir(parents=True, exist_ok=True)

model_path = model_dir / "chgnet-mp-2024.pth"

if model_path.exists():
    print(f"[OK] Model already exists: {model_path}")
else:
    print(f"Downloading CHGNet-MP-2024 to {model_path}...")
    print(f"Size: ~100 MB")
    print(f"This may take 3-5 minutes...")
    
    try:
        # CHGNet 官方下载链接
        url = "https://github.com/CederGroupHub/chgnet/raw/main/pretrained_0.3.0.pth"
        urllib.request.urlretrieve(url, model_path)
        print(f"[OK] Download complete: {model_path}")
        print(f"Size: {model_path.stat().st_size / 1024 / 1024:.1f} MB")
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        print(f"Try alternative URL...")
        
        # 备用下载链接
        try:
            url2 = "https://huggingface.co/ceder/chgnet/resolve/main/chgnet_0.3.0.pth"
            urllib.request.urlretrieve(url2, model_path)
            print(f"[OK] Download complete from alternative: {model_path}")
        except Exception as e2:
            print(f"[ERROR] Alternative also failed: {e2}")
            print(f"Please download manually from:")
            print(f"  https://github.com/CederGroupHub/chgnet/tree/main")
