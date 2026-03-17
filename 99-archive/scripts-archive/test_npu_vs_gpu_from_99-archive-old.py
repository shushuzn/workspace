#!/usr/bin/env python3
"""
NPU vs GPU 性能对比测试

测试 Qwen3.5-2B 在 NPU 和 GPU 上的推理速度
"""

from openvino import Core
import time
import numpy as np
from pathlib import Path


def test_device_performance(device: str, model_path: str, num_runs: int = 5) -> dict:
    """
    测试设备性能
    
    Args:
        device: 设备类型 ('CPU', 'GPU', 'NPU')
        model_path: 模型路径
        num_runs: 测试次数
    
    Returns:
        性能测试结果
    """
    print(f"\n{'='*60}")
    print(f"测试设备：{device}")
    print(f"{'='*60}")
    
    core = Core()
    
    # 检查设备可用性
    if device not in core.available_devices:
        print(f"❌ {device} 不可用")
        return {'error': f'{device} not available'}
    
    # 获取设备信息
    try:
        device_name = core.get_property(device, "FULL_DEVICE_NAME")
        print(f"设备名称：{device_name}")
    except:
        device_name = device
        print(f"设备名称：{device}")
    
    # 检查模型
    model_dir = Path(model_path)
    if not model_dir.exists():
        print(f"[ERROR] 模型不存在：{model_dir}")
        return {'error': f'Model not found: {model_dir}'}
    
    # 查找 OpenVINO 模型
    xml_file = model_dir / "openvino_model.xml"
    if not xml_file.exists():
        # 尝试其他格式
        xml_file = list(model_dir.glob("*.xml"))
        if xml_file:
            xml_file = xml_file[0]
        else:
            print(f"[WARN] 未找到 OpenVINO 模型，需要转换")
            return {'error': 'Need to convert model'}
    
    print(f"模型文件：{xml_file}")
    
    # 加载并编译模型
    print(f"加载模型到 {device}...")
    start_load = time.time()
    try:
        compiled_model = core.compile_model(xml_file, device)
        load_time = time.time() - start_load
        print(f"✅ 加载完成，耗时：{load_time:.2f}秒")
    except Exception as e:
        print(f"❌ 加载失败：{e}")
        return {'error': str(e)}
    
    # 性能测试
    print(f"\n性能测试 ({num_runs} 次)...")
    
    # 创建虚拟输入 (模拟 token IDs)
    dummy_input = np.random.randint(100, 10000, (1, 64), dtype=np.int32)
    
    # 预热
    print("预热...")
    _ = compiled_model(dummy_input)
    
    # 正式测试
    times = []
    for i in range(num_runs):
        start = time.time()
        _ = compiled_model(dummy_input)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  第{i+1}次：{elapsed:.3f}秒")
    
    # 统计结果
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    result = {
        'device': device,
        'device_name': device_name,
        'model': str(model_dir),
        'load_time': load_time,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'num_runs': num_runs,
        'tokens_per_second': 64 / avg_time if avg_time > 0 else 0
    }
    
    # 打印结果
    print(f"\n{'='*60}")
    print(f"{device} 性能结果:")
    print(f"{'='*60}")
    print(f"平均推理时间：{avg_time:.3f}秒")
    print(f"最小推理时间：{min_time:.3f}秒")
    print(f"最大推理时间：{max_time:.3f}秒")
    print(f"推理速度：{result['tokens_per_second']:.1f} tokens/秒")
    print(f"加载时间：{load_time:.2f}秒")
    
    return result


def compare_devices(model_path: str):
    """对比多个设备"""
    print("="*60)
    print("NPU vs GPU vs CPU 性能对比测试")
    print("="*60)
    
    results = {}
    
    # 测试顺序：NPU → GPU → CPU
    devices = ['NPU', 'GPU', 'CPU']
    
    for device in devices:
        result = test_device_performance(device, model_path)
        if 'error' not in result:
            results[device] = result
    
    # 对比结果
    if len(results) >= 2:
        print(f"\n{'='*60}")
        print("性能对比总结")
        print(f"{'='*60}")
        
        # 按速度排序
        sorted_devices = sorted(
            results.keys(),
            key=lambda d: results[d]['avg_time']
        )
        
        print("\n推理速度排名 (从快到慢):")
        for i, device in enumerate(sorted_devices, 1):
            result = results[device]
            print(f"  {i}. {device}: {result['avg_time']:.3f}秒 ({result['tokens_per_second']:.1f} tokens/s)")
        
        # 最佳选择
        best_device = sorted_devices[0]
        print(f"\n🏆 推荐设备：{best_device}")
        print(f"   速度：{results[best_device]['tokens_per_second']:.1f} tokens/秒")
        
        # 速度提升
        if len(sorted_devices) >= 2:
            second_device = sorted_devices[1]
            speedup = results[second_device]['avg_time'] / results[best_device]['avg_time']
            print(f"   比第二快的 {second_device} 快 {speedup:.2f}x")
    
    return results


if __name__ == '__main__':
    import sys
    
    # 默认模型路径
    model_path = "D:/AI-Models/Qwen3.5-2B"
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    print(f"模型路径：{model_path}")
    
    # 开始测试
    results = compare_devices(model_path)
    
    print(f"\n测试完成！")
