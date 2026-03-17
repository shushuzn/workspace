# 研究脚本索引

**创建时间:** 2026-03-06 23:01  
**位置:** `11-research/scripts/`  
**总计:** 60+ Python 脚本

---

## 📊 GP 模型训练 (15 个)

### 核心脚本
- [[gp_run]] - GP 模型基础训练
- [[gp_optimization]] - GP 超参数优化
- [[gp_optimization_v2]] - GP 优化 V2
- [[train_gp]] - GP 训练简化版
- [[train_gp_log]] - GP 对数转换训练
- [[train_gp_optimized]] - GP 优化训练

### 特定数据集
- [[gp_complete_features]] - 完整特征 GP
- [[gp_no_collinearity]] - 无共线性 GP
- [[gp_retrain_200samples]] - 200 样本重训练
- [[lig_gp_optimized_120samples]] - 120 样本优化
- [[train_73samples]] - 73 样本训练

### 不确定性分析
- [[gp_uncertainty_plot]] - GP 不确定性可视化
- [[ensemble_learning]] - 集成学习
- [[ensemble_predict]] - 集成预测
- [[test_ensemble]] - 集成测试

---

## 🤖 机器学习模型 (10 个)

### Gradient Boosting
- [[train_gb_regularized]] - 正则化 GB 训练
- [[train_best_model]] - 最佳模型训练

### Random Forest
- [[train_rf]] - 随机森林训练

### 模型对比
- [[compare_models]] - 模型性能对比
- [[verify_and_test_models]] - 模型验证测试

### 特征工程
- [[analyze_features]] - 特征分析
- [[generate_feature_importance]] - 特征重要性生成
- [[lig_data_quality_check]] - 数据质量检查

---

## 🧠 深度学习 (15 个)

### CHGNet 模型
- [[chgnet_finetune]] - CHGNet 微调
- [[chgnet_lig_relax]] - CHGNet LIG 结构弛豫
- [[chgnet_test]] - CHGNet 测试
- [[chgnet_v042_mptrj]] - CHGNet v0.42 MPTraj
- [[download_chgnet]] - CHGNet 下载
- [[download_chgnet_to_d_drive]] - CHGNet 下载到 D 盘
- [[find_chgnet_model_name]] - CHGNet 模型名称查找
- [[list_chgnet_models]] - CHGNet 模型列表
- [[use_chgnet_local_model]] - 使用本地 CHGNet 模型

### MACE 模型
- [[mace_finetune]] - MACE 微调
- [[mace_lig_relax]] - MACE LIG 结构弛豫
- [[mace_test]] - MACE 测试
- [[download_mace]] - MACE 下载

### 模型安装
- [[install_models_via_pip]] - pip 安装模型
- [[transfer_models_to_d_drive]] - 模型迁移到 D 盘

---

## 📝 论文自动化 (10 个)

### 论文准备
- [[autonomous_paper_prep]] - 自动论文准备
- [[autonomous_paper_prep_v2]] - V2 版本
- [[autonomous_paper_prep_v3]] - V3 版本
- [[autonomous_paper_prep_v4]] - V4 版本

### 文献挖掘
- [[literature_mining]] - 文献挖掘
- [[literature_batch_extract]] - 批量文献提取
- [[literature_batch2_extract]] - 批次 2 提取
- [[literature_batch3_extract]] - 批次 3 提取
- [[literature_batch4_extract]] - 批次 4 提取
- [[literature_batch5_extract]] - 批次 5 提取

### 参考文献
- [[check_references_format]] - 参考文献格式检查
- [[convert_bibtex_to_carbon]] - BibTeX 转 Carbon 格式

---

## 📡 数据收集 (5 个)

### arXiv 监控
- [[arxiv_lig_monitor]] - arXiv LIG 监控

### 数据增强
- [[data_augmentation]] - 数据增强

### 在线学习
- [[online_learning]] - 在线学习

---

## 🚀 部署与提交 (5 个)

### GitHub 仓库
- [[setup_github_repo]] - GitHub 仓库设置
- [[package_submission]] - 投稿打包

### 可视化
- [[visualize_model]] - 模型可视化
- [[export_figures]] - 图表导出

### 预测工具
- [[predict]] - 预测脚本 (生产环境)

---

## 🔗 相关链接

### 项目文档
- [[../PROJECT_INDEX]] - 研究项目总索引
- [[../paper/README]] - LIG 论文项目
- [[../cnt-research/README]] - CNT 研究项目

### 数据与模型
- [[../data]] - 数据集目录
- [[../models]] - 模型文件目录
- [[../figures]] - 可视化图表目录

### 文档中心
- [[../../15-docs/LINK_INDEX]] - 内部链接索引
- [[../../15-docs/FOLDER-INDEX]] - 文件夹索引

### 记忆系统
- [[../../memory/2026-03-06]] - 今日记忆日志

---

## 📝 使用指南

### 快速开始
```bash
# GP 模型训练
py scripts/gp_run.py

# 预测
py scripts/predict.py

# 文献挖掘
py scripts/literature_mining.py
```

### 依赖安装
```bash
pip install scikit-learn pandas numpy matplotlib
pip install shap  # SHAP 分析
```

---

*最后更新:* 2026-03-06 23:08

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../PROJECT_INDEX]] - 研究项目总索引 (引用脚本目录)
- [[../../15-docs/LINK_INDEX]] - 内部链接总索引 (引用脚本统计)
- [[../../30-scripts/README]] - PowerShell 脚本索引 (姐妹索引)
- [[../../README]] - Workspace 导航首页 (通过项目索引间接引用)

**相关脚本:**
- [[gp_run]] - GP 训练 (被 PROJECT_INDEX 引用)
- [[predict]] - 预测工具 (被论文文档引用)
- [[autonomous_paper_prep]] - 论文自动化 (被投稿文档引用)

---
