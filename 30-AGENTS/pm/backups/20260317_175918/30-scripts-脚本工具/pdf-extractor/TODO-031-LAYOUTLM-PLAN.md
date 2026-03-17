# PDF 解析优化 - LayoutLM 集成计划

**任务 ID:** todo-031  
**优先级:** 🟡 MEDIUM  
**预计时间:** 1-2 周  
**创建日期:** 2026-03-10

---

## 📋 任务描述

集成高级布局分析模型 (LayoutLM/LayoutLMv3)，提升双栏/复杂排版 PDF 解析准确率至 98%。

---

## 🎯 验收标准

| 标准 | 目标 | 验证方法 |
|------|------|----------|
| LayoutLM 集成 | ✅ 完成 | 代码审查 |
| 双栏 PDF 准确率 | ≥95% | 测试集验证 |
| 复杂排版识别率 | ≥90% | 测试集验证 |
| 表格提取准确率 | ≥85% | 人工抽检 |
| 公式提取准确率 | ≥90% | 人工抽检 |
| 处理速度 | <30 秒/页 | 性能测试 |
| 文档完善 | ✅ 完成 | README + 使用示例 |

---

## 📚 技术方案

### 方案 A: Marker (已实施 ✅)

**优势:**
- 专为 PDF→Markdown 设计
- 支持公式/表格/图表
- 简单易用，无需复杂配置
- 内置布局分析

**依赖:**
```bash
pip install marker-pdf --user
```

**集成方式:**
```bash
# 命令行使用
marker_single input.pdf --output_dir output/

# Python API
from marker.convert import convert_single_pdf
from marker.models import load_all_models

model_refs = load_all_models()
full_text, images, out_meta = convert_single_pdf("input.pdf", model_refs)
```

**状态:** ✅ 2026-03-10 安装完成

### 方案 B: PaddleOCR + Layout 分析

**优势:**
- 中文支持好
- OCR + 布局一体化
- 轻量级

**依赖:**
```bash
pip install paddlepaddle
pip install paddleocr
```

### 方案 C: Marker (新兴方案)

**优势:**
- 专为 PDF→Markdown 设计
- 支持公式/表格/图表
- 简单易用

**依赖:**
```bash
pip install marker-pdf
```

---

## 📁 文件结构

```
30-scripts/pdf-extractor/
├── README.md                 # 使用文档
├── config.yaml              # 配置文件
├── layoutlm_extractor.py    # LayoutLM 主脚本
├── paddle_extractor.py      # PaddleOCR 备用
├── marker_extractor.py      # Marker 备用
├── test_suite/              # 测试集
│   ├── double_column/       # 双栏 PDF 样本
│   ├── tables/              # 含表格 PDF
│   ├── formulas/            # 含公式 PDF
│   └── mixed/               # 混合复杂排版
├── benchmarks/              # 性能基准
│   └── accuracy_report.md
└── examples/                # 使用示例
    └── sample_output.md
```

---

## 📊 测试集构建

### 双栏 PDF 样本 (20 个)
- arXiv 论文 (CS/Physics)
- IEEE 论文
- ACM 论文

### 表格样本 (15 个)
- 数据表格
- 对比表格
- 复杂嵌套表格

### 公式样本 (20 个)
- 行内公式
- 块级公式
- 多行方程组
- 矩阵/积分

### 混合排版 (10 个)
- 论文首页
- 图表 + 文字混排
- 多栏 + 公式 + 表格

---

## 📈 实施步骤

### Week 1: 基础集成
- [ ] Day 1-2: LayoutLMv3 环境配置
- [ ] Day 3-4: 基础提取脚本开发
- [ ] Day 5: 单元测试编写

### Week 2: 优化与测试
- [ ] Day 6-7: 测试集验证
- [ ] Day 8-9: 性能优化
- [ ] Day 10: 文档完善

---

## 🔧 代码示例

```python
#!/usr/bin/env python3
# layoutlm_extractor.py - PDF 布局分析提取器

import fitz  # PyMuPDF
from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
import torch

class PDFLayoutExtractor:
    def __init__(self, model_name="microsoft/layoutlmv3-base"):
        self.processor = LayoutLMv3Processor.from_pretrained(model_name)
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(model_name)
        
    def extract_page(self, pdf_path, page_num=0):
        """提取单页内容"""
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        # 获取页面图像
        pix = page.get_pixmap()
        image = pix.tobytes("png")
        
        # 获取文本和边界框
        blocks = page.get_text("dict")["blocks"]
        words = []
        boxes = []
        
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        words.append(span["text"])
                        boxes.append(span["bbox"])
        
        # LayoutLM 处理
        inputs = self.processor(
            image=image,
            words=words,
            boxes=boxes,
            return_tensors="pt"
        )
        
        outputs = self.model(**inputs)
        predictions = outputs.logits.argmax(-1)
        
        # 解析预测结果
        return self._parse_predictions(predictions, words, boxes)
    
    def _parse_predictions(self, predictions, words, boxes):
        """解析模型预测，生成结构化输出"""
        # TODO: 实现布局解析逻辑
        pass

if __name__ == "__main__":
    extractor = PDFLayoutExtractor()
    result = extractor.extract_page("sample.pdf", 0)
    print(result)
```

---

## 📏 评估指标

### 准确率指标
- **布局识别准确率:** 正确识别文本块/图表/表格的比例
- **阅读顺序准确率:** 正确排序文本块的比例
- **公式提取准确率:** LaTeX 转换正确率
- **表格结构准确率:** 行列结构正确率

### 性能指标
- **处理速度:** 秒/页
- **内存占用:** MB
- **GPU 利用率:** %

---

## 🔗 相关资源

- [LayoutLMv3 GitHub](https://github.com/microsoft/unilm/tree/master/layoutlmv3)
- [LayoutLMv3 Paper](https://arxiv.org/abs/2204.08387)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [Marker PDF](https://github.com/VikParuchuri/marker)

---

## 📝 进度日志

### 2026-03-10
- ✅ 任务规划完成
- ✅ 技术方案确定 (LayoutLMv3)
- ✅ 测试集设计完成
- ⏸️ 等待开始实施

---

*最后更新：2026-03-10*
