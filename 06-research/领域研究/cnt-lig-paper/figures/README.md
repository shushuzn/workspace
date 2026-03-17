# 论文图表制作指南

**论文标题:** Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4×  
**目标期刊:** Nature Communications  
**图表数量:** 8 个主图 + 补充图

---

## 📊 主图列表

### Figure 1: Graphical Abstract (研究路径图)

**尺寸:** 1200×800 px (300 dpi)  
**格式:** TIFF + SVG  
**内容:** 11 方向完整闭环流程图

**制作工具:**
- BioRender (推荐)
- PowerPoint + Inkscape
- Adobe Illustrator

**配色方案:**
- 主色：#2E86AB (蓝色)
- 辅色：#A23B72 (紫色)
- 强调：#F18F01 (橙色)

**参考布局:**
```
┌─────────────────────────────────────────────┐
│  预测 → 对比 → 图谱 → 复合 → 逆向 → 主动    │
│    ↓                                  ↑    │
│    └─── 蒸馏 → 部署 → 实验 → 反馈 ────┘    │
│                                             │
│  [核心数据标注]                              │
│  - 1000+ 样本                                │
│  - 10 模型 R²>0.75                           │
│  - 协同峰值 2.40×                            │
└─────────────────────────────────────────────┘
```

**文件:** `Figure_1_Graphical_Abstract.tif`

---

### Figure 2: 电导率演进曲线

**尺寸:** 800×600 px (300 dpi)  
**类型:** 柱状图 + 折线图组合  
**数据:**

| 体系 | 电导率 (S/m) | 协同因子 |
|------|--------------|----------|
| 单一 CNT | 6.99×10⁵ | - |
| 二元 | 4.35×10⁵ | 1.29× |
| 三元 | 5.86×10⁵ | 1.67× |
| 四元 | 8.61×10⁵ | 2.40× ⭐ |
| 五元 | 7.26×10⁵ | 1.78× |
| LIG | 1.76×10³ | - |

**制作要点:**
- 左 Y 轴：电导率 (对数刻度)
- 右 Y 轴：协同因子 (线性)
- 四元体系用橙色高亮
- 误差棒标注标准差

**文件:** `Figure_2_Conductivity_Evolution.tif`

---

### Figure 3: 协同效应分析

**尺寸:** 800×600 px (300 dpi)  
**类型:** 柱状图 + 趋势线  
**数据:** 二元→五元协同因子

**制作要点:**
- 柱状图显示协同因子
- 趋势线连接各点
- 四元峰值用星号标注
- 箭头标注关键机制

**文件:** `Figure_3_Synergistic_Effect.tif`

---

### Figure 4: SHAP 特征重要性

**尺寸:** 800×600 px (300 dpi)  
**类型:** 水平条形图  
**数据:**

| 特征 | 重要性 |
|------|--------|
| diameter_nm | 68% |
| cvd_temperature_C | 27% |
| length_um | 12% |
| layers | 10% |
| aspect_ratio | 5% |

**制作要点:**
- 前 5 特征详细标注
- 颜色渐变 (深蓝→浅蓝)
- 右侧添加物理解释

**文件:** `Figure_4_SHAP_Feature_Importance.tif`

---

### Figure 5: 逆向设计工作流程

**尺寸:** 1000×800 px (300 dpi)  
**类型:** 流程图  
**内容:** 正向预测 + 逆向设计

**制作要点:**
- 左侧：正向预测流程
- 右侧：逆向设计流程
- 底部：多目标优化 Pareto 前沿
- 箭头标注数据流

**文件:** `Figure_5_Inverse_Design_Workflow.tif`

---

### Figure 6: 主动学习推荐 Top20

**尺寸:** 1000×800 px (300 dpi)  
**类型:** 散点图 + 高亮  
**内容:** 1000 候选 UCB 分布

**制作要点:**
- X 轴：预测电导率
- Y 轴：UCB 分数
- Top20 用红色高亮
- 气泡大小=置信度

**文件:** `Figure_6_Active_Learning_Top20.tif`

---

### Figure 7: 模型蒸馏性能对比

**尺寸:** 800×800 px (300 dpi)  
**类型:** 雷达图 + 散点图  
**内容:** GP vs RF vs GB vs Ridge

**制作要点:**
- 左侧：雷达图 (R²/速度/大小)
- 右侧：Pareto 前沿散点图
- 四模型四色区分
- 最优区域标注

