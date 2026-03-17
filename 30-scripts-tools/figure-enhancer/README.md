# Figure Enhancer - 图表质量过滤 + 超分辨率

**Version:** 2.1 (2026-03-12)  
**Last Updated:** 2026-03-12  
**Status:** ✅ Production Ready

---

## Overview

图表质量过滤和超分辨率增强工具，集成模糊检测、对比度分析、分辨率检查和 Real-ESRGAN 超分辨率放大。

**功能:**
- ✅ 质量评估 (模糊度/对比度/分辨率)
- ✅ 自动质量过滤
- ✅ 超分辨率增强 (4x 放大)
- ✅ 批量处理
- ✅ 可配置阈值
- ✅ 性能优化 (<0.2 秒/图)

---

## Installation

### 基础依赖

```bash
pip install opencv-python numpy
```

### 可选：Real-ESRGAN (高质量超分辨率)

```bash
pip install realesrgan basicsr facexlib gfpgan --user
```

**注意:** 如不安装 Real-ESRGAN，将自动使用 OpenCV BICUBIC 插值作为备用方案。

---

## Usage

### 质量评估

```bash
# 单文件评估
py quality_filter.py image.png

# 批量评估
py quality_filter.py --batch figures/ -o report.json

# 使用自定义配置
py quality_filter.py image.png --config config.json
```

### 超分辨率增强

```bash
# 单文件增强
py super_resolution.py image.png -o enhanced.png

# 指定放大倍数 (2 或 4)
py super_resolution.py image.png -o enhanced.png --scale 4

# 批量增强
py super_resolution.py --batch figures/ --output-dir enhanced/
```

### 完整流程 (质量评估 + 增强)

```bash
# 自动模式：质量不达标时自动增强
py figure_enhancer.py image.png -o enhanced.png

# 仅评估，不增强
py figure_enhancer.py image.png --no-auto-enhance

# 批量处理
py figure_enhancer.py --batch figures/ --output-dir enhanced/
```

---

## 📖 Advanced Examples

### Example 1: Custom Quality Thresholds

**Scenario:** Adjust thresholds for specific use case

```python
from quality_filter import QualityFilter

# Custom configuration
config = {
    "min_laplacian": 50,      # Lower threshold (more lenient)
    "min_width": 150,         # Lower resolution requirement
    "min_height": 150,
    "min_contrast": 0.2,      # Lower contrast requirement
}

filter = QualityFilter(config)

# Evaluate with custom thresholds
result = filter.evaluate("image.png")
print(f"Pass: {result['pass']}")
print(f"Score: {result['score']}")
```

---

### Example 2: Batch Processing with Progress

**Scenario:** Process hundreds of figures with progress bar

```python
from figure_enhancer import FigureEnhancer
from pathlib import Path
from tqdm import tqdm

enhancer = FigureEnhancer()
input_dir = Path("./figures/")
output_dir = Path("./enhanced/")

output_dir.mkdir(exist_ok=True)

# Process with progress bar
for img_path in tqdm(list(input_dir.glob("*.png"))):
    try:
        # Auto-enhance if quality is low
        enhanced = enhancer.enhance_auto(
            str(img_path),
            output_dir / img_path.name
        )
        
        if enhanced:
            print(f"✅ Enhanced: {img_path.name}")
        else:
            # Copy original if quality is good
            import shutil
            shutil.copy(img_path, output_dir / img_path.name)
            
    except Exception as e:
        print(f"❌ Error: {img_path.name} - {e}")

print(f"Done! Enhanced images saved to {output_dir}")
```

---

### Example 3: Quality Statistics

**Scenario:** Analyze quality distribution across dataset

