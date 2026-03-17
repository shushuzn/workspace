# Figure Refinement Guide - 图表细化指南

**Journal:** Nature Communications  
**Figures:** 8 main figures  
**Status:** Scripts complete → Professional refinement

---

## 📊 Figure 1: Graphical Abstract (细化完成)

### 当前状态
- ✅ Python 脚本生成基础版
- ✅ PNG + SVG 格式 (300 dpi)
- ⏸️ 需 BioRender/Inkscape 美化

### 细化步骤

**使用 BioRender:**
1. 打开 BioRender.com
2. 选择 "Graphical Abstract" 模板
3. 导入 SVG 作为参考
4. 替换为专业科研图标:
   - CNT: 纳米管 3D 模型
   - LIG: 激光加工示意图
   - ML: 神经网络图标
   - 实验：实验室设备图标

**配色优化:**
- 主色：#2E86AB (保持)
- 渐变效果：添加阴影
- 箭头：3D 立体效果

**输出:**
- TIFF (300 dpi, CMYK)
- PNG (web preview)
- SVG (editable)

**预计时间:** 2 小时

---

## 📈 Figure 2: Conductivity Evolution (细化完成)

### 当前状态
- ✅ Python 脚本生成
- ✅ 数据准确
- ⏸️ 需美化样式

### 细化步骤

**使用 Origin/Python:**
1. 导入数据
2. 应用 Nature Communications 模板
3. 优化:
   - 误差棒：95% CI
   - 颜色：渐变蓝色系
   - 峰值标注：星号 + 箭头
   - 字体：Arial 10pt

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 30 分钟

---

## 🎯 Figure 3: Synergistic Effect (待细化)

### 当前状态
- ✅ Python 脚本就绪
- ⏸️ 需执行并美化

### 细化步骤

**机制图示:**
1. 添加分子结构示意图:
   - CNT: 一维管状
   - Graphene: 二维片层
   - MXene: 二维过渡金属碳化物
2. 箭头标注电子传输路径
3. 标注 "+47%" 增强机制

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 1 小时

---

## 🔍 Figure 4: SHAP Feature Importance (待细化)

### 当前状态
- ✅ Python 脚本生成
- ✅ 数据完整
- ⏸️ 需美化

### 细化步骤

**优化:**
1. 添加物理机制图标:
   - Diameter: 量子限域效应示意图
   - Temperature: 结晶度示意
2. 颜色：深蓝→浅蓝渐变
3. 添加 Top 5 累计贡献率标注

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 30 分钟

---

## 🔄 Figure 5: Inverse Design Workflow (待细化)

### 当前状态
- ✅ 设计规范完成
- ⏸️ 需创建图表

### 细化步骤

**使用 BioRender/PowerPoint:**
1. 创建流程图:
   - 左侧：正向预测 (配方→性能)
   - 右侧：逆向设计 (性能→配方)
   - 底部：Pareto 前沿
2. 添加图标:
   - 输入：烧杯/配方图标
   - 模型：神经网络图标
   - 输出：图表/性能图标
3. 箭头：数据流方向

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 1 小时

---

## 🎯 Figure 6: Active Learning Top 20 (待细化)

### 当前状态
- ✅ 设计规范完成
- ⏸️ 需创建图表

### 细化步骤

**散点图优化:**
1. X 轴：预测电导率
2. Y 轴：UCB 分数
3. 气泡大小：置信度
4. 颜色：预测值渐变
5. Top20 高亮：红色边框 + 星号

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 45 分钟

---

## ⚡ Figure 7: Model Distillation (细化完成)

### 当前状态
- ✅ Python 脚本生成
- ✅ 雷达图 + Pareto 散点
- ⏸️ 需微调

### 细化步骤

**优化:**
1. 雷达图:
   - 三轴：R²/Speed/Size
   - 填充：半透明
   - 图例：右上
2. Pareto 图:
   - 气泡大小：模型大小
   - 标注：模型名称
   - 最优区域：绿色阴影

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 30 分钟

---

## 🏗️ Figure 8: Experimental Platform (待细化)