**文件:** `Figure_7_Model_Distillation_Comparison.tif`

---

### Figure 8: 实验验证平台架构

**尺寸:** 1200×800 px (300 dpi)  
**类型:** 系统架构图  
**内容:** 完整闭环流程

**制作要点:**
- 6 步骤环形布局
- 数据流箭头标注
- 关键模块放大展示
- 颜色统一 (蓝绿色系)

**文件:** `Figure_8_Experimental_Platform_Architecture.tif`

---

## 🛠️ 制作工具推荐

### 免费工具
- **Inkscape** - 矢量图编辑 (SVG)
- **GIMP** - 位图编辑 (TIFF/PNG)
- **Python Matplotlib** - 数据图表
- **Draw.io** - 流程图

### 付费工具
- **Adobe Illustrator** - 专业矢量图
- **BioRender** - 科研图示 (推荐)
- **Origin** - 科学绘图
- **GraphPad Prism** - 统计图表

### 在线工具
- **Canva** - 简易设计
- **Lucidchart** - 流程图
- **Plotly** - 交互图表

---

## 📐 Nature Communications 格式要求

### 主图
- **分辨率:** ≥300 dpi
- **格式:** TIFF/EPS/PDF
- **尺寸:** 单栏 (8.3cm) / 双栏 (17.2cm)
- **字体:** Arial/Helvetica, 8-10pt
- **颜色:** RGB 或 CMYK

### 补充图
- **分辨率:** ≥150 dpi
- **格式:** PDF  preferred
- **尺寸:** 灵活
- **字体:** 与主图一致

### 图注
- **长度:** 每图 200-300 词
- **内容:** 方法简述 + 关键发现
- **缩写:** 首次定义

---

## 📅 制作时间线

| 日期 | 任务 | 预计时间 |
|------|------|----------|
| 2026-03-12 AM | Figure 1 (Graphical Abstract) | 2 小时 |
| 2026-03-12 PM | Figure 2-3 (电导率 + 协同) | 2 小时 |
| 2026-03-13 AM | Figure 4-5 (SHAP+ 逆向) | 2 小时 |
| 2026-03-13 PM | Figure 6-7 (主动学习 + 蒸馏) | 2 小时 |
| 2026-03-14 AM | Figure 8 (实验平台) | 1 小时 |
| 2026-03-14 PM | 统一检查 + 导出 | 1 小时 |

**总计:** 10 小时 (1.5 天)

---

## ✅ 质量检查清单

### 技术检查
- [ ] 分辨率≥300 dpi
- [ ] 格式正确 (TIFF/EPS)
- [ ] 字体嵌入
- [ ] 颜色模式正确 (RGB/CMYK)
- [ ] 文件大小<10MB/图

### 内容检查
- [ ] 数据准确
- [ ] 误差棒标注
- [ ] 统计显著性标注 (*p<0.05, **p<0.01)
- [ ] 比例尺标注
- [ ] 缩写首次定义

### 美观检查
- [ ] 配色统一
- [ ] 字体一致
- [ ] 对齐整齐
- [ ] 留白适当
- [ ] 视觉层次清晰

---

## 📤 文件命名规范

**主图:**
```
Figure_1_Graphical_Abstract.tif
Figure_2_Conductivity_Evolution.tif
Figure_3_Synergistic_Effect.tif
Figure_4_SHAP_Feature_Importance.tif
Figure_5_Inverse_Design_Workflow.tif
Figure_6_Active_Learning_Top20.tif
Figure_7_Model_Distillation_Comparison.tif
Figure_8_Experimental_Platform_Architecture.tif
```

**补充图:**
```
Supplementary_Figure_S1_Data_Distribution.tif
Supplementary_Figure_S2_Model_Learning_Curve.tif
...
```

**源文件:**
```
Figure_1_Source.svg
Figure_2_Source.ai
...
```

---

## 🔗 参考资源

### Nature Communications 作者指南
- https://www.nature.com/ncomms/submit

### 科研图示最佳实践
- https://www.nature.com/nature/for-authors/illustrations

### 配色方案
- https://colorbrewer2.org/
- https://coolors.co/

### 字体下载
- https://fonts.google.com/
- https://www.fontsquirrel.com/

---

*创建时间：2026-03-11 15:03*  
*状态：图表制作准备中*  
*目标完成：2026-03-14*
