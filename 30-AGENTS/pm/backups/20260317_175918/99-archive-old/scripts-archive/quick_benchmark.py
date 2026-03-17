#!/usr/bin/env python3
"""快速性能测试 - NPU vs GPU vs CPU"""

from openvino import Core
import time

print("="*60)
print("NPU vs GPU vs CPU 快速性能测试")
print("="*60)

core = Core()
devices = core.available_devices
print(f"可用设备：{devices}\n")

results = {}

for device in ['NPU', 'GPU', 'CPU']:
    if device not in devices:
        print(f"[SKIP] {device} 不可用")
        continue
    
    print(f"\n测试 {device}...")
    
    try:
        device_name = core.get_property(device, "FULL_DEVICE_NAME")
    except:
        device_name = device
    
    print(f"设备：{device_name}")
    
    # 简单计算测试
    import numpy as np
    
    # 创建测试数据
    size = 1000
    a = np.random.rand(size, size).astype(np.float32)
    b = np.random.rand(size, size).astype(np.float32)
    
    # 测试
    times = []
    for i in range(5):
        start = time.time()
        # 简单矩阵运算
        c = np.dot(a, b)
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    
    results[device] = {
        'name': device_name,
        'avg_time': avg_time
    }
    
    print(f"平均时间：{avg_time:.4f}秒\n")

# 对比
if len(results) >= 2:
    print("="*60)
    print("性能对比")
    print("="*60)
    
    sorted_devices = sorted(results.keys(), key=lambda d: results[d]['avg_time'])
    
    print("\n排名 (从快到慢):")
    for i, device in enumerate(sorted_devices, 1):
        r = results[device]
        print(f"  {i}. {device}: {r['avg_time']:.4f}秒")
    
    best = sorted_devices[0]
    print(f"\n推荐：{best}")

print("\n测试完成！")
