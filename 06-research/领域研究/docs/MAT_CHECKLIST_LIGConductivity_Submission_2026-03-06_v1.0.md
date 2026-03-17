# Carbon 期刊投稿检查清单

**论文标题:** Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression

**目标期刊:** Carbon (Elsevier)

**IF:** 11.3 | **Q1** | **出版商:** Elsevier

---

## 📋 投稿前检查清单

### 1. 论文文件

| 项目 | 要求 | 状态 | 备注 |
|------|------|------|------|
| 主文稿 | Word 或 LaTeX | ⏳ | 需转换 |
| 摘要 | 独立文件，~200 字 | ✅ | 已完成 |
| 图表 | 单独文件，300+ DPI | ✅ | 6 个 PNG，全部 300 DPI |
| 参考文献 | Carbon 格式 | ✅ | 33 篇，已转换 |
| 补充材料 | 可选 | ✅ | 数据集、代码链接 |

### 2. 作者信息

| 项目 | 状态 | 备注 |
|------|------|------|
| 作者姓名 | ⏳ 待填写 | 全部作者 |
| 作者单位 | ⏳ 待填写 | 完整机构名称 |
| 通信作者 | ⏳ 待填写 | 姓名 + 邮箱 |
| ORCID | ⏳ 待填写 | 建议所有作者 |
| 作者顺序 | ⏳ 待确认 | 第一作者、通信作者 |

### 3. 投稿信 (Cover Letter)

| 项目 | 状态 | 文件位置 |
|------|------|----------|
| Cover Letter 草稿 | ✅ 已准备 | `paper/cover_letter.md` |
| 填写作者信息 | ⏳ 待填写 | - |
| 填写单位信息 | ⏳ 待填写 | - |
| 推荐审稿人 | ⏳ 待填写 | 2-3 位（可选） |

### 4. 数据可用性

| 项目 | 状态 | 链接 |
|------|------|------|
| GitHub 仓库 | ✅ 已完成 | https://github.com/shushuzn/lig-conductivity-prediction |
| Zenodo DOI | ⏳ 待上传 | [待填写] |
| 数据声明 | ⏳ 待填写 | 论文中补充材料部分 |

### 5. 伦理与声明

| 项目 | 要求 | 状态 |
|------|------|------|
| 利益冲突 | 声明无或有 | ⏳ 待填写 |
| 资金资助 | 如有需声明 | ⏳ 待填写 |
| 作者贡献 | 可选 | ⏳ 待填写 |
| 数据可用性声明 | 必须 | ⏳ 待填写 |

---

## 📝 Carbon 期刊格式要求

### 文稿格式

| 要求 | 说明 |
|------|------|
| 语言 | English |
| 格式 | Word 或 LaTeX |
| 行距 | 双倍行距 |
| 字体 | 12pt, Times New Roman 或 Arial |
| 页边距 | 2.54 cm (1 inch) |
| 行号 | 建议添加（方便审稿） |

### 摘要要求

- **字数:** 200-250 字
- **结构:** 背景、方法、结果、结论
- **关键词:** 5-6 个

### 图表要求

| 类型 | 格式 | 分辨率 |
|------|------|--------|
| 彩色图 | TIFF, PNG, EPS | 300 DPI |
| 线条图 | TIFF, EPS | 600-1200 DPI |
| 组合图 | TIFF, PNG | 300 DPI |

**当前状态:** ✅ 全部 6 个图表均为 300 DPI PNG

### 参考文献格式

**Carbon 使用数字顺序编码制:**

```
[1] Author A, Author B. Title. Journal Name. Year;Volume(Issue):Pages.
```

**当前状态:** ✅ 33 篇已全部转换

---

## 🌐 投稿系统流程

### Elsevier Editorial Manager (EM)

1. **登录/注册:** https://www.editorialmanager.com/carbon/
2. **选择投稿类型:** Original Research Article
3. **上传文件:**
   - Manuscript (主文稿)
   - Figures (图表)
   - Supplementary Material (补充材料)
   - Cover Letter (投稿信)
4. **填写元数据:**
   - 标题
   - 作者信息
   - 摘要
   - 关键词
5. **确认并提交**

### 预计时间线

| 阶段 | 预计时间 |
|------|----------|
| 初审 (Editor check) | 1-3 天 |
| 送审 (Under review) | 2-4 周 |
| 审稿意见返回 | 4-8 周 |
| 修改 (如需) | 2-4 周 |
| 接受后出版 | 2-4 周 |

**总计:** 约 8-16 周

---

## ✅ 最终检查

投稿前最后确认：

- [ ] 论文全文通读（无拼写/语法错误）
- [ ] 图表引用正确（图 1-6 都在文中引用）
- [ ] 参考文献编号连续（[1]-[33]）
- [ ] 作者信息完整（姓名、单位、邮箱、ORCID）
- [ ] Cover Letter 填写完整
- [ ] Zenodo DOI 已获取并添加到论文
- [ ] GitHub 仓库公开可访问
- [ ] 所有文件已转换为 Word/LaTeX 格式
- [ ] 投稿系统账号已注册

---

## 📁 文件清单

投稿时需要准备的文件：

| 文件 | 格式 | 位置 |
|------|------|------|
| Manuscript | .docx 或 .tex | `ORGANIZED_PROJECT/01_Paper_Draft/` |
| Cover Letter | .docx 或 .pdf | `paper/cover_letter.md` (需转换) |
| Figure 1 | .png (300 DPI) | `figures/GP_performance_comparison.png` |
| Figure 2 | .png (300 DPI) | `figures/GP_200samples_prediction.png` |
| Figure 3 | .png (300 DPI) | `figures/GP_feature_importance.png` |
| Figure 4 | .png (300 DPI) | `figures/GP_200samples_residuals.png` |
| Figure 5 | .png (300 DPI) | `figures/GP_200samples_uncertainty.png` |
| Figure 6 | .png (300 DPI) | `figures/Ensemble_GP_MACE_prediction.png` |
| Highlights | .docx | 需创建（3-5 条） |
| Graphical Abstract | .png/.jpg | 需创建（可选） |

---

## 🎯 下一步行动

### 立即可做（无需用户输入）

- [ ] 创建 Highlights 文件
- [ ] 创建 Graphical Abstract 草稿
- [ ] 准备数据可用性声明模板

### 需要用户填写

- [ ] 作者姓名和单位
- [ ] 通信作者邮箱
- [ ] ORCID IDs
- [ ] Zenodo 上传获取 DOI
- [ ] 推荐审稿人（可选）

### 投稿当天

- [ ] 最终通读论文
- [ ] 转换 Word 格式
- [ ] 上传投稿系统
- [ ] 确认提交

---

*创建日期：2026-03-06*  
*最后更新：2026-03-06 19:30*
