#!/usr/bin/env python3
"""
导出高分辨率图表用于论文投稿

输出格式：TIFF (≥600 dpi) + PNG (≥300 dpi)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def export_prediction_figure(figures_dir='figures', dpi=600):
    """导出预测 vs 真实值图"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 示例数据 (实际应从模型输出读取)
    y_true = np.random.uniform(100, 50000, 40)
    y_pred = y_true * (1 + np.random.normal(0, 0.2, 40))
    
    ax.scatter(y_true, y_pred, alpha=0.6, edgecolors='k')
    ax.plot([y_true.min(), y_true.max()], 
            [y_true.min(), y_true.max()], 
            'r--', label='Ideal')
    ax.set_xlabel('True Conductivity (S/m)')
    ax.set_ylabel('Predicted Conductivity (S/m)')
    ax.set_title('Prediction vs True Values')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 保存
    out_path = Path(figures_dir) / 'prediction_figure'
    plt.savefig(f'{out_path}.tiff', dpi=dpi, bbox_inches='tight')
    plt.savefig(f'{out_path}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] prediction_figure.tiff ({dpi} dpi)")
    print(f"[OK] prediction_figure.png (300 dpi)")

def export_residuals_figure(figures_dir='figures', dpi=600):
    """导出残差分析图"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 示例数据
    y_pred = np.random.uniform(100, 50000, 40)
    residuals = np.random.normal(0, 500, 40)
    
    ax.scatter(y_pred, residuals, alpha=0.6, edgecolors='k')
    ax.axhline(y=0, color='r', linestyle='--')
    ax.set_xlabel('Predicted Conductivity (S/m)')
    ax.set_ylabel('Residuals (S/m)')
    ax.set_title('Residual Analysis')
    ax.grid(True, alpha=0.3)
    
    # 保存
    out_path = Path(figures_dir) / 'residuals_figure'
    plt.savefig(f'{out_path}.tiff', dpi=dpi, bbox_inches='tight')
    plt.savefig(f'{out_path}.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"[OK] residuals_figure.tiff ({dpi} dpi)")
    print(f"[OK] residuals_figure.png (300 dpi)")

def main():
    print("=" * 50)
    print("Export High-Resolution Figures")
    print("=" * 50)
    
    figures_dir = 'figures'
    Path(figures_dir).mkdir(exist_ok=True)
    
    export_prediction_figure(figures_dir)
    export_residuals_figure(figures_dir)
    
    print("=" * 50)
    print("All figures exported successfully!")
    print("=" * 50)

if __name__ == '__main__':
    main()
