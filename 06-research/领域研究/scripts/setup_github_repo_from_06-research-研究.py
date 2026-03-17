#!/usr/bin/env python3
"""
准备 GitHub 仓库文件结构

创建 lig-conductivity-prediction 仓库所需的所有文件。
"""

import shutil
from pathlib import Path

def setup_github_repo(repo_dir='github_repo'):
    """准备 GitHub 仓库"""
    
    # 创建仓库目录
    repo_path = Path(repo_dir)
    if repo_path.exists():
        shutil.rmtree(repo_path)
    repo_path.mkdir(parents=True)
    
    print("=" * 50)
    print("Setting up GitHub Repository")
    print("=" * 50)
    
    # 创建子目录
    (repo_path / 'data').mkdir()
    (repo_path / 'models').mkdir()
    (repo_path / 'scripts').mkdir()
    (repo_path / 'notebooks').mkdir()
    (repo_path / 'figures').mkdir()
    
    # 复制文件
    print("\nCopying files...")
    
    # README
    shutil.copy('../11-research/README.md', repo_path / 'README.md')
    print("  [OK] README.md")
    
    # LICENSE
    shutil.copy('../11-research/scripts/LICENSE', repo_path / 'LICENSE')
    print("  [OK] LICENSE")
    
    # requirements.txt
    shutil.copy('../11-research/scripts/requirements.txt', repo_path / 'requirements.txt')
    print("  [OK] requirements.txt")
    
    # 数据
    shutil.copy('../11-research/data/lig_dataset_200.csv', repo_path / 'data' / 'lig_dataset_200.csv')
    shutil.copy('../11-research/data/README.md', repo_path / 'data' / 'README.md')
    print("  [OK] data/")
    
    # 模型
    for f in ['LIG_GP_200samples.pkl', 'LIG_GP_scaler_X.pkl', 'LIG_GP_scaler_y.pkl', 'LIG_GP_200samples_config.json']:
        shutil.copy(f'../11-research/models/{f}', repo_path / 'models' / f)
    shutil.copy('../11-research/models/model_card.md', repo_path / 'models' / 'model_card.md')
    print("  [OK] models/")
    
    # 脚本
    for f in ['predict.py', 'gp_run.py', 'gp_retrain_200samples.py']:
        src = Path(f'../11-research/scripts/{f}')
        if src.exists():
            shutil.copy(src, repo_path / 'scripts' / f)
    print("  [OK] scripts/")
    
    # 图表
    for f in ['prediction_figure.tiff', 'prediction_figure.png', 'residuals_figure.tiff', 'residuals_figure.png']:
        src = Path(f'figures/{f}')
        if src.exists():
            shutil.copy(src, repo_path / 'figures' / f)
    print("  [OK] figures/")
    
    # 创建笔记本教程
    print("\nCreating tutorial notebook...")
    notebook_content = """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# LIG Conductivity Prediction Tutorial\\n\\nThis notebook demonstrates how to use the pre-trained GP model to predict LIG conductivity."]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": ["import joblib\\nimport numpy as np\\n\\n# Load model\\nmodel = joblib.load('models/LIG_GP_200samples.pkl')\\nscaler_X = joblib.load('models/LIG_GP_scaler_X.pkl')\\nscaler_y = joblib.load('models/LIG_GP_scaler_y.pkl')"]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": ["# Predict\\nX_new = np.array([[10.0, 50.0, 1.0]])  # E, v, co\\nX_scaled = scaler_X.transform(X_new)\\ny_pred, y_std = model.predict(X_scaled, return_std=True)\\nprint(f'Predicted conductivity: {y_pred[0]:.1f} ± {y_std[0]:.1f} S/m')]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 4
}
"""
    (repo_path / 'notebooks' / 'tutorial.ipynb').write_text(notebook_content)
    print("  [OK] notebooks/tutorial.ipynb")
    
    print("\n" + "=" * 50)
    print(f"Repository prepared: {repo_path.absolute()}")
    print("=" * 50)
    
    print("\nNext steps:")
    print("1. Create GitHub repository: lig-conductivity-prediction")
    print("2. Initialize git in the repo directory")
    print("3. Add remote and push")
    
    return repo_path

if __name__ == '__main__':
    setup_github_repo()
