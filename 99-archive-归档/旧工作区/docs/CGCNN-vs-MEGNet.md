# CGCNN vs MEGNet - 模型对比

**版本:** v1.0  
**创建时间:** 2026-03-05 20:40  
**目的:** 对比两种材料性能预测模型

---

## 📊 核心对比

| 特性 | CGCNN | MEGNet |
|------|-------|--------|
| **全称** | Crystal Graph Convolutional Neural Network | Materials Graph Network |
| **架构** | 图卷积神经网络 | 图神经网络 + 全局状态 |
| **提出时间** | 2018 | 2019 |
| **精度 (形成能)** | MAE ~0.03 eV/atom | MAE ~0.02 eV/atom |
| **精度 (带隙)** | MAE ~0.35 eV | MAE ~0.28 eV |
| **推理速度** | 较快 | 稍慢 |
| **模型大小** | ~50 MB | ~100 MB |
| **适用场景** | 晶体材料 | 晶体/分子/材料 |

---

## 🎯 架构差异

### CGCNN

```
原子特征 → 卷积层 → 池化 → 全连接 → 性能预测
    ↑
晶体图 (原子 + 键)
```

**特点:**
- 专注晶体结构
- 局部特征提取
- 计算效率高

### MEGNet

```
原子特征 → 图网络 → 全局状态 → 性能预测
    ↑          ↑          ↑
  原子      键信息    整体特征
```

**特点:**
- 引入全局状态向量
- 捕获长程相互作用
- 适用性更广

---

## 💻 CPU 优化对比

### 已实现保护机制

| 机制 | CGCNN | MEGNet |
|------|-------|--------|
| 线程限制 | ✅ intra=4, inter=2 | ✅ intra=4, inter=2 |
| 并发控制 | ✅ max=1 | ✅ max=1 |
| CPU 监控 | ✅ 阈值 70% | ✅ 阈值 70% |
| 缓存系统 | ✅ 500 条 LRU | ✅ 500 条 LRU |
| 批处理 | ✅ batch=10 | ✅ batch=10 |

**两者 CPU 使用完全一致！** ✅

---

## 📈 性能对比 (预估)

### 单次预测

| 模型 | CPU 使用 | 耗时 | 内存 |
|------|---------|------|------|
| **CGCNN** | 40-50% | 2-3 秒 | ~500 MB |
| **MEGNet** | 45-55% | 2.5-4 秒 | ~800 MB |

### 批量预测 (10 个)

| 模型 | CPU 使用 | 耗时 | 内存 |
|------|---------|------|------|
| **CGCNN** | 60-70% | 20-30 秒 | ~600 MB |
| **MEGNet** | 65-75% | 25-40 秒 | ~1 GB |

---

## 🎯 使用建议

### 选择 CGCNN 的场景

1. ✅ **快速筛选** - 需要快速预测大量材料
2. ✅ **资源受限** - 内存有限 (<1 GB)
3. ✅ **晶体材料** - 只处理晶体结构
4. ✅ **日常使用** - 对精度要求不高

### 选择 MEGNet 的场景

1. ✅ **高精度需求** - 需要更准确的预测
2. ✅ **多样材料** - 晶体 + 分子 + 其他
3. ✅ **研究用途** - 发表级精度
4. ✅ **复杂体系** - 需要长程相互作用

---

## 🔧 在我们的系统中

### 当前状态

| 模型 | 状态 | 脚本 | 大小 |
|------|------|------|------|
| **CGCNN** | ✅ CPU 优化版 | cgcnn-model.py | 13.1 KB |
| **MEGNet** | ✅ CPU 优化版 | megnet-model.py | 12.5 KB |

### 统一接口

```python
# 两者使用相同的接口
from cgcnn_model import get_cgcnn_model
from megnet_model import get_megnet_model

# 创建模型 (配置相同)
cgcnn = get_cgcnn_model(config)
megnet = get_megnet_model(config)

# 预测 (接口一致)
result_cgcnn = cgcnn.predict(structure)
result_megnet = megnet.predict(structure)
```

### 模型选择策略

```python
def predict_with_best_model(structure, priority='accuracy'):
    if priority == 'speed':
        model = get_cgcnn_model()
    else:  # accuracy
        model = get_megnet_model()
    
    return model.predict(structure)
```

---

## 📊 精度对比 (Materials Project 数据集)

| 性能 | CGCNN (MAE) | MEGNet (MAE) | 提升 |
|------|-----------|------------|------|
| **形成能** | 0.030 eV | 0.020 eV | +33% |
| **带隙** | 0.35 eV | 0.28 eV | +20% |
| **体积模量** | 15 GPa | 12 GPa | +20% |
| **剪切模量** | 12 GPa | 10 GPa | +17% |

**MEGNet 精度全面领先！** 🏆

---

## 💡 实际应用建议

### 日常研究

```python
# 快速筛选：用 CGCNN
candidates = screen_1000_materials(model='cgcnn')

# 精选材料：用 MEGNet
top_100 = rerank(candidates, model='megnet')

# 实验验证：用 MEGNet + DFT
final_validation(top_10, model='megnet+dft')
```

### 高通量筛选

```python
# 第一阶段：CGCNN 快速筛选
stage1 = cgcnn.predict_batch(1000_materials)

# 第二阶段：MEGNet 精确预测
stage2 = megnet.predict_batch(stage1.top_100)

# 第三阶段：DFT 验证
stage3 = dft.calculate(stage2.top_10)
```

---

## 🎯 在我们的 AI Research OS 中

### 集成策略

```
论文提取 → 晶体结构 → [CGCNN/MEGNet] → 性能预测 → 知识图谱
                                    ↓
                              自动选择模型
                              (速度 vs 精度)
```

### 默认配置

- **日常使用:** CGCNN (快速)
- **重要研究:** MEGNet (精确)
- **大批量:** CGCNN 初筛 + MEGNet 精选

---

## 📝 总结

| 维度 | 胜者 | 理由 |
|------|------|------|
| **精度** | 🏆 MEGNet | 全面领先 17-33% |
| **速度** | 🏆 CGCNN | 快 20-30% |
| **内存** | 🏆 CGCNN | 占用少 30-40% |
| **通用性** | 🏆 MEGNet | 支持更多材料类型 |
| **CPU 优化** | 🤝 平手 | 保护机制相同 |

**推荐:**
- ✅ **两者都装** - 根据场景选择
- ✅ **默认 CGCNN** - 日常使用
- ✅ **重要用 MEGNet** - 高精度需求

---

*文档生成时间：2026-03-05 20:40*  
*作者：Claw (AI Research OS)*
