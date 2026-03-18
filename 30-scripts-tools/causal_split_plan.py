#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Causal Inference Engine - Module Split Plan

当前文件：causal_inference_engine.py (95.7KB, 2321 行)
目标：拆分为 5 个模块，每个<30KB

拆分方案:
==========

1. causal_core.py (核心引擎，~15KB)
   - CausalMethod 枚举
   - CausalEstimate 数据类
   - CausalGraph 数据类
   - Counterfactual 数据类
   - CausalInferenceEngine 主类框架
   - load_state(), save_state() 方法

2. causal_methods_did.py (DID 方法，~20KB)
   - difference_in_differences() 方法
   - 相关辅助函数

3. causal_methods_matching.py (匹配方法，~20KB)
   - propensity_score_matching() 方法
   - 相关辅助函数

4. causal_methods_iv.py (工具变量，~15KB)
   - instrumental_variables() 方法
   - 相关辅助函数

5. causal_methods_rdd.py (断点回归，~15KB)
   - regression_discontinuity() 方法
   - 相关辅助函数

6. causal_utils.py (工具函数，~10KB)
   - _normal_cdf()
   - _ols_simple()
   - _iv_estimate()
   - _calculate_cohens_d()
   - _power_analysis()
   - _create_effect_plot()
   - _interpret_effect()

7. causal_inference_engine.py (主入口，~5KB)
   - 导入所有模块
   - 暴露统一 API
   - main() 函数

总计：~100KB (拆分后更易维护)
"""

# 拆分执行脚本
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
BACKUP_DIR = SCRIPTS_DIR.parent / "99-backups" / "causal-split-20260318"

def create_backup():
    """Create backup"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    src = SCRIPTS_DIR / "causal_inference_engine.py"
    dst = BACKUP_DIR / "causal_inference_engine.py"
    
    if src.exists():
        import shutil
        shutil.copy2(src, dst)
        print(f"[OK] Backup created: {dst}")
    else:
        print(f"[ERROR] Source file not found: {src}")

if __name__ == "__main__":
    print("[Causal Split Plan] Causal Inference Engine ")
    print("=" * 60)
    create_backup()
    print("\nNext: Execute actual split")
