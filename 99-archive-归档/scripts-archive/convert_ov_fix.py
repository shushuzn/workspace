#!/usr/bin/env python3
"""转换脚本 - 修复导入问题"""

from pathlib import Path
import sys

model_path = Path("D:/AI-Models/Qwen3.5-2B")
output_path = model_path / "openvino_model"

print(f"模型路径：{model_path}")
print(f"输出路径：{output_path}")

# 尝试不同的导入方式
try:
    from optimum.intel.openvino import OVModelForCausalLM
    print("导入成功：optimum.intel.openvino")
except ImportError as e:
    print(f"导入失败：{e}")
    try:
        from optimum.exporters.openvino import export_from_model
        print("导入成功：optimum.exporters.openvino")
    except ImportError as e2:
        print(f"导入失败：{e2}")
        print("\n尝试使用命令行工具...")
        
        import subprocess
        cmd = [
            sys.executable, "-m", "optimum.exporters.openvino",
            "--model", str(model_path),
            "--task", "text-generation",
            str(output_path)
        ]
        
        print(f"执行：{' '.join(cmd)}")
        subprocess.run(cmd)
        sys.exit(0)

# 加载并转换
print("\n加载模型...")
model = OVModelForCausalLM.from_pretrained(
    model_path,
    export=True,
    trust_remote_code=True,
)

print(f"\n保存到 {output_path}...")
model.save_pretrained(output_path)

print(f"\n✅ 转换完成！")
