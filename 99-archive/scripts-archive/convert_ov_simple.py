#!/usr/bin/env python3
"""简单转换脚本 - 使用 ov_convert 命令行工具"""

import subprocess
import sys
from pathlib import Path

model_path = "D:/AI-Models/Qwen3.5-2B"
output_path = f"{model_path}/openvino_model"

print(f"模型路径：{model_path}")
print(f"输出路径：{output_path}")

# 使用 ov_convert 命令行工具
cmd = [
    sys.executable, "-m", "openvino.tools.ov_convert",
    model_path,
    "--output", output_path,
    "--compress_to_fp16"
]

print(f"\n执行命令：{' '.join(cmd)}")
print(f"\n预计时间：5-10 分钟")

try:
    subprocess.run(cmd, check=True)
    print(f"\n✅ 转换完成！")
    print(f"OpenVINO 模型：{output_path}")
except Exception as e:
    print(f"\n[ERROR] 转换失败：{e}")
    print(f"\n尝试手动安装:")
    print(f"  pip install optimum-intel openvino-tokenizers")
