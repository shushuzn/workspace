#!/usr/bin/env python3
"""
下载 CHGNet 预训练模型并转移到 D 盘
需要先设置 DGL 后端
"""
import os
import sys
from pathlib import Path
import shutil

print("=" * 70)
print("下载 CHGNet 预训练模型并转移到 D 盘")
print("=" * 70)

# 设置 DGL 后端 (必须先设置！)
print("\n[1/4] 设置 DGL 后端...")
try:
    import matgl
    matgl.set_backend('DGL')
    print("  [OK] DGL 后端设置成功")
except Exception as e:
    print(f"  [ERROR] DGL 后端设置失败：{e}")
    print(f"  [INFO] 请先安装 DGL:")
    print(f"    pip install dgl dglgo -f https://data.dgl.ai/wheels/repo.html")
    sys.exit(1)

# D 盘模型目录
d_models_dir = Path("D:/OpenClaw/workspace/research/models/pretrained/chgnet")
d_models_dir.mkdir(parents=True, exist_ok=True)

print(f"\n目标目录：{d_models_dir}")

# ============================================================================
# 2. 下载 CHGNet 模型
# ============================================================================
print("\n[2/4] 下载 CHGNet 模型...")

model_name = "CHGNet-MP-2024.2.13-PBE"

try:
    print(f"  正在下载：{model_name}...")
    print(f"  (首次下载会自动从 GitHub 获取，约 100-150 MB)")
    print(f"  这可能需要 5-10 分钟...")
    
    # 加载模型 (会自动下载)
    model = matgl.load_model(model_name)
    
    print(f"  [OK] 下载成功！")
    print(f"  模型已缓存到默认位置")
    
except Exception as e:
    print(f"  [ERROR] 下载失败：{e}")
    print(f"  请检查网络连接")
    sys.exit(1)

# ============================================================================
# 3. 找到并复制到 D 盘
# ============================================================================
print("\n[3/4] 复制模型到 D 盘...")

# C 盘缓存位置
c_cache = Path.home() / ".cache" / "matgl"

if c_cache.exists():
    print(f"  源目录：{c_cache}")
    
    # 列出所有文件
    files = list(c_cache.glob("**/*"))
    model_files = [f for f in files if f.is_file()]
    
    if model_files:
        print(f"  找到 {len(model_files)} 个文件:")
        for f in model_files:
            size_mb = f.stat().st_size / 1024 / 1024
            print(f"    - {f.relative_to(c_cache)} ({size_mb:.1f} MB)")
        
        # 复制到 D 盘
        print(f"\n  正在复制到 D 盘...")
        for f in model_files:
            rel_path = f.relative_to(c_cache)
            dest = d_models_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if not dest.exists():
                print(f"    复制：{rel_path}")
                shutil.copy2(f, dest)
        
        print(f"  [OK] 模型已复制到：{d_models_dir}")
        
        # 验证
        d_files = list(d_models_dir.glob("**/*"))
        d_model_files = [f for f in d_files if f.is_file()]
        
        total_size = sum(f.stat().st_size for f in d_model_files) / 1024 / 1024
        print(f"  总计：{len(d_model_files)} 个文件，{total_size:.1f} MB")
    else:
        print(f"  [WARN] 缓存目录为空")
else:
    print(f"  [WARN] 缓存目录不存在：{c_cache}")

# ============================================================================
# 4. 更新模型清单
# ============================================================================
print("\n[4/4] 更新模型清单...")

import json
from datetime import datetime

manifest_path = Path("D:/OpenClaw/workspace/research/models/pretrained/model_manifest.json")

if manifest_path.exists():
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
else:
    manifest = {}

# 更新 CHGNet 信息
manifest['models']['chgnet'] = {
    'model_name': model_name,
    'backend': 'DGL',
    'path': str(d_models_dir),
    'downloaded_at': datetime.now().isoformat(),
    'status': 'downloaded'
}

# 计算总大小
total_size = 0
for model_type in ['mace', 'chgnet']:
    model_dir = Path(manifest.get('models', {}).get(model_type, {}).get('path', ''))
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
print("[OK] CHGNet 下载完成！")
print("=" * 70)

print(f"\n模型位置:")
print(f"  C 盘缓存：{c_cache}")
print(f"  D 盘备份：{d_models_dir}")

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
