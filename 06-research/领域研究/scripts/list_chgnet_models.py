#!/usr/bin/env python3
"""
查找并下载正确的 CHGNet 模型
"""
import matgl
import requests
import json
from pathlib import Path

print("=" * 70)
print("查找可用的 CHGNet 模型")
print("=" * 70)

# 设置 DGL 后端
matgl.set_backend('DGL')

# 预训练模型基础 URL
base_url = matgl.utils.io.PRETRAINED_MODELS_BASE_URL
print(f"\n基础 URL: {base_url}")

# 尝试获取模型列表
print("\n尝试获取模型列表...")

# CHGNet GitHub 仓库的预训练模型目录
repo_url = "https://api.github.com/repos/materialsvirtuallab/matgl/contents/pretrained_models"

try:
    response = requests.get(repo_url, timeout=10)
    if response.status_code == 200:
        items = response.json()
        print(f"\n[OK] 找到 {len(items)} 个预训练模型目录:")
        
        chgnet_models = []
        for item in items:
            if item['type'] == 'dir' and 'CHGNet' in item['name']:
                chgnet_models.append(item['name'])
                print(f"  - {item['name']}")
        
        if chgnet_models:
            print(f"\n[OK] 可用 CHGNet 模型:")
            for model in chgnet_models:
                print(f"  - {model}")
            
            # 使用最新的模型
            latest_model = chgnet_models[0]  # 第一个通常是最新的
            print(f"\n使用模型：{latest_model}")
            
            # 尝试加载
            print(f"\n尝试加载：{latest_model}...")
            try:
                model = matgl.load_model(latest_model)
                print(f"[OK] 加载成功！")
            except Exception as e:
                print(f"[ERROR] 加载失败：{e}")
        else:
            print(f"[WARN] 未找到 CHGNet 模型")
    else:
        print(f"[ERROR] GitHub API 请求失败：{response.status_code}")
        print(f"  响应：{response.text[:200]}")
except Exception as e:
    print(f"[ERROR] 请求失败：{e}")
    print(f"\n[INFO] 常见 CHGNet 模型名称:")
    print(f"  - CHGNet-MP-2024.2.13-PBE")
    print(f"  - CHGNet-MP-2023.12.9-PBE")
    print(f"  - CHGNet-0.3.0")
    print(f"  - CHGNet-0.2.0")

print("\n" + "=" * 70)
