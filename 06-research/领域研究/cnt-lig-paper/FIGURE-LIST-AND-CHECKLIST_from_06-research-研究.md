# 论文图表包 + 投稿清单

**论文标题:** Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4×  
**投稿期刊:** Nature Communications  
**创建日期:** 2026-03-11

---

## 📊 主要图表列表 (8 个)

### Figure 1: 研究路径图 (Graphical Abstract)

**内容:**
- 11 个研究方向完整闭环流程图
- 从预测→实验→反馈→更新
- 时间线：2 小时完成

**格式:**
- 尺寸：1200×800 px (300 dpi)
- 格式：PNG + SVG
- 颜色：Nature Communications 配色方案

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_1_Research_Pathway.svg
```

**制作工具:**
- BioRender / PowerPoint / Inkscape
- 参考：现有 45+ 可视化图表整合

---

### Figure 2: 电导率演进曲线

**内容:**
- 单一 CNT → 二元 → 三元 → 四元 → 五元 → LIG
- 电导率值标注
- 协同因子标注

**数据:**
```
单一 CNT: 6.99×10⁵ S/m
二元：4.35×10⁵ S/m (1.29×)
三元：5.86×10⁵ S/m (1.67×)
四元：8.61×10⁵ S/m (2.40×) ⭐
五元：7.26×10⁵ S/m (1.78×)
LIG: 1.76×10³ S/m
```

**格式:**
- 类型：折线图 + 柱状图组合
- 尺寸：800×600 px
- 颜色：渐变蓝色系

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_2_Conductivity_Evolution.png
```

---

### Figure 3: 协同效应分析

**内容:**
- 二元→五元协同因子对比
- 峰值标注 (四元 2.40×)
- 机制解释箭头

**数据:**
```
二元：1.29×
三元：1.67× (+29% vs 二元)
四元：2.40× (+44% vs 三元) ⭐
五元：1.78× (-26% vs 四元)
```

**格式:**
- 类型：柱状图 + 趋势线
- 尺寸：800×600 px
- 颜色：橙色系 (突出峰值)

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_3_Synergistic_Effect.png
```

---

### Figure 4: 特征重要性 (SHAP 分析)

**内容:**
- 11 特征 SHAP 值排序
- 前 5 特征详细标注
- 物理解释

**数据:**
```
1. diameter_nm: 68%
2. cvd_temperature_C: 27%
3. length_um: 12%
4. layers: 10%
5. aspect_ratio: 5%
...
```

**格式:**
- 类型：水平条形图
- 尺寸：800×600 px
- 颜色：蓝绿渐变

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_4_SHAP_Feature_Importance.png
```

---

### Figure 5: 逆向设计工作流程

**内容:**
- 正向预测：配方→性能
- 逆向设计：性能→配方
- 多目标优化：Pareto 前沿

**流程图:**
```
输入目标 → GP 模型 → 差分进化 → 推荐配方
   ↓                        ↑
   └────── 迭代优化 ─────────┘
```

**格式:**
- 类型：流程图
- 尺寸：1000×800 px
- 颜色：蓝色系

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_5_Inverse_Design_Workflow.png
```

---

### Figure 6: 主动学习推荐 Top20

**内容:**
- 1000 候选 UCB 分数分布
- Top20 推荐标注
- 实验优先级排序

**可视化:**
- 散点图 (UCB vs 预测值)
- Top20 高亮
- 气泡大小=置信度

**格式:**
- 类型：散点图 + 高亮
- 尺寸：1000×800 px
- 颜色：红黄蓝渐变

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_6_Active_Learning_Top20.png
```

---

### Figure 7: 模型蒸馏性能对比

**内容:**
- GP vs RF vs GB vs Ridge
- R²/推理速度/模型大小
- Pareto 前沿

**数据:**
```
GP: R²=0.85, 100ms, 2MB
RF: R²=0.83, 5ms, 500KB  ⭐
GB: R²=0.84, 20ms, 800KB
Ridge: R²=0.78, 1ms, 10KB
```

