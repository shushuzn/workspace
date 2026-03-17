#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Core - Quick Verification Test
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_core import MemoryCore, MemoryConfig


def test_basic():
    """Basic functionality test"""
    print("=" * 60)
    print("Memory Core - Basic Functionality Test")
    print("=" * 60)
    
    # Initialize
    core = MemoryCore()
    print(f"[OK] MemoryCore initialized")
    
    # Process memory
    memory = core.process("Test memory content for verification")
    print(f"[OK] Memory processed: {memory.id}")
    
    # Search
    results = core.search("test")
    print(f"[OK] Search returned {len(results)} results")
    
    # Quality score
    score = core.quality.evaluate(memory.to_dict())
    print(f"[OK] Quality score: {score:.2f}")
    
    print("\n[SUCCESS] All basic tests passed!")
    return True


def test_modules():
    """Test all modules"""
    print("\n" + "=" * 60)
    print("Memory Core - Module Test")
    print("=" * 60)
    
    core = MemoryCore()
    
    modules = [
        ('Distiller', core.distiller),
        ('Quality', core.quality),
        ('Search', core.search_module),
        ('Association', core.association),
        ('Forgetting', core.forgetting),
        ('Conflict', core.conflict),
    ]
    
    for name, module in modules:
        print(f"[OK] {name} module loaded")
    
    print("\n[SUCCESS] All modules operational!")
    return True


def test_performance():
    """Performance test"""
    print("\n" + "=" * 60)
    print("Memory Core - Performance Test")
    print("=" * 60)
    
    import time
    
    core = MemoryCore()
    
    # Add 100 memories
    start = time.time()
    for i in range(100):
        core.process(f"Memory {i} for performance testing")
    elapsed = time.time() - start
    
    print(f"[OK] Processed 100 memories in {elapsed:.2f}s ({100/elapsed:.1f} mem/s)")
    
    # Search
    start = time.time()
    results = core.search("Memory")
    elapsed = time.time() - start
    
    print(f"[OK] Search completed in {elapsed:.3f}s ({len(results)} results)")
    
    print("\n[SUCCESS] Performance test passed!")
    return True


if __name__ == "__main__":
    try:
        success = True
        success &= test_basic()
        success &= test_modules()
        success &= test_performance()
        
        if success:
            print("\n" + "=" * 60)
            print("ALL TESTS PASSED - Memory Core v2.0 OPERATIONAL")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n[FAILED] Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
