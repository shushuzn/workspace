# 大文件管理指南

**版本:** v1.0 (2026-03-11)  
**用途:** 管理工作区大文件 (>5MB)

---

## 📊 当前大文件

| 文件 | 大小 | 用途 | 建议 |
|------|------|------|------|
| `lig-conductivity-prediction-zh.csv` | 53MB | CNT 数据集 | ✅ 保留 |
| `lig-conductivity-prediction.csv` | 53MB | CNT 数据集 | ✅ 保留 |
| `30-scripts/intentkit/` | 10MB | 测试数据 | ⚠️ 已归档 |
| `2401.00001.pdf` | 5.5MB | 论文 | ✅ 保留 |

---

## 🎯 管理策略

### 1. 数据集文件
- **位置:** `06-research/11-research/lig-conductivity-prediction-zenodo/`
- **大小:** 53MB × 2
- **用途:** CNT 导电性预测研究
- **建议:** 保留，研究核心数据

### 2. 论文 PDF
- **位置:** `06-research/10-ai-research/02-Models/_assets/`
- **大小:** ~5MB/个
- **用途:** 研究参考
- **建议:** 保留，学术资源

### 3. 归档数据
- **位置:** `99-archive/workspace/`
- **大小:** 36MB
- **用途:** 历史数据
- **建议:** 定期清理

---

## 🛠️ 清理建议

### 立即可清理
```powershell
# 清理 intentkit 测试数据 (已归档)
Remove-Item "30-scripts/intent-belief-integration/test_intentkit" -Recurse -Force
```

### 定期清理
```powershell
# 清理 Python 缓存
py 30-scripts/maintain.ps1 -CleanCache

# 清理临时文件
Get-ChildItem -Recurse -Include *.tmp,*.bak,*.log | Remove-Item
```

### Git LFS 建议
```bash
# 对大文件启用 Git LFS
git lfs track "*.csv"
git lfs track "*.pdf"
git lfs track "*.pkl"
```

---

## 📈 存储统计

| 类别 | 大小 | 占比 |
|------|------|------|
| 研究数据 | 167MB | 67% |
| 归档文件 | 37MB | 15% |
| 脚本工具 | 31MB | 12% |
| 数据收集 | 3MB | 1% |
| 其他 | 9MB | 5% |
| **总计** | **~247MB** | **100%** |

---

*最后更新：2026-03-11 | 版本 v1.0*