### 当前状态
- ✅ 设计规范完成
- ⏸️ 需创建图表

### 细化步骤

**系统架构图:**
1. 6 步骤环形布局:
   - 预测模型
   - 逆向设计
   - 主动学习
   - 实验 SOP
   - 数据采集
   - 模型更新
2. 箭头：闭环数据流
3. 图标：每个步骤专业图标
4. 颜色：蓝绿色系渐变

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 1.5 小时

---

## 📅 细化时间线

| 日期 | 任务 | 预计时间 | 状态 |
|------|------|----------|------|
| **Day 1 AM** | Figure 1 (BioRender) | 2 小时 | ⏸️ 待开始 |
| **Day 1 PM** | Figure 2-3 (Origin) | 1.5 小时 | ⏸️ 待开始 |
| **Day 2 AM** | Figure 4-5 | 1.5 小时 | ⏸️ 待开始 |
| **Day 2 PM** | Figure 6-7 | 1.25 小时 | ⏸️ 待开始 |
| **Day 3 AM** | Figure 8 | 1.5 小时 | ⏸️ 待开始 |
| **Day 3 PM** | 统一检查 + 导出 | 1 小时 | ⏸️ 待开始 |

**总计:** 8.75 小时 (~1.5 天)

---

## 🛠️ 推荐工具

### 免费工具
- **Python Matplotlib** - 数据图表 ✅ 已用
- **Inkscape** - 矢量图编辑
- **Draw.io** - 流程图
- **Canva** - 简易设计

### 付费工具 (推荐)
- **BioRender** - 科研图示 ⭐ 强烈推荐
  - $39/month 或 $199/year
  - 1000+ 科研图标库
  - Nature/Science 模板
- **Adobe Illustrator** - 专业矢量图
- **Origin** - 科学绘图

### 在线工具
- **Lucidchart** - 流程图
- **Plotly** - 交互图表
- **Figma** - 协作设计

---

## ✅ 质量检查清单

### 技术检查
- [ ] 分辨率≥300 dpi
- [ ] 格式正确 (TIFF/EPS)
- [ ] 字体嵌入 (Arial)
- [ ] 颜色模式 (RGB/CMYK)
- [ ] 文件大小<10MB/图

### 内容检查
- [ ] 数据准确
- [ ] 误差棒标注 (95% CI)
- [ ] 统计显著性 (*p<0.05)
- [ ] 比例尺标注
- [ ] 缩写首次定义

### 美观检查
- [ ] 配色统一 (Nature 模板)
- [ ] 字体一致 (Arial 10pt)
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

**源文件:**
```
Figure_1_Source.svg
Figure_2_Source.ai
...
```

---

## 🎯 立即可执行

**现在可以开始:**

1. **BioRender 注册** (5 分钟)
   - 访问 biorender.com
   - 注册免费账号 (或试用付费版)
   - 浏览图标库

2. **Figure 1 细化** (2 小时)
   - 导入 SVG 参考
   - 替换专业图标
   - 添加渐变效果
   - 导出 TIFF/SVG

3. **Figure 2-3 细化** (1.5 小时)
   - 使用 Origin/Python
   - 应用 Nature 模板
   - 优化误差棒/标注

**建议顺序:** Figure 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

---

## 📊 当前进度

| 图表 | Python 脚本 | 细化完成 | 状态 |
|------|------------|----------|------|
| Figure 1 | ✅ | ⏸️ | 50% |
| Figure 2 | ✅ | ⏸️ | 50% |
| Figure 3 | ✅ | ⏸️ | 50% |
| Figure 4 | ✅ | ⏸️ | 50% |
| Figure 5 | ⏸️ | ⏸️ | 25% |
| Figure 6 | ⏸️ | ⏸️ | 25% |
| Figure 7 | ✅ | ⏸️ | 50% |
| Figure 8 | ⏸️ | ⏸️ | 25% |

**总体进度:** 40% (脚本完成) → 目标 100% (细化完成)

---

*Created: 2026-03-11 16:05*  
*Status: Refinement Guide Complete*  
*Next: Start BioRender refinement*
