#!/usr/bin/env python3
"""
将 MACE 和 CHGNet 模型从 C 盘转移到 D 盘
并设置环境变量指向新位置
"""
import shutil
import os
from pathlib import Path
import json

print("=" * 70)
print("转移 MACE 和 CHGNet 模型到 D 盘")
print("=" * 70)

# D 盘模型目录
d_models_dir = Path("D:/OpenClaw/workspace/research/models/pretrained")
d_models_dir.mkdir(parents=True, exist_ok=True)

print(f"\n目标目录：{d_models_dir}")

# ============================================================================
# 1. 转移 MACE 模型
# ============================================================================
print("\n[1/3] 转移 MACE 模型...")

# C 盘 MACE 缓存位置
c_mace_cache = Path.home() / ".cache" / "mace"
d_mace_dir = d_models_dir / "mace"

if c_mace_cache.exists():
    print(f"  源目录：{c_mace_cache}")
    
    # 创建 D 盘目录
    d_mace_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制所有 MACE 模型文件
    mace_files = list(c_mace_cache.glob("*"))
    if mace_files:
        print(f"  找到 {len(mace_files)} 个文件")
        
        for f in mace_files:
            if f.is_file():
                dest = d_mace_dir / f.name
                print(f"  复制：{f.name} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
                shutil.copy2(f, dest)
        
        print(f"  [OK] MACE 模型已复制到：{d_mace_dir}")
        
        # 创建配置文件
        mace_config = {
            'model_path': str(d_mace_dir / mace_files[0].name),
            'original_cache': str(c_mace_cache),
            'transferred_at': '2026-03-06'
        }
        
        with open(d_mace_dir / "mace_config.json", 'w', encoding='utf-8') as f:
            json.dump(mace_config, f, indent=2, ensure_ascii=False)
        
        print(f"  [OK] 配置文件已保存：{d_mace_dir / 'mace_config.json'}")
    else:
        print(f"  [WARN] C 盘 MACE 缓存为空")
else:
    print(f"  [WARN] C 盘 MACE 缓存不存在：{c_mace_cache}")

# ============================================================================
# 2. 转移 CHGNet 模型
# ============================================================================
print("\n[2/3] 转移 CHGNet 模型...")

# C 盘 CHGNet 缓存位置
c_chgnet_cache = Path.home() / ".cache" / "matgl"
d_chgnet_dir = d_models_dir / "chgnet"

if c_chgnet_cache.exists():
    print(f"  源目录：{c_chgnet_cache}")
    
    # 创建 D 盘目录
    d_chgnet_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制所有 CHGNet 模型文件
    chgnet_files = list(c_chgnet_cache.glob("**/*"))
    if chgnet_files:
        print(f"  找到 {len(chgnet_files)} 个文件")
        
        for f in chgnet_files:
            if f.is_file():
                rel_path = f.relative_to(c_chgnet_cache)
                dest = d_chgnet_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                print(f"  复制：{rel_path} ({f.stat().st_size / 1024 / 1024:.1f} MB)")
                shutil.copy2(f, dest)
        
        print(f"  [OK] CHGNet 模型已复制到：{d_chgnet_dir}")
    else:
        print(f"  [WARN] C 盘 CHGNet 缓存为空")
else:
    print(f"  [WARN] C 盘 CHGNet 缓存不存在：{c_chgnet_cache}")

# ============================================================================
# 3. 设置环境变量
# ============================================================================
print("\n[3/3] 设置环境变量...")

# 创建 .env 文件
env_file = Path("D:/OpenClaw/workspace/research/.env")

env_content = f"""# MACE and CHGNet Model Paths
# Created: 2026-03-06

# MACE Model
MACE_CACHE_PATH={d_mace_dir}
MACE_MODEL_PATH={d_mace_dir / '20231210mace128L0_energy_epoch249model' if d_mace_dir.exists() else ''}

# CHGNet Model
MATGL_CACHE_PATH={d_chgnet_dir}

# Usage:
# Load these environment variables before running your scripts:
#   import os
#   os.environ['MACE_CACHE_PATH'] = '{d_mace_dir}'
#   os.environ['MATGL_CACHE_PATH'] = '{d_chgnet_dir}'
"""

with open(env_file, 'w', encoding='utf-8') as f:
    f.write(env_content)

print(f"  [OK] 环境变量配置已保存：{env_file}")

# 创建模型清单
model_manifest = {
    'transfer_date': '2026-03-06',
    'source': str(Path.home()),
    'destination': str(d_models_dir),
    'models': {
        'mace': {
            'path': str(d_mace_dir),
            'files': [f.name for f in d_mace_dir.glob("*") if f.is_file()]
        },
        'chgnet': {
            'path': str(d_chgnet_dir),
            'files': [str(f.relative_to(d_chgnet_dir)) for f in d_chgnet_dir.glob("**/*") if f.is_file()]
        }
    },
    'total_size_mb': sum(f.stat().st_size for f in d_models_dir.glob("**/*") if f.is_file()) / 1024 / 1024
}

manifest_path = d_models_dir / "model_manifest.json"
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(model_manifest, f, indent=2, ensure_ascii=False)

print(f"  [OK] 模型清单已保存：{manifest_path}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("[OK] 模型转移完成！")
print("=" * 70)

print(f"\n模型位置:")
print(f"  MACE: {d_mace_dir}")
print(f"  CHGNet: {d_chgnet_dir}")
print(f"  总大小：{model_manifest['total_size_mb']:.1f} MB")

print(f"\n使用方法:")
print(f"  1. 加载环境变量:")
print(f"     source {env_file}")
print(f"  2. 或在 Python 中设置:")
print(f"     import os")
print(f"     os.environ['MACE_CACHE_PATH'] = '{d_mace_dir}'")
print(f"     os.environ['MATGL_CACHE_PATH'] = '{d_chgnet_dir}'")

print(f"\n下一步:")
print(f"  1. 验证模型可用性")
print(f"  2. 运行迁移学习微调")
print(f"  3. 集成预测")

print("=" * 70)
