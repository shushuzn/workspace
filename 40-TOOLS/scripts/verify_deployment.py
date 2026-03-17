#!/usr/bin/env python3
"""
Memory Core v2.0 部署验证脚本

验证所有功能正常工作
"""

import sys
import time
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

def verify():
    """验证部署"""
    print("=" * 60)
    print("Memory Core v2.0 部署验证")
    print("=" * 60)
    
    errors = []
    
    # 测试 1: 导入模块
    print("\n[1/8] 测试模块导入...")
    try:
        from memory_core import MemoryCore, MemoryConfig
        print("[OK] MemoryCore 导入成功")
    except Exception as e:
        errors.append(f"导入失败：{e}")
        print(f"[FAIL] 导入失败：{e}")
        return False
    
    # 测试 2: 初始化
    print("\n[2/8] 测试初始化...")
    try:
        core = MemoryCore()
        print(f"[OK] MemoryCore 初始化成功")
        print(f"  配置：{core.config.workspace}")
    except Exception as e:
        errors.append(f"初始化失败：{e}")
        print(f"[FAIL] 初始化失败：{e}")
        return False
    
    # 测试 3: 处理记忆
    print("\n[3/8] 测试处理记忆...")
    try:
        memory = core.process("测试记忆内容")
        print(f"[OK] 记忆处理成功")
        print(f"  ID: {memory.id}")
        print(f"  分数：{memory.score:.2f}")
    except Exception as e:
        errors.append(f"处理失败：{e}")
        print(f"[FAIL] 处理失败：{e}")
    
    # 测试 4: 搜索
    print("\n[4/8] 测试搜索...")
    try:
        results = core.search("测试", limit=5)
        print(f"[OK] 搜索成功")
        print(f"  结果数：{len(results)}")
    except Exception as e:
        errors.append(f"搜索失败：{e}")
        print(f"[FAIL] 搜索失败：{e}")
    
    # 测试 5: 批量处理
    print("\n[5/8] 测试批量处理...")
    try:
        memories = [f"批量测试 {i}" for i in range(10)]
        results = core.batch_process(memories, parallel=False)
        print(f"[OK] 批量处理成功")
        print(f"  处理数：{len(results)}")
    except Exception as e:
        errors.append(f"批量处理失败：{e}")
        print(f"[FAIL] 批量处理失败：{e}")
    
    # 测试 6: 统计
    print("\n[6/8] 测试统计...")
    try:
        stats = core.get_stats()
        print(f"[OK] 统计成功")
        print(f"  总数：{stats.get('total', 0)}")
        print(f"  平均分：{stats.get('avg_score', 0):.2f}")
    except Exception as e:
        errors.append(f"统计失败：{e}")
        print(f"[FAIL] 统计失败：{e}")
    
    # 测试 7: 缓存
    print("\n[7/8] 测试缓存...")
    try:
        if core.cache:
            stats = core.cache.get_stats()
            print(f"[OK] 缓存正常")
            print(f"  命中率：{stats.get('hit_rate', 'N/A')}")
        else:
            print(f"[WARN] 缓存未启用")
    except Exception as e:
        errors.append(f"缓存失败：{e}")
        print(f"[FAIL] 缓存失败：{e}")
    
    # 测试 8: 性能
    print("\n[8/8] 测试性能...")
    try:
        start = time.time()
        for i in range(20):
            core.process(f"性能测试 {i}")
        duration = time.time() - start
        avg_ms = duration / 20 * 1000
        print(f"[OK] 性能测试完成")
        print(f"  平均处理时间：{avg_ms:.2f}ms")
        
        if avg_ms < 50:
            print(f"  [OK] 性能达标 (<50ms)")
        else:
            print(f"  [WARN] 性能偏低 (>50ms)")
    except Exception as e:
        errors.append(f"性能测试失败：{e}")
        print(f"[FAIL] 性能测试失败：{e}")
    
    # 总结
    print("\n" + "=" * 60)
    if errors:
        print(f"[FAIL] 验证失败 - {len(errors)} 个错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("[OK] 验证完成 - 所有测试通过!")
        print("=" * 60)
        return True


if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)
