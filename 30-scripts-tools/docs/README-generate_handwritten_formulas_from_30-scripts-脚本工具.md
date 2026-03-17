# 手写公式数据集生成器

**数据增强工具** - 生成 500+ 手写公式样本用于模型微调

---

## 📖 简介

`generate_handwritten_formulas.py` 用于生成手写公式数据集，模拟实验室笔记中的真实书写场景，用于训练和微调公式识别模型。

### 核心功能

- **5 大领域覆盖**: 物理、化学、数学、电化学、材料科学
- **多样本书写风格**: 5 种手写风格模拟 (工整/潦草/快速/标注/混合)
- **批量生成**: 一键生成 500+ 样本
- **数据增强**: 支持旋转、缩放、噪声等增强操作
- **多格式输出**: JSON + 图像文件 (PNG)

---

## 🚀 快速使用

### 基本命令

```bash
# 生成默认 500 个样本
py 30-scripts/generate_handwritten_formulas.py --output data/handwritten/

# 指定样本数量
py 30-scripts/generate_handwritten_formulas.py --num-samples 1000 --output data/handwritten/

# 指定领域分布
py 30-scripts/generate_handwritten_formulas.py --domains physics,electrochemistry --output data/handwritten/

# 启用数据增强
py 30-scripts/generate_handwritten_formulas.py --augment --output data/handwritten/
```

### 输出示例

```
[OK] Generating 500 handwritten formula samples...
[OK] Domain distribution:
  - physics: 100 samples
  - chemistry: 100 samples
  - math: 100 samples
  - electrochemistry: 100 samples
  - materials: 100 samples

[OK] Writing styles:
  - neat: 100 samples (工整)
  - messy: 100 samples (潦草)
  - fast: 100 samples (快速)
  - annotated: 100 samples (标注)
  - mixed: 100 samples (混合)

[OK] Generated 500 images in data/handwritten/images/
[OK] Generated metadata in data/handwritten/handwritten_formulas.json
[OK] Dataset statistics:
  - Total samples: 500
  - Unique formulas: 45
  - Average formula length: 18.3 chars
  - Image resolution: 512x256
```

---

## 📊 输出格式

### 目录结构

```
data/handwritten/
├── images/
│   ├── hw_000001.png
│   ├── hw_000002.png
│   └── ...
├── handwritten_formulas.json
└── dataset_stats.json
```

### JSON 元数据

```json
{
  "generated_at": "2026-03-10T04:30:00",
  "total_samples": 500,
  "samples": [
    {
      "id": "hw_000001",
      "formula": "R = \\rho \\frac{L}{A}",
      "domain": "physics",
      "style": "neat",
      "image": "images/hw_000001.png",
      "latex_normalized": "R = \\rho \\frac{L}{A}",
      "complexity": "medium",
      "augmentations": []
    },
    {
      "id": "hw_000002",
      "formula": "E = E^0 - \\frac{RT}{nF}\\ln Q",
      "domain": "electrochemistry",
      "style": "messy",
      "image": "images/hw_000002.png",
      "latex_normalized": "E = E^{0} - \\frac{R T}{n F} \\ln{Q}",
      "complexity": "high",
      "augmentations": ["rotate_5deg", "noise_gaussian"]
    }
  ]
}
```

---

## 🎨 书写风格

| 风格 | 描述 | 特征 | 适用场景 |
|------|------|------|----------|
| **neat** (工整) | 清晰规整 | 笔画均匀、间距一致 | 正式笔记、考试 |
| **messy** (潦草) | 随意潦草 | 连笔、省略、变形 | 快速记录、草稿 |
| **fast** (快速) | 匆忙书写 | 简化、倾斜、不均匀 | 实验记录、会议 |
| **annotated** (标注) | 带标注 | 箭头、下划线、圈注 | 讲解、批注 |
| **mixed** (混合) | 风格混合 | 多种风格组合 | 真实场景模拟 |

---

## 📐 公式领域分布

### 物理 (physics) - 100 个
- 欧姆定律、电阻公式
- 功率、能量公式
- 电磁学公式
- 力学公式

### 化学 (chemistry) - 100 个
- pH 计算
- 平衡常数
- 热力学公式
- 理想气体方程

### 数学 (math) - 100 个
- 微积分 (积分、导数)
- 级数求和
- 欧拉公式
- 三角恒等式

### 电化学 (electrochemistry) - 100 个
- 电流密度公式
- Nernst 方程
- 法拉第定律
- 效率计算

### 材料科学 (materials) - 100 个
- 应力 - 应变公式
- 杨氏模量
- 密度计算
- 材料性能公式

---

## ⚙️ 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--output` | string | `data/handwritten/` | 输出目录 |
| `--num-samples` | int | 500 | 生成样本数量 |
| `--domains` | string | `all` | 领域选择 (逗号分隔) |
| `--styles` | string | `all` | 书写风格 (逗号分隔) |
| `--augment` | flag | False | 启用数据增强 |
| `--image-size` | string | `512x256` | 图像分辨率 |
| `--seed` | int | 42 | 随机种子 |

---

## 🔧 数据增强

使用 `--augment` 参数启用以下增强操作：

| 增强类型 | 描述 | 参数范围 |
|----------|------|----------|
| **旋转** | 随机旋转 | ±15° |
| **缩放** | 随机缩放 | 0.8-1.2x |
| **平移** | 随机平移 | ±10% |
| **噪声** | 高斯噪声 | σ=0-0.1 |
| **模糊** | 轻微模糊 | kernel=1-3 |
| **对比度** | 对比度调整 | 0.8-1.2 |

---

## 📝 使用场景

1. **模型微调**: 训练手写公式识别模型
2. **数据增强**: 扩展现有数据集
3. **领域适配**: 针对特定领域生成样本
4. **压力测试**: 测试模型鲁棒性

---

## 🔧 依赖

```
Pillow>=9.0.0
numpy>=1.23.0
```

### 安装依赖

```bash
pip install Pillow numpy
```

---

## 📄 相关文档

- `todo-030` - 手写公式识别支持任务
- `11-research/LIG-Stability-ML-Framework.md` - ML 框架文档

---

**维护者**: Claw (AI Research OS)  
**最后更新**: 2026-03-10
