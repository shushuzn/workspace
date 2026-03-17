#!/usr/bin/env python3
"""下载小模型 Qwen2.5-0.5B"""

from huggingface_hub import snapshot_download
import os

model_name = "Qwen/Qwen2.5-0.5B"
save_path = "D:/AI-Models/Qwen2.5-0.5B"

print(f"下载模型：{model_name}")
print(f"保存路径：{save_path}")
print(f"模型大小：约 1GB")
print(f"预计时间：5-10 分钟 (取决于网速)")

os.makedirs(save_path, exist_ok=True)

try:
    snapshot_download(
        repo_id=model_name,
        local_dir=save_path,
        local_dir_use_symlinks=False,
    )
    print(f"\n✅ 下载完成！")
    print(f"模型路径：{save_path}")
except Exception as e:
    print(f"\n❌ 下载失败：{e}")
    print(f"\n请检查:")
    print(f"  1. 网络连接")
    print(f"  2. HuggingFace 访问权限")
    print(f"  3. 磁盘空间 (至少 2GB)")
