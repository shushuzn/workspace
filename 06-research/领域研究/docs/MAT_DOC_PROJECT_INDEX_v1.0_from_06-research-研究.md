# 研究项目索引

**创建时间:** 2026-03-06 22:54  
**更新:** 实时

---

## 📊 活跃项目

### 1. LIG 导电率预测 (投稿中)

**状态:** 🟡 投稿准备 (99%)  
**目标期刊:** Carbon (IF=11.3, Q1)  
**提交截止:** 2026-03-15

#### 文档链接
- [[paper/00_abstract]] - 摘要
- [[paper/01_introduction]] - 引言
- [[paper/02_related_work]] - 相关工作
- [[paper/03_methods]] - 方法
- [[paper/04_results]] - 结果与讨论
- [[paper/05_conclusion]] - 结论
- [[paper/cover_letter]] - 投稿信
- [[paper/highlights]] - 亮点 (5 条)
- [[paper/submission_checklist]] - 投稿检查清单
- [[paper/timeline]] - 投稿时间线

#### 数据与代码
- [[github_repo]] - GitHub 仓库
- [[models]] - 模型文件
- [[figures]] - 可视化图表
- [[scripts/gp_run]] - GP 训练脚本
- [[scripts/predict]] - 预测脚本

#### 模型性能
| 指标 | 值 | 状态 |
|------|-----|------|
| R² | 0.773 | 🟡 接近目标 |
| MAE | 506.4 S/m | ✅ |
| 95% CI 覆盖率 | 100% | ✅ |

#### 待办
- [ ] 从 Sci-Hub PDF 提取数据
- [ ] 重新验证模型 (目标 R² > 0.75)
- [ ] 最终校对 (2026-03-10)
- [ ] 提交 Carbon (2026-03-15)

---

### 2. CNT 性能预测 (启动阶段)

**状态:** 🟢 Pipeline 建立完成  
**目标:** 300+ 数据点，R² > 0.75  
**预期论文:** 2 篇

#### 文档链接
- [[cnt-research/README]] - 项目总览
- [[cnt-research/literature/README]] - 文献收集指南
- [[cnt-research/literature/WEEKLY_PLAN]] - 周计划
- [[cnt-research/literature/starter_papers]] - 起点论文
- [[cnt-research/data/data_extraction_template]] - 数据提取模板

#### 脚本与工具
- [[cnt-research/scripts/cnt_gp_run]] - GP 模型训练
- [[cnt-research/scripts/cnt_shap_analysis]] - SHAP 可解释性
- [[cnt-research/scripts/cnt_data_extractor]] - 数据提取

#### 当前状态
- ✅ GP 模型 Pipeline 建立
- ✅ 3 张可视化图表生成
- ⚠️ 数据量不足 (2/300 样本)

#### 待办
- [ ] Day 2-3: 大规模文献检索
- [ ] Day 4-6: 数据提取 (300+ 样本)
- [ ] Day 7: 数据整理与分析

---

### 3. 理论工作 (100% 完成)

**状态:** ✅ 完成  
**核心发现:** k(T), Cp(T) 稳定数值模拟

#### 文档链接
- [[theory/01_theoretical_framework]] - 理论框架
- [[theory/03_deep_derivation]] - 深度推导
- [[theory/04_numerical_simulation]] - 数值模拟
- [[theory/05_temperature_dependent_properties]] - 温度依赖属性
- [[theory/06_2d_axisymmetric_model]] - 2D 轴对称模型

#### 关键结果
| 模型 | T_max | vs 1D 解析 |
|------|-------|-----------|
| 2D 常数属性 | 11,103 K | 202% ❌ |
| 2D k(T),Cp(T) | 5,341 K | 97.2% ✅ |

---

## 📁 文档结构

```
11-research/
├── PROJECT_INDEX.md          # 本文件
├── paper/                    # LIG 论文
│   ├── 00_abstract.md
│   ├── 01_introduction.md
│   ├── 02_related_work.md
│   ├── 03_methods.md
│   ├── 04_results.md
│   ├── 05_conclusion.md
│   ├── cover_letter.md
│   ├── highlights.md
│   └── submission_checklist.md
├── cnt-research/             # CNT 项目
│   ├── README.md
│   ├── literature/
│   ├── data/
│   ├── scripts/
│   ├── figures/
│   └── models/
├── theory/                   # 理论工作
│   ├── 01_theoretical_framework.md
│   ├── 03_deep_derivation.md
│   ├── 04_numerical_simulation.md
│   ├── 05_temperature_dependent_properties.md
│   └── 06_2d_axisymmetric_model.md
├── models/                   # 模型文件
├── figures/                  # 可视化图表
├── scripts/                  # 脚本工具
├── data/                     # 数据集
└── ORGANIZED_PROJECT/        # 旧版论文草稿
```

---

## 🔗 跨文档链接

### 记忆与日志
- [[../memory/2026-03-06]] - 今日记忆
- [[../MEMORY]] - 长期记忆

### 核心文档
- [[../HEARTBEAT]] - 心跳任务
- [[../SOUL]] - 身份定义
- [[../AGENTS]] - 工作区规范
- [[../TOOLS]] - 工具配置

### 索引与导航
- [[../15-docs/FOLDER-INDEX]] - 文件夹总索引
- [[../README]] - 项目总览

---

---

## 🔙 反向链接

**链接到本文档的文件:**
- [[../README]] - Workspace 导航首页 (引用 PROJECT_INDEX 作为研究入口)
- [[../15-docs/LINK_INDEX]] - 内部链接总索引
- [[../HEARTBEAT]] - 心跳任务清单 (引用项目状态)
- [[../memory/2026-03-06]] - 今日记忆日志 (记录项目进展)
- [[../32-workflows/WORKFLOW_INDEX]] - 工作流索引 (使用项目输出)
- [[../32-workflows/06-knowledge-graph/README]] - 知识图谱工作流

**子项目文档:**
- [[paper/README]] - LIG 论文项目
- [[cnt-research/README]] - CNT 研究项目
- [[theory/01_theoretical_framework]] - 理论框架
- [[scripts/README]] - 研究脚本索引

---

*最后更新:* 2026-03-06 23:27
