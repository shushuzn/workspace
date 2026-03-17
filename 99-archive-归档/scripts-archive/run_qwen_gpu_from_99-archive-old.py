#!/usr/bin/env python3
"""
使用 Intel Arc GPU 运行 Qwen3.5-2B

基于 OpenVINO 的 GPU 加速推理
"""

from openvino import Core
import time
from pathlib import Path


def check_model():
    """检查模型状态"""
    model_path = Path("D:/AI-Models/Qwen3.5-2B")
    
    print("="*60)
    print("Qwen3.5-2B GPU 推理")
    print("="*60)
    
    print(f"\n模型路径：{model_path}")
    
    if not model_path.exists():
        print(f"[ERROR] 模型不存在")
        return None
    
    # 检查 OpenVINO 格式
    xml_files = list(model_path.glob("*.xml"))
    if xml_files:
        print(f"OpenVINO 模型：{xml_files[0]}")
        return xml_files[0]
    else:
        print(f"[WARN] 未找到 OpenVINO 模型，需要转换")
        print(f"\n请运行:")
        print(f"  py convert_to_openvino.py {model_path}")
        return None


def load_to_gpu(model_xml: Path):
    """加载模型到 GPU"""
    
    print(f"\n加载模型到 Intel Arc GPU...")
    
    core = Core()
    
    # GPU 设备
    device = 'GPU'
    
    # 检查 GPU
    if device not in core.available_devices:
        print(f"[ERROR] GPU 不可用")
        print(f"可用设备：{core.available_devices}")
        return None
    
    # 获取 GPU 信息
    try:
        gpu_name = core.get_property(device, "FULL_DEVICE_NAME")
        print(f"GPU 设备：{gpu_name}")
    except:
        print(f"GPU 设备：{device}")
    
    # 加载模型
    start = time.time()
    try:
        compiled_model = core.compile_model(model_xml, device)
        load_time = time.time() - start
        print(f"加载完成，耗时：{load_time:.2f}秒")
        return compiled_model
    except Exception as e:
        print(f"[ERROR] 加载失败：{e}")
        return None


def simple_inference(compiled_model):
    """简单推理测试"""
    
    print(f"\n推理测试...")
    
    # 创建输入 (模拟 token IDs)
    import numpy as np
    
    # 输入：batch=1, seq_len=32
    input_ids = np.random.randint(1000, 10000, (1, 32)).astype(np.int32)
    
    # 推理
    start = time.time()
    try:
        output = compiled_model(input_ids)
        infer_time = time.time() - start
        
        print(f"推理完成")
        print(f"推理时间：{infer_time:.4f}秒")
        print(f"输出形状：{output[0].shape}")
        
        # 计算 tokens/秒
        tokens_per_sec = 32 / infer_time
        print(f"推理速度：{tokens_per_sec:.1f} tokens/秒")
        
        return True
    except Exception as e:
        print(f"[ERROR] 推理失败：{e}")
        return False


def main():
    """主函数"""
    
    # 1. 检查模型
    model_xml = check_model()
    if model_xml is None:
        print(f"\n需要先转换模型格式")
        return False
    
    # 2. 加载到 GPU
    compiled_model = load_to_gpu(model_xml)
    if compiled_model is None:
        return False
    
    # 3. 推理测试
    success = simple_inference(compiled_model)
    
    if success:
        print(f"\n✅ GPU 推理测试成功！")
        print(f"\n下一步:")
        print(f"  1. 集成到信号提取器")
        print(f"  2. 应用到自身对话")
        return True
    else:
        print(f"\n❌ 推理测试失败")
        return False


if __name__ == '__main__':
    import sys
    
    # 检查 Python 路径
    sys.path.insert(0, str(Path(__file__).parent))
    
    success = main()
    
    if success:
        print(f"\n🎉 Intel Arc GPU 运行 Qwen3.5-2B 成功！")
    else:
        print(f"\n需要进一步配置")
