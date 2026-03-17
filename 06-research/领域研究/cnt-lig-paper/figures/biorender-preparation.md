# BioRender Preparation Guide - BioRender 准备指南

**目标:** 使用 BioRender 完成 Figure 1, 3, 5, 6, 8 细化  
**时间:** 2026-03-11 16:08 开始  
**预计:** 2 小时/图

---

## 📋 BioRender 注册与设置

### 步骤 1: 注册账号 (5 分钟)

1. 访问 **biorender.com**
2. 点击 "Sign Up"
3. 选择:
   - ✅ Free Plan (试用 30 天)
   - 或 Scientific Plan ($39/month)
4. 填写邮箱/密码
5. 验证邮箱

### 步骤 2: 选择模板

1. 登录后点击 "Create New"
2. 选择 "Graphical Abstract"
3. 搜索模板:
   - "Machine Learning"
   - "Materials Science"
   - "Nanotechnology"
4. 选择最接近的模板作为起点

### 步骤 3: 导入参考图

1. 点击 "Upload" → "Upload Image"
2. 上传 `Figure_1_Graphical_Abstract.svg`
3. 设置为参考层 (降低透明度至 30%)
4. 锁定参考层

---

## 🎨 Figure 1: Graphical Abstract (BioRender 细化)

### 所需图标 (从 BioRender 库搜索)

| 元素 | 搜索关键词 | 数量 | 颜色 |
|------|------------|------|------|
| **CNT** | "carbon nanotube" | 1 | #2E86AB |
| **LIG** | "laser graphene" | 1 | #A23B72 |
| **Graphene** | "graphene sheet" | 1 | #2E86AB |
| **MXene** | "2D material" | 1 | #F18F01 |
| **PEDOT** | "polymer" | 1 | #26A69A |
| **ML Model** | "neural network" | 1 | #2E86AB |
| **Database** | "database" | 1 | #A23B72 |
| **Experiment** | "lab equipment" | 3 | #F18F01 |
| **Arrow** | "arrow circular" | 6 | #2E86AB |
| **Star** | "star highlight" | 1 | #FF5722 |

### 布局步骤

**Phase 1: 背景与框架 (15 分钟)**
1. 创建 1200×800 px 画布
2. 设置背景色：#FFFFFF
3. 添加圆角矩形框架 (6 个)
4. 应用渐变色填充

**Phase 2: 添加图标 (45 分钟)**
1. 从库中拖拽图标到对应位置
2. 调整大小 (保持比例)
3. 应用统一配色
4. 添加阴影效果 (Depth: 20%)

**Phase 3: 文字标注 (30 分钟)**
1. 添加阶段标题 (Arial Bold 11pt)
2. 添加时间标注 (Arial Italic 9pt)
3. 添加项目符号列表 (Arial 9pt)
4. 检查拼写

**Phase 4: 箭头与连接 (20 分钟)**
1. 添加环形箭头 (6 个)
2. 设置箭头样式：3D, #2E86AB
3. 调整曲线平滑度
4. 添加数据流标注

