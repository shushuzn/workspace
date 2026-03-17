#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TIFF 转 PNG 压缩工具
将大尺寸 TIFF 文件转换为 PNG，节省磁盘空间
"""

import os
import sys
import io

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    from PIL import Image
except ImportError:
    print("❌ 需要安装 Pillow: pip install Pillow")
    sys.exit(1)

# 配置
FIGURES_DIR = r'D:\OpenClaw\workspace\06-research\领域研究\lig-conductivity-prediction-zenodo\figures'

def convert_tiff_to_png(tiff_path, png_path=None, quality=95):
    """转换 TIFF 为 PNG"""
    if png_path is None:
        base, _ = os.path.splitext(tiff_path)
        png_path = base + '.png'
    
    # 获取原始大小
    original_size = os.path.getsize(tiff_path)
    
    # 打开并转换
    img = Image.open(tiff_path)
    
    # 保存为 PNG（压缩）
    img.save(png_path, 'PNG', optimize=True)
    
    # 获取新大小
    new_size = os.path.getsize(png_path)
    saved = original_size - new_size
    saved_percent = (saved / original_size) * 100
    
    return {
        'tiff': tiff_path,
        'png': png_path,
        'original_mb': round(original_size / 1024 / 1024, 2),
        'new_mb': round(new_size / 1024 / 1024, 2),
        'saved_mb': round(saved / 1024 / 1024, 2),
        'saved_percent': round(saved_percent, 1)
    }

def main():
    print("🔍 扫描 TIFF 文件...")
    
    tiff_files = []
    for root, dirs, files in os.walk(FIGURES_DIR):
        for file in files:
            if file.lower().endswith('.tiff'):
                tiff_files.append(os.path.join(root, file))
    
    if not tiff_files:
        print("✅ 没有找到 TIFF 文件")
        return
    
    print(f"📊 找到 {len(tiff_files)} 个 TIFF 文件\n")
    
    results = []
    for tiff_path in tiff_files:
        print(f"转换：{os.path.basename(tiff_path)}")
        result = convert_tiff_to_png(tiff_path)
        results.append(result)
        print(f"  {result['original_mb']} MB → {result['new_mb']} MB (节省 {result['saved_percent']}%)\n")
    
    # 汇总
    total_original = sum(r['original_mb'] for r in results)
    total_saved = sum(r['saved_mb'] for r in results)
    
    print("=" * 60)
    print(f"✅ 完成：转换 {len(results)} 个文件")
    print(f"📊 原始：{total_original:.2f} MB")
    print(f"💾 节省：{total_saved:.2f} MB ({(total_saved/total_original)*100:.1f}%)")
    print("=" * 60)

if __name__ == '__main__':
    main()
