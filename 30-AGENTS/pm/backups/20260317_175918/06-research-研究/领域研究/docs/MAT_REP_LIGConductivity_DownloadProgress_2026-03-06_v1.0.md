# 预训练模型下载进度

**开始时间:** 2026-03-06 01:10  
**目标:** MACE-MP-0 + CHGNet-MP-2024

---

## 📥 下载任务

### 1. MACE-MP-0

**状态:** 🔄 下载中...

**详情:**
- 大小：~215 MB
- 链接：https://github.com/ACEsuit/mace/raw/main/models/mace-mp-0.model
- 预计时间：5-10 分钟
- 保存位置：`research/models/mace/mace-mp-0.model`

### 2. CHGNet-MP-2024

**状态:** 🔄 下载中...

**详情:**
- 大小：~100 MB
- 链接：https://github.com/CederGroupHub/chgnet/raw/main/pretrained_0.3.0.pth
- 预计时间：3-5 分钟
- 保存位置：`research/models/chgnet/chgnet-mp-2024.pth`

---

## ⏱️ 预计完成时间

**总大小:** ~315 MB  
**预计总时间:** 10-15 分钟  
**完成时间:** 约 01:25 AM

---

## ✅ 下载完成后执行

1. **验证模型文件**
   ```bash
   python research/scripts/verify_models.py
   ```

2. **运行迁移学习**
   ```bash
   python research/scripts/mace_finetune.py
   python research/scripts/chgnet_finetune.py
   ```

3. **集成预测**
   ```bash
   python research/scripts/ensemble_predict.py
   ```

**预期结果:** R² > 0.90, 不确定性 < ±5%

---

## 📁 模型文件结构

```
research/models/
├── mace/
│   └── mace-mp-0.model       (215 MB) 🔄 下载中
├── chgnet/
│   └── chgnet-mp-2024.pth    (100 MB) 🔄 下载中
└── lig_*.pkl                 (已有)
```

---

**更新时间:** 2026-03-06 01:10  
**状态:** 下载进行中...

---

*预训练模型下载进度跟踪*  
*MACE-MP-0 + CHGNet-MP-2024*