**格式:**
- 类型：雷达图 + 散点图
- 尺寸：800×800 px
- 颜色：四色区分

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_7_Model_Distillation_Comparison.png
```

---

### Figure 8: 实验验证平台架构

**内容:**
- 完整闭环流程图
- 6 步骤：预测→设计→筛选→实验→反馈→更新
- 自动化数据流

**流程图:**
```
预测模型 → 逆向设计 → 主动学习 → 实验 SOP
   ↑                                    ↓
   └──── 模型更新 ← 数据反馈 ←───────────┘
```

**格式:**
- 类型：系统架构图
- 尺寸：1200×800 px
- 颜色：蓝绿色系

**文件位置:**
```
11-research/cnt-lig-paper/figures/Figure_8_Experimental_Platform_Architecture.png
```

---

## 📋 投稿清单

### 1. 主文档

- [ ] **Manuscript** (Word/LaTeX)
  - 正文：12857 词
  - 格式：Nature Communications template
  - 文件：`manuscript.docx` / `manuscript.tex`

- [ ] **Abstract** (单独文件)
  - 250 词
  - 文件：`abstract.docx`

- [ ] **Cover Letter**
  - 投稿信
  - 强调创新性 (2.40×协同效应)
  - 文件：`cover_letter.docx`

---

### 2. 图表文件

- [ ] **Figure 1-8** (高分辨率)
  - 格式：TIFF/PNG (300 dpi)
  - 尺寸：符合期刊要求
  - 文件：`Figure_1.tif` ... `Figure_8.tif`

- [ ] **Figure Captions** (单独文件)
  - 每个图 200-300 词说明
  - 文件：`figure_captions.docx`

- [ ] **Supplementary Figures** (如有)
  - 额外图表
  - 文件：`Supplementary_Fig_S1.tif` ...

---

### 3. 数据文件

- [ ] **6 个数据集**
  - CNT: 533 样本
  - LIG: 200 样本
  - 二元：135 样本
  - 三元：153 样本
  - 四元：84 样本
  - 五元：35 样本
  - 格式：CSV + Excel
  - 文件：`Dataset_1_CNT.csv` ... `Dataset_6_Quinary.csv`

- [ ] **Data Dictionary**
  - 字段说明
  - 单位/格式
  - 文件：`data_dictionary.xlsx`

- [ ] **Data Availability Statement**
  - GitHub/Zenodo DOI
  - 文件：`data_availability.docx`

---

### 4. 代码文件

- [ ] **Python 包**
  - cnt-materials-ml v1.0.0
  - PyPI 链接
  - 文件：`code_repository.txt`

- [ ] **Jupyter Notebooks**
  - 关键分析复现
  - 文件：`Notebook_1_Data_Preprocessing.ipynb` ...

- [ ] **Code README**
  - 安装说明
  - 使用示例
  - 文件：`CODE_README.md`

---

### 5. 补充材料

- [ ] **Supplementary Note 1: Dataset Details**
  - 6 数据集详细说明
  - 文件：`Supplementary_Note_1.docx`

- [ ] **Supplementary Note 2: Model Performance**
  - 完整性能指标
  - 文件：`Supplementary_Note_2.docx`

- [ ] **Supplementary Note 3: Experimental SOPs**
  - 3 个标准化实验方案
  - 文件：`Supplementary_Note_3.docx`

- [ ] **Supplementary Note 4: Python Package Documentation**
  - API 参考
  - 文件：`Supplementary_Note_4.docx`

---

### 6. 作者信息

- [ ] **Author List**
  - 姓名 + 单位 + 邮箱
  - 文件：`author_list.docx`

- [ ] **Author Contributions**
  - CRediT taxonomy
  - 文件：`author_contributions.docx`

- [ ] **Competing Interests**
  - 利益冲突声明
  - 文件：`competing_interests.docx`

- [ ] **ORCID IDs**
  - 所有作者 ORCID
  - 文件：`orcid_list.docx`

---

### 7. 推荐审稿人

- [ ] **Reviewer Suggestions** (3-5 人)
  - 姓名 + 单位 + 邮箱
  - 无利益冲突声明
  - 文件：`reviewer_suggestions.docx`

**建议人选:**
1. Prof. James Tour (Rice University) - LIG 开创者
2. Prof. [CNT 专家] - CNT 领域权威
3. Prof. [ML+Materials] - 机器学习材料交叉领域

---

### 8. 投稿系统信息

- [ ] **Title** (150 字符以内)
  - "Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4×"

- [ ] **Running Title** (50 字符)
  - "ML-Guided CNT-LIG Composite Design"

- [ ] **Article Type**
  - Article (完整研究论文)

- [ ] **Subject Area**
  - Materials Science / Nanotechnology / Machine Learning

- [ ] **Keywords** (5-8 个)
  - carbon nanotube
  - laser-induced graphene
  - machine learning
  - composite materials
  - synergistic effect
  - inverse design
  - active learning

---

## 📅 投稿时间线

### Week 1 (2026-03-11 to 2026-03-18)

| 日期 | 任务 | 状态 |
|------|------|------|
| 2026-03-11 | 论文草稿完成 | ✅ 完成 |
| 2026-03-12 | 图表美化 (8 个) | 待开始 |
| 2026-03-13 | 合作者审阅 | 待开始 |
| 2026-03-14 | 补充材料整理 | 待开始 |
| 2026-03-15 | 投稿信撰写 | 待开始 |
| 2026-03-16 | 格式检查 | 待开始 |
| 2026-03-17 | 最终审阅 | 待开始 |
| 2026-03-18 | **投稿系统提交** | 待开始 |

### Week 2-4 (投稿后)

| 时间 | 预期状态 |
|------|----------|
| Week 2 | 编辑初审 (送审/拒稿) |
| Week 3-6 | 同行评审 (2-3 审稿人) |
| Week 7-8 | 审稿意见返回 |
| Week 9-10 | 修改回复 |
| Week 11-12 | 二审 (如需) |
| Week 13-16 | 接收/拒稿决定 |

---

## ✅ 投稿前检查清单

### 格式检查

- [ ] 字数符合要求 (Nature Comm: 正文<5000 词，本稿 12857 词需精简)
- [ ] 图表分辨率≥300 dpi
- [ ] 参考文献格式正确
- [ ] 单位使用 SI 制
- [ ] 缩写首次定义

### 内容检查

- [ ] 摘要 250 词以内
- [ ] 引言清晰阐述创新点
- [ ] 方法可复现
- [ ] 结果支持结论
- [ ] 讨论充分对比文献

### 伦理检查

- [ ] 无抄袭/剽窃
- [ ] 数据真实
- [ ] 作者署名无争议
- [ ] 利益冲突声明
- [ ] 动物/人类伦理 (如适用)

### 技术检查

- [ ] 所有文件已上传
- [ ] 文件格式正确
- [ ] 文件大小符合限制
- [ ] 补充材料完整
- [ ] 推荐审稿人无利益冲突

---

## 📧 投稿后跟进

### 编辑初审 (Week 1-2)

**可能结果:**
1. **送审** - 进入同行评审 (理想)
2. **拒稿** - 转投他刊 (备选：Science Advances, Advanced Materials)
3. **修改后重投** - 需补充数据/修改

**应对策略:**
- 送审：等待评审，准备回复
- 拒稿：根据编辑意见修改，转投
- 修改：快速补充，1 周内重投

### 同行评审 (Week 3-6)

**预期审稿人:**
- 2-3 位领域专家
- 评审周期：3-4 周

**可能意见:**
- 正面：接受/小修
- 中性：大修
- 负面：拒稿

**应对策略:**
- 正面：快速修改回复
- 中性：逐点回复，补充实验/数据
- 负面：申诉或转投

### 修改回复 (Week 7-10)

**回复要点:**
- 礼貌专业
- 逐点回复
- 标注修改位置
- 补充数据/实验 (如需要)
- 时间：2 周内完成

---

## 🎯 成功标准

### 短期 (投稿后 1 月)

- [ ] 通过初审，进入评审
- [ ] 收到审稿意见
- [ ] 完成修改回复

### 中期 (投稿后 3 月)

- [ ] 论文接收
- [ ] 在线发表
- [ ] 媒体宣传

### 长期 (发表后 1 年)

- [ ] 引用>100 次
- [ ] 会议邀请 2-3 次
- [ ] 合作机会 3-5 个

---

*创建时间：2026-03-11 14:56*  
*状态：投稿准备中*  
*目标投稿日期：2026-03-18*
