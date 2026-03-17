#!/usr/bin/env python3
"""
使用 CHGNet 本地预训练模型
并复制到 D 盘
"""
import chgnet
import matgl
from pathlib import Path
import shutil
import json

print("=" * 70)
print("使用 CHGNet 本地预训练模型")
print("=" * 70)

print(f"\nCHGNet 版本：{chgnet.__version__}")

# 设置 DGL 后端
matgl.set_backend('DGL')

# CHGNet pretrained 目录
chgnet_pretrained = Path(chgnet.__file__).parent / "pretrained"
print(f"\nCHGNet pretrained 目录：{chgnet_pretrained}")

# 列出所有模型
print(f"\n可用模型:")
model_files = list(chgnet_pretrained.glob("**/*.pth.tar"))
for f in model_files:
    size_mb = f.stat().st_size / 1024 / 1024
    rel_path = f.relative_to(chgnet_pretrained)
    print(f"  - {rel_path} ({size_mb:.1f} MB)")

# D 盘目标目录
d_chgnet_dir = Path("D:/OpenClaw/workspace/research/models/pretrained/chgnet")
d_chgnet_dir.mkdir(parents=True, exist_ok=True)

print(f"\n目标目录：{d_chgnet_dir}")

# 复制最新模型 (0.3.0)
print(f"\n[1/2] 复制最新模型 (0.3.0)...")

latest_model = chgnet_pretrained / "0.3.0" / "chgnet_0.3.0_e29f68s314m37.pth.tar"

if latest_model.exists():
    dest = d_chgnet_dir / "chgnet_0.3.0.pth.tar"
    print(f"  源文件：{latest_model.name}")
    print(f"  目标：{dest}")
    
    shutil.copy2(latest_model, dest)
    print(f"  [OK] 复制成功！")
    
    # 计算大小
    size_mb = dest.stat().st_size / 1024 / 1024
    print(f"  大小：{size_mb:.1f} MB")
else:
    print(f"  [WARN] 模型文件不存在：{latest_model}")

# 复制 README
readme = chgnet_pretrained / "0.3.0" / "README.md"
if readme.exists():
    shutil.copy2(readme, d_chgnet_dir / "README.md")
    print(f"  [OK] README 已复制")

# 创建配置文件
print(f"\n[2/2] 创建配置文件...")

config = {
    'model_name': 'chgnet_0.3.0',
    'model_file': 'chgnet_0.3.0_e29f68s314m37.pth.tar',
    'chgnet_version': chgnet.__version__,
    'backend': 'DGL',
    'model_path': str(d_chgnet_dir),
    'original_path': str(latest_model),
    'size_mb': size_mb,
    'copied_at': '2026-03-06'
}

config_path = d_chgnet_dir / "chgnet_config.json"
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"  [OK] 配置已保存：{config_path}")

# 更新模型清单
manifest_path = Path("D:/OpenClaw/workspace/research/models/pretrained/model_manifest.json")

if manifest_path.exists():
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
else:
    manifest = {}

manifest['models']['chgnet'] = {
    'model_name': 'chgnet_0.3.0',
    'model_file': 'chgnet_0.3.0_e29f68s314m37.pth.tar',
    'backend': 'DGL',
    'path': str(d_chgnet_dir),
    'size_mb': size_mb,
    'status': 'ready',
    'copied_at': '2026-03-06'
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

print(f"  [OK] 模型清单已更新")

# 总结
print("\n" + "=" * 70)
print("[OK] CHGNet 模型已就绪！")
print("=" * 70)

print(f"\n模型位置:")
print(f"  原始：{latest_model}")
print(f"  D 盘：{d_chgnet_dir}")
print(f"  大小：{size_mb:.1f} MB")

print(f"\n使用方法:")
print(f"  import chgnet")
print(f"  import matgl")
print(f"  matgl.set_backend('DGL')")
print(f"  # 使用本地模型文件加载")
print(f"  model_path = r'{d_chgnet_dir / 'chgnet_0.3.0.pth.tar'}'")
print(f"  # 具体加载方式参考 CHGNet 文档")

print(f"\n下一步:")
print(f"  1. 验证 CHGNet 模型可用性")
print(f"  2. 运行 MACE 迁移学习微调")
print(f"  3. 运行 CHGNet 迁移学习微调")
print(f"  4. 集成预测 (GP + MACE + CHGNet)")

print("=" * 70)
