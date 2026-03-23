#!/usr/bin/env python3
"""
LIG 稳定性预测模型训练脚本

功能:
- 加载稳定性数据集
- 特征工程
- 模型训练 (回归 + 分类)
- 模型评估
- 特征重要性分析

使用:
    python train_stability_model.py --data data/lig_stability.csv --output models/
"""

import argparse
import json
import pickle
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
import matplotlib.pyplot as plt


def load_data(data_path: str) -> pd.DataFrame:
    """加载数据集"""
    df = pd.read_csv(data_path)
    print(f"[OK] Loaded {len(df)} samples from {data_path}")
    return df


def preprocess_data(df: pd.DataFrame):
    """数据预处理"""
    # 处理缺失值
    df = df.dropna(subset=['change_percent'])  # 标签不能缺失

    # 特征工程
    df['energy_density'] = df['laser_power'] / df['scan_speed']  # 能量密度
    df['total_exposure'] = df['laser_power'] * df['scan_passes']  # 总曝光量

    # 稳定性评级
    def assign_grade(change):
        if change < 5:
            return 'A'
        elif change < 15:
            return 'B'
        elif change < 30:
            return 'C'
        else:
            return 'D'

    df['stability_grade'] = df['change_percent'].apply(assign_grade)

    print(f"[OK] Preprocessed {len(df)} samples")
    return df


def prepare_features(df: pd.DataFrame):
    """准备特征矩阵"""
    # 数值特征
    numerical_features = [
        'laser_power',
        'scan_speed',
        'scan_passes',
        'test_duration',
        'test_temperature',
        'energy_density',
        'total_exposure'
    ]

    # 类别特征
    categorical_features = [
        'laser_type',
        'precursor',
        'has_coating',
        'has_composite',
        'test_condition'
    ]

    # 编码类别特征
    df_encoded = pd.get_dummies(df, columns=categorical_features, drop_first=True)

    # 特征矩阵
    feature_cols = numerical_features + [
        col for col in df_encoded.columns
        if any(col.startswith(f) for f in categorical_features)
    ]

    X = df_encoded[feature_cols]
    y_reg = df_encoded['change_percent']  # 回归标签
    y_cls = df_encoded['stability_grade']  # 分类标签

    print(f"[OK] Prepared {X.shape[1]} features")
    return X, y_reg, y_cls, feature_cols


def train_regression_model(X, y, feature_names):
    """训练回归模型"""
    print("\n" + "=" * 60)
    print("Training Regression Model (Predicting Change %)")
    print("=" * 60)

    # 划分训练测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Random Forest 回归
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    # 交叉验证
    cv_scores = cross_val_score(
        model, X_train, y_train,
        cv=5,
        scoring='neg_mean_absolute_error'
    )

    # 训练
    model.fit(X_train, y_train)

    # 测试集评估
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"\nCross-Validation MAE: {-cv_scores.mean():.2f} (+/- {cv_scores.std():.2f})")
    print(f"Test Set MAE: {mae:.2f}%")

    # 特征重要性
    importances = model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)

    print("\nTop 10 Important Features:")
    print(feature_importance.head(10).to_string(index=False))

    return model, mae, feature_importance


def train_classification_model(X, y, feature_names):
    """训练分类模型"""
    print("\n" + "=" * 60)
    print("Training Classification Model (Predicting Stability Grade)")
    print("=" * 60)

    # 划分训练测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Random Forest 分类
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    # 交叉验证
    cv_scores = cross_val_score(
        model, X_train, y_train,
        cv=5,
        scoring='accuracy'
    )

    # 训练
    model.fit(X_train, y_train)

    # 测试集评估
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nCross-Validation Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    print(f"Test Set Accuracy: {accuracy:.3f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

    return model, accuracy


def save_models(reg_model, cls_model, feature_importance, output_dir: str):
    """保存模型"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 保存模型
    with open(output_path / 'rf_regressor.pkl', 'wb') as f:
        pickle.dump(reg_model, f)

    with open(output_path / 'rf_classifier.pkl', 'wb') as f:
        pickle.dump(cls_model, f)

    # 保存特征重要性
    feature_importance.to_csv(output_path / 'feature_importance.csv', index=False)

    print(f"\n[OK] Models saved to {output_dir}")


def plot_feature_importance(feature_importance, output_dir: str):
    """绘制特征重要性图"""
    plt.figure(figsize=(10, 8))
    top_features = feature_importance.head(15)

    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance')
    plt.title('Top 15 Features for LIG Stability Prediction')
    plt.gca().invert_yaxis()
    plt.tight_layout()

    plt.savefig(Path(output_dir) / 'feature_importance.png', dpi=300)
    print(f"[OK] Feature importance plot saved")


def main():
    parser = argparse.ArgumentParser(description="LIG Stability Model Training")
    parser.add_argument("--data", type=str, required=True,
                        help="Path to dataset CSV")
    parser.add_argument("--output", type=str, default="models/",
                        help="Output directory for models")
    parser.add_argument("--min-samples", type=int, default=30,
                        help="Minimum samples required for training")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("LIG Stability Prediction Model Training")
    print("=" * 60)
    print(f"Dataset: {args.data}")
    print(f"Output: {args.output}")
    print(f"Min Samples: {args.min_samples}")

    # 检查数据文件
    if not Path(args.data).exists():
        print(f"\n[ERROR] Dataset not found: {args.data}")
        print("\nNext Steps:")
        print("1. Collect stability data from literature")
        print("2. Create CSV file with required columns:")
        print("   - paper_id, laser_power, scan_speed, scan_passes")
        print("   - test_duration, test_condition, change_percent")
        print("   - has_coating, has_composite, etc.")
        print("\nSee: 11-research/LIG-Stability-ML-Framework.md")
        return 1

    # 加载数据
    df = load_data(args.data)

    # 检查样本量
    if len(df) < args.min_samples:
        print(f"\n[WARN] Only {len(df)} samples (need >= {args.min_samples})")
        print("Model training may be unreliable with limited data.")
        print("\nRecommendation: Collect more data before training.")

    # 预处理
    df = preprocess_data(df)

    # 准备特征
    X, y_reg, y_cls, feature_names = prepare_features(df)

    # 训练回归模型
    reg_model, reg_mae, feature_importance = train_regression_model(
        X, y_reg, feature_names
    )

    # 训练分类模型
    cls_model, cls_acc = train_classification_model(
        X, y_cls, feature_names
    )

    # 保存模型
    save_models(reg_model, cls_model, feature_importance, args.output)

    # 绘制特征重要性
    plot_feature_importance(feature_importance, args.output)

    # 生成训练报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'dataset': {
            'path': args.data,
            'samples': len(df),
            'features': len(feature_names)
        },
        'regression': {
            'mae': reg_mae,
            'model': 'RandomForestRegressor'
        },
        'classification': {
            'accuracy': cls_acc,
            'model': 'RandomForestClassifier'
        },
        'top_features': feature_importance.head(10).to_dict('records')
    }

    with open(Path(args.output) / 'training_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[OK] Training complete!")
    print(f"See: {args.output}/training_report.json")

    return 0


if __name__ == "__main__":
    exit(main())
