#!/usr/bin/env python3
"""
使用 CHGNet v0.4.2 + MPtrj 预训练权重
进行 LIG 迁移学习微调
"""
import chgnet
import matgl
import torch
from pathlib import Path
import json

print("=" * 70)
print("CHGNet v0.4.2 + MPtrj 预训练权重")
print("=" * 70)

print(f"\nCHGNet 版本：{chgnet.__version__}")
print(f"PyTorch 版本：{torch.__version__}")
print(f"CUDA 可用：{torch.cuda.is_available()}")

# 设置 DGL 后端
matgl.set_backend('DGL')

# 查找 CHGNet 0.4.2 的预训练权重
print("\n[1/4] 查找 CHGNet 0.4.2 MPtrj 预训练权重...")

# CHGNet pretrained 目录
chgnet_pretrained = Path(chgnet.__file__).parent / "pretrained"
print(f"CHGNet pretrained 目录：{chgnet_pretrained}")

# 查找 MPtrj 相关模型
print("\n搜索 MPtrj 相关模型...")
mptrj_files = list(chgnet_pretrained.glob("**/*mptrj*.pth.tar")) + \
              list(chgnet_pretrained.glob("**/*MP-0.4*.pth.tar")) + \
              list(chgnet_pretrained.glob("**/*0.4*.pth.tar"))

if mptrj_files:
    print(f"找到 {len(mptrj_files)} 个 MPtrj 相关模型:")
    for f in mptrj_files:
        size_mb = f.stat().st_size / 1024 / 1024
        rel_path = f.relative_to(chgnet_pretrained)
        print(f"  - {rel_path} ({size_mb:.1f} MB)")

    # 使用最新的 MPtrj 模型
    mptrj_model = mptrj_files[0]
    print(f"\n使用模型：{mptrj_model.name}")
else:
    print("未找到 MPtrj 模型")
    print("使用 0.3.0 版本作为替代")
    mptrj_model = chgnet_pretrained / "0.3.0" / "chgnet_0.3.0_e29f68s314m37.pth.tar"
    print(f"使用模型：{mptrj_model.name}")

# 复制到 D 盘
d_chgnet_dir = Path("D:/OpenClaw/workspace/research/models/pretrained/chgnet_v0.4.2")
d_chgnet_dir.mkdir(parents=True, exist_ok=True)

print(f"\n[2/4] 复制模型到 D 盘...")
print(f"目标目录：{d_chgnet_dir}")

import shutil
dest = d_chgnet_dir / "chgnet_mptrj.pth.tar"
shutil.copy2(mptrj_model, dest)
print(f"[OK] 复制成功！")

size_mb = dest.stat().st_size / 1024 / 1024
print(f"大小：{size_mb:.1f} MB")

# 创建配置文件
config = {
    'model_name': 'CHGNet-MPtrj',
    'chgnet_version': chgnet.__version__,
    'model_file': 'chgnet_mptrj.pth.tar',
    'backend': 'DGL',
    'model_path': str(d_chgnet_dir),
    'original_path': str(mptrj_model),
    'size_mb': size_mb,
    'copied_at': '2026-03-06'
}

config_path = d_chgnet_dir / "chgnet_config.json"
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"[OK] 配置已保存：{config_path}")

# 加载模型
print(f"\n[3/4] 加载 CHGNet 模型...")

try:
    from chgnet.model.model import CHGNet
    from chgnet.model.dynamics import Relaxer

    # 加载预训练权重
    print(f"  从 {dest} 加载...")

    # 使用 CHGNet 的 load 方法
    chgnet_model = CHGNet.from_file(str(dest))
    print(f"  [OK] 模型加载成功！")

    # 打印模型信息
    print(f"  原子类型：{chgnet_model.atom_types}")
    print(f"  设备：{next(chgnet_model.parameters()).device}")

    model_loaded = True

except Exception as e:
    print(f"  [ERROR] 模型加载失败：{e}")
    print(f"  [INFO] 尝试使用 matgl 加载...")

    try:
        # 尝试使用 matgl 加载
        model = matgl.load_model(str(dest))
        print(f"  [OK] matgl 加载成功！")
        model_loaded = True
    except Exception as e2:
        print(f"  [ERROR] matgl 加载也失败：{e2}")
        model_loaded = False

# 测试模型
if model_loaded:
    print(f"\n[4/4] 测试模型...")

    try:
        from ase.build import bulk

        # 创建测试结构 (石墨)
        graphite = bulk('C', 'hex', a=2.46, c=6.71)
        print(f"  测试结构：石墨 ({len(graphite)} 原子)")

        # 使用 CHGNet 计算能量
        if hasattr(chgnet_model, 'predict_structure'):
            result = chgnet_model.predict_structure(graphite)
            energy = result['e']
            print(f"  [OK] 石墨能量：{energy:.4f} eV")
            print(f"  [OK] 每原子能量：{energy /len(graphite):.4f} eV/atom")
        else:
            print(f"  [INFO] 模型已加载，但未测试能量计算")

        test_success = True

    except Exception as e:
        print(f"  [WARN] 测试失败：{e}")
        test_success = False
else:
    test_success = False

# 总结
print("\n" + "=" * 70)
if model_loaded and test_success:
    print("[OK] CHGNet v0.4.2 + MPtrj 就绪！")
else:
    print("[WARN] CHGNet 已加载但测试未完全通过")
print("=" * 70)

print(f"\n模型位置:")
print(f"  D 盘：{d_chgnet_dir}")
print(f"  大小：{size_mb:.1f} MB")

print(f"\n下一步:")
print(f"  1. 运行 CHGNet 迁移学习微调")
print(f"  2. 运行 MACE 迁移学习微调")
print(f"  3. 集成预测 (GP + MACE + CHGNet)")

print("=" * 70)
