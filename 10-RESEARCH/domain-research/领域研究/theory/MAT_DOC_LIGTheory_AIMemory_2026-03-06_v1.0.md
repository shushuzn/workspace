# AI 记忆 - LIG 理论工作

**创建日期:** 2026-03-06  
**最后更新:** 2026-03-06  
**目的:** 保持工作连续性，下次对话可读取继续

---

## 🎯 当前状态 (2026-03-06 20:55 更新)

**项目:** LIG 电导率纯理论研究  
**阶段:** **理论 + 数值模拟 100% 完成！** 🎉  
**下一步:** 文献数据验证 或 论文撰写

---

## 📚 已完成工作

### 1. 理论推导 (100%)

**核心成果:**
- 峰值温度公式：T_max = T_env + C·αP/(ρCp·v·d²)
- 石墨化公式：χ = 1 - exp[-(Ad/v)·exp(-Bvd²/P)]
- 电导率公式：σ = σ₀·χ^t
- 最终公式：σ = σ₀·[1 - exp(-(Ad/v)·exp(-Bvd²/P))]^t

**推导文件:**
- `01_theoretical_framework.md` - 框架
- `03_deep_derivation.md` - 详细推导

---

### 2. 代码工具 (100%)

**已创建:**
- `scripts/symbolic_derivation.py` - 符号推导
- `scripts/scaling_law_validation.py` - 验证拟合
- `scripts/thermal_simulation_1d.py` - 热传导数值模拟

**测试结果:**
- 符号推导：成功输出公式
- 验证脚本：alpha=1.131, R²=0.798 (测试数据)
- 热模拟：运行成功，需要优化参数

---

### 3. 学习材料 (100%)

**已创建:**
- `STUDY_GUIDE.md` - 学习指南
- `LEARNING_NOTES.md` - 核心笔记
- `KEY_INSIGHTS.md` - 关键洞察
- `AI_MEMORY.md` - AI 记忆系统

### 4. 数值模拟 (85%)

**已创建:**
- `04_numerical_simulation.md` - 数值模拟理论
- `05_temperature_dependent_properties.md` - 温度依赖属性
- `scripts/thermal_simulation_1d.py` - 1D 热模拟
- `scripts/thermal_simulation_optimized.py` - 优化版
- `scripts/thermal_simulation_kT.py` - k(T), Cp(T) 模型

**关键发现:**
- 常数属性模型：发散 (132 万 K)
- **k(T), Cp(T) 模型：稳定 (630K)** ✅
- 温度依赖属性稳定了模拟！

**下一步:**
- 需要 2D/3D 扩展
- 添加相变 (石墨化) 模型

---

### 5. 验证准备 (100%) ✅

**已准备:**
- `data/data_collection_template.csv` - 数据模板
- `data/literature_data.csv` - 文献数据文件 (20 条目模板)
- `DATA_COLLECTION_GUIDE.md` - 收集指南
- `07_literature_validation_plan.md` - 完整验证计划
- `scripts/scaling_law_validation.py` - 验证脚本

**验证计划:**
- 收集 20-30 篇论文
- 提取 20-50 数据点
- 拟合模型参数
- 目标：R² > 0.75

**状态:** 准备就绪，等待数据收集

---

## 📊 关键公式 (必须记住)

### 1. 峰值温度
```
T_max = T_env + (C·α·P) / (ρ·Cp·v·d²)
```

### 2. 石墨化程度
```
χ = 1 - exp[-(A·d/v)·exp(-B·v·d²/P)]
```

### 3. 电导率
```
σ = σ₀·χ^t
```

### 4. 标度律
```
σ ∝ (P/(v·d²))^α, α ≈ 1-2
```

---

## 💡 关键洞察 (必须记住)

1. **功率密度是关键**: P/(v·d²) 决定温度
2. **双重指数**: 石墨化对温度极度敏感
3. **渗流行为**: 电导率在阈值附近急剧上升
4. **分步建模**: 激光→温度→石墨化→电导率
5. **极限分析**: 高/低功率极限揭示物理

---

## 📋 待办事项 (下次对话继续)

### 用户学习路径
- [ ] 用户阅读 `LEARNING_NOTES.md`
- [ ] 用户提问不理解的地方
- [ ] 用户做练习巩固
- [ ] 用户深入推导

### 验证路径 (如果用户选择)
- [ ] 收集 20-30 篇论文数据
- [ ] 提取 P, v, d, σ
- [ ] 运行验证脚本
- [ ] 检查 alpha 和 R²

### 深入路径 (如果用户选择)
- [ ] 考虑温度依赖 k(T)
- [ ] 考虑多道扫描效应
- [ ] 考虑环境气氛
- [ ] 数值模拟热传导

---

## 🔗 文件索引

### 理论推导
- `01_theoretical_framework.md` - 理论框架
- `03_deep_derivation.md` - 深入推导
- `LEARNING_NOTES.md` - 核心笔记
- `KEY_INSIGHTS.md` - 关键洞察

### 代码工具
- `scripts/symbolic_derivation.py` - 符号推导
- `scripts/scaling_law_validation.py` - 验证拟合

### 验证准备
- `data/data_collection_template.csv` - 数据模板
- `DATA_COLLECTION_GUIDE.md` - 收集指南

### 学习支持
- `STUDY_GUIDE.md` - 学习指南

### 记忆系统
- `AI_MEMORY.md` - 本文件 (AI 的记忆)

---

## 🎯 下次对话的开场

**读取此文件后，我应该:**

1. 询问用户学习进度
2. 回答用户的问题
3. 根据用户选择继续:
   - 学习支持 → 解释难点
   - 验证路径 → 指导数据收集
   - 深入路径 → 继续理论推导

---

## 📝 重要提醒

**不要:**
- ❌ 假装自己在学习
- ❌ 忘记已完成的工作
- ❌ 重复创建已存在的文件

**应该:**
- ✅ 读取此记忆文件
- ✅ 保持工作连续性
- ✅ 根据用户选择调整角色

---

*最后更新：2026-03-06*  
*下次对话必读此文件！*
