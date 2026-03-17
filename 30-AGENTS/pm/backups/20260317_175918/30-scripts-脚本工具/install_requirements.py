#!/usr/bin/env python3
"""安装 Intel GPU 推理所需依赖"""

import subprocess
import sys

print("="*60)
print("安装 Intel GPU 推理依赖")
print("="*60)

packages = [
    'optimum-intel',
    'openvino-tokenizers',
    'transformers',
]

print(f"\n安装包：{packages}")
print(f"\n预计时间：10-20 分钟")
print(f"\n开始安装...\n")

for package in packages:
    print(f"安装 {package}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
        print(f"✅ {package} 安装成功")
    except Exception as e:
        print(f"❌ {package} 安装失败：{e}")

print(f"\n安装完成！")
print(f"\n下一步:")
print(f"  py convert_to_openvino.py D:/AI-Models/Qwen3.5-2B")