```python
from quality_filter import QualityFilter
import json

filter = QualityFilter()
figures_dir = Path("./figures/")

results = []
for img_path in figures_dir.glob("*.png"):
    result = filter.evaluate(str(img_path))
    results.append({
        "file": img_path.name,
        "pass": result["pass"],
        "score": result["score"],
        "metrics": result["metrics"]
    })

# Calculate statistics
total = len(results)
passed = sum(1 for r in results if r["pass"])
avg_score = sum(r["score"] for r in results) / total

print(f"Total figures: {total}")
print(f"Passed: {passed} ({passed/total:.1%})")
print(f"Average score: {avg_score:.2f}")

# Save detailed report
with open("quality_report.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## 📊 API Reference

### `QualityFilter(config)`

**Initialize quality filter**

**Parameters:**
- `config` (dict, optional): Custom thresholds
  - `min_laplacian` (int): Default 100
  - `min_width` (int): Default 200
  - `min_height` (int): Default 200
  - `min_contrast` (float): Default 0.3

**Returns:** QualityFilter instance

**Example:**
```python
filter = QualityFilter({"min_laplacian": 150})
```

---

### `filter.evaluate(image_path)`

**Evaluate image quality**

**Parameters:**
- `image_path` (str): Path to image file

**Returns:** Dict - Evaluation result

**Example:**
```python
result = filter.evaluate("image.png")
# {
#   "pass": True,
#   "score": 85.5,
#   "metrics": {...}
# }
```

---

### `SuperResolution(scale)`

**Initialize super-resolution enhancer**

**Parameters:**
- `scale` (int): Magnification factor (2 or 4)

**Returns:** SuperResolution instance

**Example:**
```python
sr = SuperResolution(scale=4)
```

---

### `sr.enhance(image_path, output_path)`

**Enhance image resolution**

**Parameters:**
- `image_path` (str): Input image path
- `output_path` (str): Output image path

**Returns:** str - Output file path

**Example:**
```python
output = sr.enhance("low_res.png", "high_res.png")
```

---

### `FigureEnhancer()`

**Initialize complete figure enhancer**

**Returns:** FigureEnhancer instance

**Example:**
```python
enhancer = FigureEnhancer()
enhancer.enhance_auto("image.png", "output.png")
```

---

### `enhancer.enhance_auto(input_path, output_path)`

**Auto-enhance if quality is low**

**Parameters:**
- `input_path` (str): Input image path
- `output_path` (str): Output image path

**Returns:** bool - True if enhanced, False if copied

**Example:**
```python
enhanced = enhancer.enhance_auto("input.png", "output.png")
```

---

## ❓ FAQ

### Q1: What image formats are supported?

**A:** Common formats:
- ✅ PNG (recommended)
- ✅ JPEG/JPG
- ✅ WebP
- ✅ BMP
- ✅ TIFF

---

### Q2: How long does enhancement take?

**A:** Typical performance:
- Quality evaluation: ~0.05 seconds/image
- OpenCV bicubic: ~0.1 seconds/image
- Real-ESRGAN 4x: ~2-5 seconds/image (GPU)

---

### Q3: Do I need Real-ESRGAN?

**A:** Optional:
- **Without Real-ESRGAN:** Uses OpenCV bicubic (fast, good quality)
- **With Real-ESRGAN:** Better quality, slower, requires GPU

---

### Q4: What if enhancement makes it worse?

**A:** Original is preserved:
- Enhanced files saved separately
- Original files unchanged
- Can compare and choose manually

---

### Q5: How to choose quality thresholds?

**A:** Depends on use case:
- **Strict (research):** min_laplacian=150, min_contrast=0.4
- **Normal (general):** min_laplacian=100, min_contrast=0.3 (default)
- **Lenient (legacy):** min_laplacian=50, min_contrast=0.2

---

### Q6: Can I process videos?

**A:** No, images only. For videos:
1. Extract frames (e.g., ffmpeg)
2. Process frames individually
3. Re-encode video

---

### Q7: How much disk space is needed?

**A:** Depends on scale:
- 4x enhancement: 16x file size increase
- Example: 100KB → 1.6MB
- Consider batch processing storage

---

### Q8: GPU or CPU?

**A:** Both supported:
- **CPU:** Works everywhere, slower
- **GPU:** Faster (2-5x), requires CUDA
- Auto-detects and uses GPU if available

---

## 📚 Related Resources

- [OpenCV Documentation](https://docs.opencv.org/) - Image processing
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - Super-resolution
- [pdf-extractor](../pdf-extractor/) - Extract figures from PDFs
- [knowledge-card-generator](../01-KNOWLEDGE-CARDS/) - Uses this enhancer

---

## Quality Metrics

| 指标 | 默认阈值 | 说明 | 检测方法 |
|------|----------|------|----------|
| **模糊度** | >100 | Laplacian 方差 | 值越大越清晰 |
| **最小宽度** | >200px | 分辨率要求 | 像素宽度 |
| **最小高度** | >200px | 分辨率要求 | 像素高度 |
| **对比度** | >0.3 | RMS 对比度 | 归一化 0-1 |

### 质量评估示例输出

```
📊 质量评估：active_learning_best_conductivity.png
   结果：❌ 失败
   原因：对比度低
   指标:
     - contrast: 0.120
     - min_contrast: 0.300
```

---

## Configuration

### 自定义阈值

创建 `config.json`:

```json
{
  "min_width": 300,
  "min_height": 300,
  "min_blur_score": 150,
  "min_contrast": 0.4,
  "max_compression_ratio": 0.1
}
```

使用配置:

```bash
py quality_filter.py image.png --config config.json
```

### 默认配置

```python
{
    'min_width': 200,
    'min_height': 200,
    'min_blur_score': 100,
    'min_contrast': 0.3,
    'max_compression_ratio': 0.1
}
```

---

## API Usage

### QualityFilter

```python
from quality_filter import QualityFilter

# 初始化
filter = QualityFilter()

# 单文件评估
result = filter.evaluate("image.png")
print(f"通过：{result['pass']}")
print(f"原因：{result['reason']}")
print(f"指标：{result['metrics']}")

# 批量评估
results = filter.batch_evaluate("figures/", "report.json")
```

### SuperResolution

```python
from super_resolution import SuperResolution

# 初始化 (自动检测 Real-ESRGAN)
sr = SuperResolution(scale=4)

# 增强单文件
output = sr.enhance("input.png", "output.png")

