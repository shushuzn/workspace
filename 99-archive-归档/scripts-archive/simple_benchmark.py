#!/usr/bin/env python3
"""
简单性能测试 - 测试 OpenVINO 在 NPU/GPU/CPU 上的性能

使用虚拟模型测试设备性能
"""

from openvino import Core
import time
import numpy as np


def benchmark_device(device: str, num_runs: int = 10) -> dict:
    """测试设备性能"""
    
    print(f"\n{'='*60}")
    print(f"测试设备：{device}")
    print(f"{'='*60}")
    
    core = Core()
    
    # 检查设备
    if device not in core.available_devices:
        print(f"[ERROR] {device} 不可用")
        return {'error': f'{device} not available'}
    
    # 获取设备信息
    try:
        device_name = core.get_property(device, "FULL_DEVICE_NAME")
    except:
        device_name = device
    
    print(f"设备：{device_name}")
    
    # 创建简单模型 (用于测试)
    print(f"\n创建测试模型...")
    
    # 使用 OpenVINO 创建简单神经网络
    from openvino.runtime import opset11 as opset
    from openvino.runtime import Model, PartialShape
    
    # 输入：batch=1, seq_len=64, hidden=512
    input1 = opset.parameter([1, 64, 512], name="input1")
    input2 = opset.parameter([512, 512], name="weight")
    
    # 矩阵乘法
    matmul = opset.matmul(input1, input2, False, True)
    
    # 创建模型
    model = Model([matmul], [input1, input2], "TestModel")
    
    # 编译到设备
    print(f"编译到 {device}...")
    start_compile = time.time()
    compiled_model = core.compile_model(model, device)
    compile_time = time.time() - start_compile
    print(f"编译完成，耗时：{compile_time:.2f}秒")
    
    # 性能测试
    print(f"\n性能测试 ({num_runs} 次)...")
    
    # 创建输入数据
    input_data_1 = np.random.rand(1, 64, 512).astype(np.float32)
    input_data_2 = np.random.rand(512, 512).astype(np.float32)
    
    # 预热
    _ = compiled_model([input_data_1, input_data_2])
    
    # 正式测试
    times = []
    for i in range(num_runs):
        start = time.time()
        _ = compiled_model([input_data_1, input_data_2])
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  第{i+1}次：{elapsed:.4f}秒")
    
    # 统计
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    result = {
        'device': device,
        'device_name': device_name,
        'compile_time': compile_time,
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'inferences_per_second': 1 / avg_time if avg_time > 0 else 0
    }
    
    # 打印结果
    print(f"\n{'='*60}")
    print(f"{device} 性能结果:")
    print(f"{'='*60}")
    print(f"平均推理时间：{avg_time:.4f}秒")
    print(f"推理速度：{result['inferences_per_second']:.1f} 次/秒")
    print(f"编译时间：{compile_time:.2f}秒")
    
    return result


def compare_all_devices():
    """对比所有设备"""
    
    print("="*60)
    print("NPU vs GPU vs CPU 性能对比")
    print("="*60)
    
    core = Core()
    devices = core.available_devices
    
    print(f"可用设备：{devices}")
    
    results = {}
    
    # 测试每个设备
    for device in ['NPU', 'GPU', 'CPU']:
        if device in devices:
            result = benchmark_device(device)
            if 'error' not in result:
                results[device] = result
    
    # 对比
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
            print(f"  {i}. {device}: {result['avg_time']:.4f}秒 ({result['inferences_per_second']:.1f} 次/秒)")
        
        # 最佳选择
        best_device = sorted_devices[0]
        print(f"\n🏆 推荐设备：{best_device}")
        
        # 速度提升
        if len(sorted_devices) >= 2:
            second_device = sorted_devices[1]
            speedup = results[second_device]['avg_time'] / results[best_device]['avg_time']
            print(f"   比第二快的 {second_device} 快 {speedup:.2f}x")
    
    return results


if __name__ == '__main__':
    results = compare_all_devices()
    print(f"\n测试完成！")
