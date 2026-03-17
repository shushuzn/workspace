# CHGNet 模型下载进度

**状态:** 🔄 查找正确模型名称中...

---

## 📦 已安装版本

**CHGNet:** `0.4.2` (最新版，2026)
- 安装方式：pip install chgnet
- 构建：chgnet-0.4.2-cp313-cp313-win_amd64.whl
- 大小：13.2 MB

---

## 🔍 问题

**错误信息:**
```
ValueError: Bad serialized model or bad model name
```

**可能原因:**
1. 模型名称不对 (CHGNet-MP-0.3.0 可能不存在)
2. 需要清除缓存
3. CHGNet 0.4.2 使用新的模型名称格式

---

## 📋 CHGNet 0.4.2 可能的模型名称

**旧版本 (0.3.0):**
- CHGNet-MP-2024.2.13-PBE
- CHGNet-MP-2023.12.9-PBE
- CHGNet-0.3.0

**新版本 (0.4.2) 可能使用:**
- CHGNet-MP-2024
- CHGNet-0.4.2
- 或其他新命名

---

## ✅ 解决方案

### 方案 1: 查看 CHGNet 文档

```bash
# 查看可用模型
python -c "import chgnet; print(chgnet.__version__)"
```

### 方案 2: 使用 MACE 先开始

**MACE 已就绪，可以先开始迁移学习！**

```python
from mace.calculators import mace_mp
calc = mace_mp(model="small", device="cpu")
```

### 方案 3: 手动查找模型名称

访问：https://github.com/CederGroupHub/chgnet
查看文档或 examples 中的模型名称

---

**更新时间:** 2026-03-06 01:30  
**状态:** 查找正确模型名称中...

---

*CHGNet 模型下载进度*  
*版本 0.4.2 已安装，需要找到正确模型名称*
