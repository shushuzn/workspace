#!/usr/bin/env python3
"""
转换 HuggingFace 模型到 OpenVINO 格式

支持 Qwen3.5-2B 等模型
"""

import sys
from pathlib import Path


def convert_model(model_path: str, output_path: str = None):
    """转换模型到 OpenVINO"""
    
    model_dir = Path(model_path)
    if not model_dir.exists():
        print(f"[ERROR] 模型不存在：{model_dir}")
        return False
    
    if output_path is None:
        output_path = model_dir / "openvino_model"
    
    print(f"模型路径：{model_dir}")
    print(f"输出路径：{output_path}")
    
    try:
        from optimum.intel import OVModelForCausalLM
        
        print("\n加载并转换模型...")
        print("(首次转换需要 5-10 分钟)")
        
        # 加载并转换模型
        ov_model = OVModelForCausalLM.from_pretrained(
            model_dir,
            export=True,
            load_in_8bit=False,
            trust_remote_code=True,
        )
        
        # 保存
        print(f"\n保存到 {output_path}...")
        ov_model.save_pretrained(output_path)
        
        print(f"\n✅ 转换完成！")
        print(f"OpenVINO 模型路径：{output_path}")
        
        return True
        
    except ImportError as e:
        print(f"\n[ERROR] 缺少依赖：{e}")
        print("\n请安装:")
        print("  pip install optimum-intel openvino-tokenizers")
        return False
    
    except Exception as e:
        print(f"\n[ERROR] 转换失败：{e}")
        return False


if __name__ == '__main__':
    # 默认模型路径
    model_path = "D:/AI-Models/Qwen3.5-2B"
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    success = convert_model(model_path)
    
    if success:
        print(f"\n下一步：运行测试")
        print(f"  py test_npu_vs_gpu.py {model_path}")
    else:
        print(f"\n转换失败，请检查错误信息")
