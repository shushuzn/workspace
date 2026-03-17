#!/usr/bin/env python3
"""
模型自动更新机制

功能：
1. 加载新实验数据
2. 合并到训练集
3. 重新训练模型
4. 评估性能提升
5. 保存新模型版本
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.model_selection import cross_val_score
import pickle
import json

def load_existing_data():
    """加载现有训练数据"""
    datasets = {
        'binary': '../cnt-lig-composite/data/cnt_lig_composite_dataset.csv',
        'ternary': '../cnt-lig-graphene-ternary/data/ternary_composite_dataset.csv',
        'quaternary': '../cnt-lig-graphene-mxene-quaternary/data/quaternary_composite_dataset.csv',
        'quinary': '../cnt-lig-graphene-mxene-pedot-quinary/data/quinary_composite_dataset.csv'
    }
    
    all_data = []
    for system, path in datasets.items():
        try:
            df = pd.read_csv(path)
            df['system'] = system
            all_data.append(df)
        except FileNotFoundError:
            pass
    
    if len(all_data) > 0:
        return pd.concat(all_data, ignore_index=True)
    return None

def load_new_experimental_data(data_path):
    """加载新实验数据"""
    df = pd.read_csv(data_path)
    return df

def retrain_model(existing_data, new_data):
    """重新训练模型"""
    # 合并数据
    if existing_data is not None:
        combined = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        combined = new_data
    
    print(f"  合并后样本数：{len(combined)}")
    
    # 特征工程
    feature_cols = ['cnt_ratio', 'lig_ratio', 'graphene_ratio', 'mxene_ratio', 'pedot_ratio']
    X = combined[feature_cols].values
    y = np.log10(combined['composite_conductivity'].values)
    
    # 处理 NaN
    mask = ~np.isnan(y)
    X = X[mask]
    y = y[mask]
    
    # 训练模型
    kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
    model = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5, random_state=42)
    model.fit(X, y)
    
    # 交叉验证
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
    
    return model, cv_scores.mean(), cv_scores.std()

def save_new_model(model, version, cv_r2_mean, cv_r2_std):
    """保存新模型"""
    models_dir = Path('../cnt-lig-deployment/package/cnt_materials_ml/models')
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / f"student_gp_v{version}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # 保存版本信息
    version_info = {
        'version': version,
        'date': pd.Timestamp.now().isoformat(),
        'cv_r2_mean': cv_r2_mean,
        'cv_r2_std': cv_r2_std,
        'training_samples': len(model.X_train_)
    }
    
    version_file = models_dir / "version_history.json"
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(version_info)
    
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print(f"  新模型已保存：v{version}")
    print(f"  CV R²: {cv_r2_mean:.4f} (+/- {cv_r2_std:.4f})")

if __name__ == "__main__":
    # 示例使用
    existing = load_existing_data()
    new = load_new_experimental_data('data/experimental_results.csv')
    
    model, cv_r2_mean, cv_r2_std = retrain_model(existing, new)
    save_new_model(model, version="2.0", cv_r2_mean=cv_r2_mean, cv_r2_std=cv_r2_std)