**Phase 5: 中心指标框 (10 分钟)**
1. 创建中心圆角矩形
2. 添加 4 个关键指标
3. 应用橙色高亮 (#F18F01)
4. 添加图标前缀

**Phase 6: 导出 (10 分钟)**
1. 点击 "Export"
2. 选择格式:
   - ✅ TIFF (300 dpi, CMYK)
   - ✅ PNG (web preview)
   - ✅ SVG (editable)
3. 命名：`Figure_1_Graphical_Abstract_BioRender`
4. 下载

**预计总时间:** 2 小时 10 分钟

---

## 📊 Figure 3: Synergistic Effect (BioRender 细化)

### 所需图标

| 元素 | 搜索关键词 | 数量 |
|------|------------|------|
| **CNT Structure** | "nanotube structure" | 1 |
| **Graphene Layer** | "graphene layer" | 1 |
| **MXene Sheet** | "MXene 2D" | 1 |
| **Electron** | "electron arrow" | 3 |
| **Plus Sign** | "plus symbol" | 1 |
| **Percentage** | "percentage 47%" | 1 |

### 细化步骤

**机制图示 (1 小时):**
1. 左侧：二元复合示意图
2. 中间：三元复合 (+Graphene)
3. 右侧：四元复合 (+MXene) ⭐ 峰值
4. 添加电子传输路径箭头
5. 标注 "+47%" 增强机制

**柱状图集成 (30 分钟):**
1. 导出 Python 生成的柱状图 (PNG)
2. 导入 BioRender
3. 添加分子结构图示
4. 统一配色

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计总时间:** 1.5 小时

---

## 🔄 Figure 5: Inverse Design Workflow (BioRender 细化)

### 所需图标

| 元素 | 搜索关键词 | 数量 |
|------|------------|------|
| **Input Formulation** | "beaker formula" | 1 |
| **ML Model** | "machine learning" | 1 |
| **Output Graph** | "performance chart" | 1 |
| **Reverse Arrow** | "reverse arrow" | 1 |
| **Pareto Front** | "optimization curve" | 1 |
| **Computer** | "computer screen" | 1 |

### 流程图布局

**左侧：正向预测 (30 分钟)**
1. 输入图标 (配方)
2. ML 模型图标
3. 输出图标 (性能)
4. 箭头连接

**右侧：逆向设计 (30 分钟)**
1. 目标性能输入
2. 优化算法图标
3. 推荐配方输出
4. 迭代循环箭头

**底部：Pareto 前沿 (30 分钟)**
1. 导入 Python 生成的 Pareto 图
2. 添加图例说明
3. 标注最优区域

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计总时间:** 1.5 小时

---

## 🎯 Figure 6: Active Learning Top 20 (BioRender 辅助)

### 细化步骤

**散点图优化 (45 分钟):**
1. 使用 Python 生成基础散点图
2. 导入 BioRender
3. 添加 Top20 高亮 (红色边框)
4. 添加标注气泡
5. 添加图例说明

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计时间:** 45 分钟

---

## 🏗️ Figure 8: Experimental Platform (BioRender 细化)

### 所需图标

| 元素 | 搜索关键词 | 数量 |
|------|------------|------|
| **Prediction Model** | "computer model" | 1 |
| **Inverse Design** | "design process" | 1 |
| **Active Learning** | "AI learning" | 1 |
| **Lab SOP** | "lab protocol" | 1 |
| **Data Collection** | "data form" | 1 |
| **Model Update** | "model refresh" | 1 |
| **Circular Arrow** | "cycle arrow" | 1 |

### 系统架构图

**环形布局 (1 小时):**
1. 6 个步骤均匀分布
2. 每个步骤添加图标 + 文字
3. 添加环形箭头 (闭环)
4. 中心添加"Closed-Loop"标注

**数据流标注 (30 分钟):**
1. 添加虚线箭头 (反馈回路)
2. 标注"Auto-Update"
3. 添加版本号 (v1.0 → v2.0 → v3.0)

**输出:**
- TIFF (300 dpi)
- SVG (editable)

**预计总时间:** 1.5 小时

---

## 📅 BioRender 细化时间线

| 日期 | 任务 | 开始时间 | 结束时间 | 状态 |
|------|------|----------|----------|------|
| **Now** | Figure 1 (Graphical Abstract) | 16:10 | 18:20 | ⏸️ 待开始 |
| **Break** | 休息 15 分钟 | 18:20 | 18:35 | - |
| **Continue** | Figure 3 (Synergistic Effect) | 18:35 | 20:05 | ⏸️ 待开始 |
| **Day 2 AM** | Figure 5 (Inverse Design) | 09:00 | 10:30 | ⏸️ 待开始 |
| **Day 2 PM** | Figure 6 (Active Learning) | 14:00 | 14:45 | ⏸️ 待开始 |
| **Day 3 AM** | Figure 8 (Experimental) | 09:00 | 10:30 | ⏸️ 待开始 |
| **Day 3 PM** | 统一检查 + 导出 | 14:00 | 15:00 | ⏸️ 待开始 |

---

## ✅ 质量检查 (每图完成后)

### 技术检查
- [ ] 分辨率 300 dpi
- [ ] 格式 TIFF + SVG
- [ ] 字体 Arial (已嵌入)
- [ ] 颜色模式 RGB/CMYK
- [ ] 文件大小<10MB

### 内容检查
- [ ] 数据准确
- [ ] 文字无拼写错误
- [ ] 图标与内容匹配
- [ ] 箭头方向正确
- [ ] 图例完整

### 美观检查
- [ ] 配色统一 (Nature 模板)
- [ ] 对齐整齐
- [ ] 留白适当
- [ ] 视觉层次清晰
- [ ] 专业美观

---

## 📤 文件命名与存储

**BioRender 源文件:**
```
Figure_1_BioRender_Source.br
Figure_3_BioRender_Source.br
Figure_5_BioRender_Source.br
Figure_6_BioRender_Source.br
Figure_8_BioRender_Source.br
```

**导出文件:**
```
Figure_1_Graphical_Abstract_BioRender.tiff
Figure_1_Graphical_Abstract_BioRender.png
Figure_1_Graphical_Abstract_BioRender.svg
...
```

**存储位置:**
```
11-research/cnt-lig-paper/figures/
├── biorender/
│   ├── sources/         # .br 源文件
│   ├── tiff/            # 300 dpi TIFF
│   ├── png/             # Web preview
│   └── svg/             # Editable SVG
└── ...
```

---

## 🎯 立即可开始

**现在 (16:08):**
1. ✅ 打开浏览器
2. ✅ 访问 biorender.com
3. ✅ 注册/登录账号
4. ✅ 开始 Figure 1 细化

**预计完成时间:** 18:20 (Figure 1)

**进度追踪:**
- 每完成一个阶段，勾选 ✅
- 遇到困难，记录问题
- 完成后保存 + 导出

---

*Created: 2026-03-11 16:08*  
*Status: Ready to Start BioRender*  
*First Target: Figure 1 (2 hours)*
