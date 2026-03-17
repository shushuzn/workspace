# 预印本发布计划

**平台:** arXiv  
**分类:** 
- cond-mat.mtrl-sci (材料科学)
- cs.LG (机器学习)

**计划发布时间:** 2026-03-10 (投稿 Carbon 前)

---

## 📋 arXiv 提交流程

### 1. 准备文件

**必须文件:**
- [ ] manuscript.pdf (LaTeX 编译或 Markdown 转 PDF)
- [ ] 图表文件 (单独上传)
- [ ] 补充材料 (可选)

**推荐格式:**
- 使用 LaTeX 模板 (Carbon/Elsevier)
- 或从 Markdown 导出 PDF

### 2. 创建 arXiv 账号

- [ ] 注册账号
- [ ] 验证邮箱
- [ ] 完善作者信息

### 3. 提交步骤

1. 登录 arXiv
2. 选择 "Submit"
3. 填写元数据:
   - 标题
   - 作者 (Claw + 通信作者)
   - 摘要
   - 关键词
   - 分类 (cond-mat.mtrl-sci, cs.LG)
4. 上传文件
5. 预览
6. 提交

### 4. 获取 arXiv ID

提交后 24-48 小时获得 arXiv ID，格式：
```
arXiv:2603.xxxxx [cond-mat.mtrl-sci]
```

---

## 📄 论文 PDF 准备

### 选项 A: LaTeX

**模板:** Elsevier/Carbon LaTeX 模板

```latex
\documentclass[review]{elsarticle}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{natbib}

\journal{Carbon}

\begin{document}

\begin{frontmatter}
\title{Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression}

\author[1]{Claw}
\author[2,*]{[用户姓名]}
\address[1]{OpenClaw Research Lab}
\address[2]{[用户机构]}

\begin{abstract}
[摘要内容]
\end{abstract}

\begin{keyword}
Laser-induced graphene \sep Gaussian process regression \sep Conductivity prediction \sep Machine learning \sep Uncertainty quantification
\end{keyword}

\end{frontmatter}

% 正文内容

\end{document}
```

### 选项 B: Markdown → PDF

使用 Pandoc:

```bash
pandoc *.md -o manuscript.pdf \
  --template eisvogel \
  --toc \
  --number-sections \
  --citeproc \
  --bibliography references_formatted.bib
```

---

## 📊 图表准备

**要求:**
- 格式：TIFF 或 EPS
- 分辨率：≥300 dpi (照片), ≥600 dpi (线图)
- 颜色模式：RGB

**导出脚本:**

```python
import matplotlib.pyplot as plt

# 高分辨率导出
plt.savefig('prediction.png', dpi=600, bbox_inches='tight')
plt.savefig('prediction.tiff', dpi=600, compression='lzw')
```

---

## 📝 元数据准备

### 标题
Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression

### 作者
- Claw¹
- [用户姓名]²*

### 单位
1. OpenClaw Research Lab
2. [用户机构]

### 通信作者
[用户姓名]  
Email: [待填写]

### 摘要
[使用 00_abstract.md 内容]

### 关键词
Laser-induced graphene; Gaussian process regression; Conductivity prediction; Machine learning; Uncertainty quantification; Materials informatics

### 分类
- cond-mat.mtrl-sci (主要)
- cs.LG (次要)

---

## 📅 时间规划

| 日期 | 任务 | 状态 |
|------|------|------|
| 2026-03-07 | 准备 PDF 初稿 | ⬜ |
| 2026-03-08 | 导出高分辨率图表 | ⬜ |
| 2026-03-09 | 创建 arXiv 账号 | ⬜ |
| 2026-03-10 | 提交 arXiv | ⬜ |
| 2026-03-12 | 获得 arXiv ID | ⬜ |
| 2026-03-15 | 投稿 Carbon (引用 arXiv ID) | ⬜ |

---

## 🔗 相关链接

- **arXiv 提交:** https://arxiv.org/submit/
- **arXiv 分类:** https://arxiv.org/classification/
- **Carbon LaTeX 模板:** [待查找]
- **Pandoc 下载:** https://pandoc.org/

---

*创建时间:* 2026-03-06 16:00
