#!/usr/bin/env python3
"""
下载 CHGNet 预训练模型到 D 盘
需要设置 DGL 后端
"""
import os
import sys
from pathlib import Path

print("=" * 70)
print("下载 CHGNet 预训练模型到 D 盘")
print("=" * 70)

# 设置 DGL 后端 (必须先设置！)
print("\n[0/4] 设置 DGL 后端...")
try:
    import matgl
    matgl.set_backend('DGL')
    print("  [OK] DGL 后端设置成功")
except Exception as e:
    print(f"  [ERROR] DGL 后端设置失败：{e}")
    print(f"  [INFO] 请先安装 DGL: pip install dgl dglgo -f https://data.dgl.ai/wheels/repo.html")
    sys.exit(1)

# D 盘模型目录
d_models_dir = Path("D:/OpenClaw/workspace/research/models/pretrained/chgnet")
d_models_dir.mkdir(parents=True, exist_ok=True)

print(f"\n目标目录：{d_models_dir}")

# ============================================================================
# 1. 尝试使用 matgl 下载模型
# ============================================================================
print("\n[1/4] 尝试使用 matgl 下载...")

model_names = [
    "CHGNet-MP-2024.2.13-PBE",
    "CHGNet-MP-2023.12.9-PBE", 
    "CHGNet-0.3.0",
]

downloaded_model = None

for model_name in model_names:
    try:
        print(f"  尝试下载：{model_name}...")
        model = matgl.load_model(model_name)
        print(f"  [OK] 下载成功：{model_name}")
        downloaded_model = model
        break
    except Exception as e:
        print(f"  [WARN] {model_name} 失败：{e}")

if downloaded_model:
    print(f"\n  [OK] CHGNet 模型已下载到默认缓存目录")
else:
    print(f"\n  [ERROR] 所有模型都下载失败")
    print(f"  [INFO] 尝试手动下载...")

# ============================================================================
# 2. 手动下载模型文件
# ============================================================================
print("\n[2/4] 手动下载模型文件...")

import urllib.request
import ssl
import json

# 忽略 SSL 证书验证
ssl._create_default_https_context = ssl._create_unverified_context

# CHGNet 模型文件列表
model_files = [
    {
        'name': 'model.pt',
        'url': 'https://github.com/CederGroupHub/chgnet/raw/main/pretrained_models/CHGNet-MP-2024.2.13-PBE/model.pt',
        'alt_url': 'https://huggingface.co/ceder/chgnet/resolve/main/model.pt'
    },
    {
        'name': 'state.pt',
        'url': 'https://github.com/CederGroupHub/chgnet/raw/main/pretrained_models/CHGNet-MP-2024.2.13-PBE/state.pt',
        'alt_url': 'https://huggingface.co/ceder/chgnet/resolve/main/state.pt'
    }
]

downloaded_files = []

for file_info in model_files:
    file_path = d_models_dir / file_info['name']
    
    if file_path.exists():
        print(f"  [OK] 已存在：{file_info['name']}")
        downloaded_files.append(file_info['name'])
        continue
    
    print(f"  下载：{file_info['name']}...")
    
    try:
        # 尝试主链接
        urllib.request.urlretrieve(file_info['url'], file_path)
        print(f"    [OK] 从主链接下载成功")
        downloaded_files.append(file_info['name'])
    except Exception as e:
        print(f"    [WARN] 主链接失败：{e}")
        
        try:
            # 尝试备用链接
            urllib.request.urlretrieve(file_info['alt_url'], file_path)
            print(f"    [OK] 从备用链接下载成功")
            downloaded_files.append(file_info['name'])
        except Exception as e2:
            print(f"    [ERROR] 备用链接也失败：{e2}")

# ============================================================================
# 3. 验证下载
# ============================================================================
print("\n[3/4] 验证下载...")

if downloaded_files:
    print(f"  [OK] 下载了 {len(downloaded_files)} 个文件:")
    for f in downloaded_files:
        file_path = d_models_dir / f
        size_mb = file_path.stat().st_size / 1024 / 1024
        print(f"    - {f} ({size_mb:.1f} MB)")
    
    # 创建配置文件
    chgnet_config = {
        'model_name': 'CHGNet-MP-2024.2.13-PBE',
        'backend': 'DGL',
        'model_path': str(d_models_dir),
        'files': downloaded_files,
        'downloaded_at': '2026-03-06'
    }
    
    config_path = d_models_dir / "chgnet_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(chgnet_config, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] 配置文件已保存：{config_path}")
else:
    print(f"  [ERROR] 没有成功下载任何文件")
    print(f"  [INFO] 请手动从以下地址下载:")
    print(f"    https://github.com/CederGroupHub/chgnet/tree/main/pretrained_models")

# ============================================================================
# 4. 更新模型清单
# ============================================================================
print("\n[4/4] 更新模型清单...")

manifest_path = Path("D:/OpenClaw/workspace/research/models/pretrained/model_manifest.json")

if manifest_path.exists():
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
else:
    manifest = {
        'transfer_date': '2026-03-06',
        'source': str(Path.home()),
        'destination': str(Path("D:/OpenClaw/workspace/research/models/pretrained")),
        'models': {}
    }

# 更新 CHGNet 信息
manifest['models']['chgnet'] = {
    'path': str(d_models_dir),
    'files': downloaded_files,
    'backend': 'DGL',
    'status': 'downloaded' if downloaded_files else 'failed'
}

# 计算总大小
total_size = 0
for model_type in ['mace', 'chgnet']:
    model_dir = Path(manifest['models'].get(model_type, {}).get('path', ''))
    if model_dir.exists():
        for f in model_dir.glob("**/*"):
            if f.is_file():
                total_size += f.stat().st_size

manifest['total_size_mb'] = total_size / 1024 / 1024

with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"  [OK] 模型清单已更新：{manifest_path}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
if downloaded_files:
    print("[OK] CHGNet 下载完成！")
else:
    print("[WARN] CHGNet 下载失败，请手动下载")
print("=" * 70)

print(f"\n模型位置:")
print(f"  MACE: D:\\OpenClaw\\workspace\\research\\models\\pretrained\\mace")
print(f"  CHGNet: D:\\OpenClaw\\workspace\\research\\models\\pretrained\\chgnet")

print(f"\n使用方法:")
print(f"  import matgl")
print(f"  matgl.set_backend('DGL')  # 必须先设置！")
print(f"  model = matgl.load_model('CHGNet-MP-2024.2.13-PBE')")

print(f"\n下一步:")
print(f"  1. 验证 CHGNet 模型可用性")
print(f"  2. 运行 MACE 迁移学习微调")
print(f"  3. 运行 CHGNet 迁移学习微调")
print(f"  4. 集成预测 (GP + MACE + CHGNet)")

print("=" * 70)
