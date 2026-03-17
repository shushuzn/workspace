#!/usr/bin/env python3
"""
LIG 电导率预测脚本

使用预训练的 GP 模型预测激光诱导石墨烯的电导率。

用法:
    python predict.py --E 10.0 --v 50.0 --co 1.0
    python predict.py --E 10.0 --v 50.0 --co 1.0 --plot
"""

import argparse
import joblib
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_model(model_dir='models'):
    """加载预训练模型"""
    model_path = Path(model_dir) / 'LIG_GP_200samples.pkl'
    scaler_X_path = Path(model_dir) / 'LIG_GP_scaler_X.pkl'
    scaler_y_path = Path(model_dir) / 'LIG_GP_scaler_y.pkl'
    
    model = joblib.load(model_path)
    scaler_X = joblib.load(scaler_X_path)
    scaler_y = joblib.load(scaler_y_path)
    
    return model, scaler_X, scaler_y

def predict(E, v, co, model, scaler_X, scaler_y):
    """预测电导率"""
    X = np.array([[E, v, co]])
    X_scaled = scaler_X.transform(X)
    
    y_pred, y_std = model.predict(X_scaled, return_std=True)
    
    y_pred_orig = scaler_y.inverse_transform(y_pred.reshape(-1, 1)).flatten()
    y_std_orig = y_std * scaler_y.scale_[0]
    
    return y_pred_orig[0], y_std_orig[0]

def main():
    parser = argparse.ArgumentParser(description='LIG 电导率预测')
    parser.add_argument('--E', type=float, required=True, help='激光能量密度 (J/cm²)')
    parser.add_argument('--v', type=float, required=True, help='扫描速度 (mm/s)')
    parser.add_argument('--co', type=float, default=1.0, help='CO₂ 激光比例 (0-1)')
    parser.add_argument('--plot', action='store_true', help='显示预测不确定性')
    parser.add_argument('--model-dir', type=str, default='models', help='模型目录')
    
    args = parser.parse_args()
    
    # 加载模型
    print("加载模型...")
    model, scaler_X, scaler_y = load_model(args.model_dir)
    
    # 预测
    print(f"\n输入参数:")
    print(f"  能量密度 (E): {args.E:.2f} J/cm²")
    print(f"  扫描速度 (v): {args.v:.2f} mm/s")
    print(f"  CO₂ 比例 (co): {args.co:.2f}")
    
    conductivity, uncertainty = predict(args.E, args.v, args.co, model, scaler_X, scaler_y)
    
    print(f"\n预测结果:")
    print(f"  电导率：{conductivity:.1f} S/m")
    print(f"  不确定性 (1σ): ±{uncertainty:.1f} S/m")
    print(f"  95% CI: [{conductivity - 1.96*uncertainty:.1f}, {conductivity + 1.96*uncertainty:.1f}] S/m")
    
    # 可视化
    if args.plot:
        plt.figure(figsize=(8, 6))
        
        # 生成不确定性曲线
        E_range = np.linspace(0.5, 50, 100)
        predictions = []
        uncertainties = []
        
        for E in E_range:
            pred, unc = predict(E, args.v, args.co, model, scaler_X, scaler_y)
            predictions.append(pred)
            uncertainties.append(unc)
        
        plt.plot(E_range, predictions, 'b-', label='预测')
        plt.fill_between(E_range, 
                         np.array(predictions) - 1.96*np.array(uncertainties),
                         np.array(predictions) + 1.96*np.array(uncertainties),
                         alpha=0.3, label='95% CI')
        plt.axvline(args.E, color='r', linestyle='--', label='当前参数')
        plt.scatter([args.E], [conductivity], color='r', s=100, zorder=5)
        
        plt.xlabel('能量密度 (J/cm²)')
        plt.ylabel('电导率 (S/m)')
        plt.title(f'LIG 电导率预测 (v={args.v:.1f} mm/s, co={args.co:.2f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    main()
