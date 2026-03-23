#!/usr/bin/env python3
"""
查找 CHGNet 0.4.2 的正确模型名称
"""
import chgnet
import matgl
from pathlib import Path
import json

print("=" * 70)
print("查找 CHGNet 0.4.2 的正确模型名称")
print("=" * 70)

print(f"\nCHGNet 版本：{chgnet.__version__}")
print(f"MATGL 版本：{matgl.__version__}")

# 设置 DGL 后端
matgl.set_backend('DGL')

# 方法 1: 查看 chgnet 模块的预训练模型
print("\n[方法 1] 查看 chgnet 模块...")

try:
    import chgnet.model
    if hasattr(chgnet.model, 'MODELS'):
        print(f"  可用模型：{chgnet.model.MODELS}")
    else:
        print(f"  未找到 MODELS 属性")
except Exception as e:
    print(f"  [ERROR] {e}")

# 方法 2: 查看 matgl 的预训练模型 URL
print("\n[方法 2] 查看 matgl 预训练模型...")

try:
    base_url = matgl.utils.io.PRETRAINED_MODELS_BASE_URL
    print(f"  基础 URL: {base_url}")

    # 尝试获取 GitHub 内容
    import requests
    repo_url = base_url.replace('raw/', '')  # 转换为 GitHub URL

    # 尝试获取目录列表
    print(f"\n  尝试获取目录列表...")

    # 常见 CHGNet 模型名称 (CHGNet 0.4.2 可能使用)
    possible_models = [
        'CHGNet-MP-2024',
        'CHGNet-MP-2024-PBE',
        'CHGNet-0.4.2',
        'CHGNet-0.4.0',
        'CHGNet-MP-0.4.2',
        'CHGNet-MP',
        'CHGNet',
    ]

    print(f"\n  尝试加载可能的模型名称:")
    for model_name in possible_models:
        try:
            print(f"    尝试：{model_name}...", end=' ')
            model = matgl.load_model(model_name)
            print(f"[OK] 成功！")
            print(f"\n  [OK] 找到可用模型：{model_name}")

            # 保存到配置文件
            config = {
                'model_name': model_name,
                'chgnet_version': chgnet.__version__,
                'matgl_version': matgl.__version__,
                'backend': 'DGL'
            }

            config_path = Path("D:/OpenClaw/workspace/research/models/pretrained/chgnet/chgnet_config.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"  配置已保存：{config_path}")
            break

        except Exception as e:
            print(f"[FAIL] {str(e)[:50]}...")

    else:
        print(f"\n  [WARN] 所有尝试都失败了")
        print(f"  [INFO] 请查看 CHGNet 文档获取正确模型名称")

except Exception as e:
    print(f"  [ERROR] {e}")

# 方法 3: 查看 CHGNet 包内文件
print("\n[方法 3] 查看 CHGNet 包内容...")

try:
    chgnet_path = Path(chgnet.__file__).parent
    print(f"  CHGNet 路径：{chgnet_path}")

    # 查找配置文件或模型列表
    for pattern in ['*.json', '*.txt', '*.md', 'README*']:
        files = list(chgnet_path.glob(pattern))
        if files:
            print(f"  找到 {pattern}: {[f.name for f in files[:5]]}")

    # 查找 examples 或 pretrained 目录
    for subdir in ['examples', 'pretrained', 'models', 'configs']:
        subdir_path = chgnet_path / subdir
        if subdir_path.exists():
            print(f"  [OK] 找到 {subdir} 目录：{subdir_path}")

except Exception as e:
    print(f"  [ERROR] {e}")

# 方法 4: 使用 help 查看文档
print("\n[方法 4] 查看 load_model 文档...")

try:
    help_text = matgl.load_model.__doc__
    if help_text:
        # 查找示例
        import re
        examples = re.findall(r"load_model\(['\"]([^'\"]+)['\"]\)", help_text)
        if examples:
            print(f"  文档中的示例模型:")
            for ex in examples:
                print(f"    - {ex}")
        else:
            print(f"  未找到示例")
    else:
        print(f"  无文档")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 70)
print("查找完成！")
print("=" * 70)