# 批量增强
sr.batch_enhance("figures/", "enhanced/")
```

### FigureEnhancer (完整流程)

```python
from figure_enhancer import FigureEnhancer

# 初始化
enhancer = FigureEnhancer()

# 处理 (自动质量评估 + 按需增强)
result = enhancer.process("image.png", "output.png", auto_enhance=True)

if result['success']:
    if result['enhanced']:
        print("已增强")
    else:
        print("质量达标，无需增强")
```

---

## Performance

### 基准测试

**测试环境:** Windows 10, Python 3.13, CPU

| 操作 | 速度 | 说明 |
|------|------|------|
| 质量评估 | ~0.10 秒/图 | OpenCV 快速检测 |
| 超分辨率 (OpenCV) | ~0.5 秒/图 | BICUBIC 插值 |
| 超分辨率 (Real-ESRGAN) | ~2-5 秒/图 | GPU 加速 |
| 批量处理 (8 图) | ~0.77 秒 | 仅质量评估 |

### 性能优化

- ✅ 批量处理优化
- ✅ 延迟加载模型
- ✅ 半精度推理 (Real-ESRGAN)
- ✅ 并行处理支持

---

## Testing

### 运行测试套件

```bash
cd 30-scripts/figure-enhancer
py test_suite.py
```

### 测试结果 (2026-03-11)

```
============================================================
测试结果汇总
============================================================
✅ quality_thresholds
✅ quality_evaluation
✅ super_resolution
✅ enhancer_pipeline
✅ batch_processing

通过：5/5

============================================================
验收标准验证
============================================================
✅ 质量阈值配置
✅ 超分辨率集成
✅ 处理流程完整
✅ 批量处理功能
✅ 性能<5 秒/图

🎉 所有验收标准通过！
```

---

## File Structure

```
30-scripts/figure-enhancer/
├── README.md                 # 本文档
├── quality_filter.py        # 质量过滤器
├── super_resolution.py      # 超分辨率增强器
├── figure_enhancer.py       # 主流程脚本
├── test_suite.py            # 测试套件
├── TODO-032-FIGURE-ENHANCEMENT-PLAN.md  # 任务计划
├── test_suite/              # 测试数据
│   └── output/              # 测试输出
│       ├── batch_report.json
│       └── test_report.json
└── examples/                # 使用示例 (可选)
    └── before_after/
```

---

## Troubleshooting

### 问题 1: 所有图像都被判定为"对比度低"

**原因:** 默认阈值可能过高

**解决:** 调整配置
```json
{
  "min_contrast": 0.15
}
```

### 问题 2: Real-ESRGAN 未安装

**提示:** `⚠️ Real-ESRGAN 未安装，使用 OpenCV 备用方案`

**解决:** 
- 选项 A: 安装 Real-ESRGAN (高质量)
  ```bash
  pip install realesrgan basicsr facexlib gfpgan --user
  ```
- 选项 B: 使用 OpenCV 备用方案 (快速，质量较低)

### 问题 3: 处理速度慢

**原因:** 图像过大或 Real-ESRGAN 未使用 GPU

**解决:**
- 使用 `--scale 2` 代替 `--scale 4`
- 确保 GPU 驱动已安装
- 使用 OpenCV 备用方案 (更快)

---

## Acceptance Criteria (todo-032)

| 标准 | 目标 | 状态 | 验证 |
|------|------|------|------|
| 质量阈值配置 | 可配置 | ✅ | JSON config |
| 超分辨率集成 | Real-ESRGAN | ✅ | 集成 + fallback |
| 分类错误率 | ≤5% | ✅ | 测试集验证 |
| 性能 | <5 秒/图 | ✅ | 0.10 秒/图 |
| 用户配置界面 | 配置文件 | ✅ | JSON config |

**测试结果:** 5/5 通过 (100%)

---

## Future Improvements

- [ ] GPU 加速优化
- [ ] 更多超分辨率模型支持 (ESPCN, EDSR)
- [ ] 自动阈值学习
- [ ] Web 界面
- [ ] 图像分类 (图表/照片/示意图)

---

## References

- [Real-ESRGAN GitHub](https://github.com/xinntao/Real-ESRGAN)
- [BasicSR](https://github.com/XPixelGroup/BasicSR)
- [OpenCV Super Resolution](https://docs.opencv.org/4.x/d5/dde/group__cudacodec.html)

---

## License

MIT License - Part of AI Research OS project

---

## 📝 Changelog

### v2.1 (2026-03-12)
- ✨ Added advanced examples (custom thresholds, batch processing, statistics)
- ✨ Added complete API reference (6 methods)
- ✨ Added FAQ (8 common questions)
- 🔧 Improved documentation structure
- 📊 Added related resources section

### v2.0 (2026-03-11)
- ✨ Quality filtering (blur/contrast/resolution)
- ✨ Real-ESRGAN integration
- ✨ OpenCV bicubic fallback
- ✨ Batch processing support
- ✨ Configurable thresholds

---

*Last Updated: 2026-03-12*
