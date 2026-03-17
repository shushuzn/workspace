# 图表文件清理建议

**检查日期:** 2026-03-10

---

## 📊 文件统计

| 类型 | 数量 | 总大小 | 状态 |
|------|------|--------|------|
| PNG (小) | 16 个 | ~1.5 MB | ✅ 正常 |
| PNG (中文) | 5 个 | ~0.5 MB | ⚠️ 建议重命名 |
| TIFF (大) | 2 个 | **112 MB** | ❌ 建议移除 |

---

## ⚠️ 问题文件

### 大文件 (112 MB)
```
figures/prediction_figure.tiff      (56 MB)
figures/residuals_figure.tiff       (56 MB)
```

**问题:** GitHub 对单个文件限制为 100MB，接近限制可能导致显示问题

**建议:** 移除或添加到 `.gitignore`

---

### 中文文件名
```
figures/LIG_GP 准确性分布.png
figures/LIG_GP 优化效果对比.png
figures/LIG_GP 预测图.png
figures/LIG_GP_120 样本预测图.png
figures/LIG_GP_准确性分布_120 样本.png
```

**问题:** 可能导致跨平台兼容性问题

**建议:** 重命名为英文

---

## 🔧 清理步骤

### 1. 移除大 TIFF 文件
```bash
cd 11-research/lig-conductivity-prediction-zenodo
git rm figures/prediction_figure.tiff
git rm figures/residuals_figure.tiff
git commit -m "cleanup: 移除大尺寸 TIFF 文件"
git push
```

### 2. 更新.gitignore
```
# Large files
*.tiff
*.tif
```

### 3. 重命名中文文件 (可选)
```bash
git mv "figures/LIG_GP 预测图.png" "figures/LIG_GP_prediction.png"
```

---

## ✅ 当前 README 使用的图表

所有引用的图表都是 PNG 格式，大小正常：

| 图表 | 文件名 | 大小 |
|------|--------|------|
| 预测结果 | `GP_200samples_prediction.png` | 173 KB |
| 残差分析 | `GP_200samples_residuals.png` | 156 KB |
| 不确定性 | `GP_200samples_uncertainty.png` | 70 KB |
| 特征重要性 | `GP_feature_importance.png` | 69 KB |
| 模型对比 | `GP_performance_comparison.png` | 64 KB |

**总计:** ~532 KB ✅

---

*检查完成：2026-03-10*
