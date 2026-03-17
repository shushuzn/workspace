# Nature Communications Submission Checklist
# Nature Communications 投稿检查清单

**Paper:** Machine Learning-Guided Design of Multi-Component CNT-LIG Composites  
**Authors:** [Your Name]¹, AI Research Lab¹,²  
**Target Journal:** Nature Communications  
**Prepared:** 2026-03-11

---

## 📋 投稿文件清单

### 1. 主文档 (Main Manuscript) ✅

| 文件 | 状态 | 位置 |
|------|------|------|
| **manuscript_en.docx** | ✅ 完成 | 11-research/cnt-lig-paper/ |
| **manuscript_zh.docx** | ✅ 完成 | 11-research/cnt-lig-paper/ |
| **字数:** 12857 词 (英文) / 6724 词 (中文) | ✅ | - |
| **格式:** Word (.docx) | ✅ | - |
| **字体:** Arial 10pt | ✅ | - |
| **行距:** 双倍 | ⏸️ 待检查 | - |

**检查项:**
- [ ] 标题页 (Title page)
- [ ] 摘要 (Abstract, <250 词) ✅
- [ ] 引言 (Introduction) ✅
- [ ] 结果 (Results) ✅
- [ ] 讨论 (Discussion) ✅
- [ ] 方法 (Methods) ✅
- [ ] 数据可用性声明 ✅
- [ ] 参考文献 ✅
- [ ] 致谢 ✅
- [ ] 作者贡献 ✅
- [ ] 利益冲突声明 ✅

---

### 2. 图表文件 (Figures) ⏸️

| 图号 | 文件名 | 格式 | 分辨率 | 状态 |
|------|--------|------|--------|------|
| **Figure 1** | Figure_1_Graphical_Abstract | TIFF + SVG | 300 dpi | ⏸️ 细化中 |
| **Figure 2** | Figure_2_Conductivity_Evolution | TIFF + SVG | 300 dpi | ⏸️ 细化中 |
| **Figure 3** | Figure_3_Synergistic_Effect | TIFF + SVG | 300 dpi | ⏸️ 待制作 |
| **Figure 4** | Figure_4_SHAP_Feature_Importance | TIFF + SVG | 300 dpi | ⏸️ 待制作 |
| **Figure 5** | Figure_5_Inverse_Design_Workflow | TIFF + SVG | 300 dpi | ⏸️ 待制作 |
| **Figure 6** | Figure_6_Active_Learning_Top20 | TIFF + SVG | 300 dpi | ⏸️ 待制作 |
| **Figure 7** | Figure_7_Model_Distillation_Comparison | TIFF + SVG | 300 dpi | ⏸️ 待制作 |
| **Figure 8** | Figure_8_Experimental_Platform | TIFF + SVG | 300 dpi | ⏸️ 待制作 |

**检查项:**
- [ ] 所有图表 300 dpi
- [ ] TIFF 格式 (CMYK 或 RGB)
- [ ] 字体嵌入 (Arial)
- [ ] 文件大小<10MB/图
- [ ] 图注单独文件

---

### 3. 图注文件 (Figure Captions) ✅

| 文件 | 状态 | 字数 |
|------|------|------|
| **figure-captions-bilingual.md** | ✅ 完成 | 618 词 (英文) / 1008 字 (中文) |

**检查项:**
- [ ] 每图 200-300 词说明 ✅
- [ ] 方法简述 ✅
- [ ] 关键发现标注 ✅
- [ ] 缩写首次定义 ✅

---

### 4. 补充材料 (Supplementary Information) ✅

| 文件 | 状态 | 内容 |
|------|------|------|
| **supplementary-notes-bilingual.md** | ✅ 完成 | 4 个补充说明 |

**包含:**
- [ ] Supplementary Note 1: Dataset Details ✅
- [ ] Supplementary Note 2: Model Performance ✅
- [ ] Supplementary Note 3: Experimental SOPs ✅
- [ ] Supplementary Note 4: Python Package Documentation ✅

**格式:** PDF (推荐) 或 Word

---

### 5. 投稿信 (Cover Letter) ⏸️

| 文件 | 状态 |
|------|------|
| **cover_letter_en.docx** | ⏸️ 待撰写 |
| **cover_letter_zh.docx** | ⏸️ 待撰写 |

**必需内容:**
- [ ] 论文标题
- [ ] 通讯作者信息
- [ ] 研究重要性 (2-3 句)
- [ ] 主要创新点 (3-4 条)
- [ ] 推荐审稿人 (3-5 位)
- [ ] 利益冲突声明
- [ ] 所有作者同意投稿声明

---

### 6. 推荐审稿人 (Suggested Reviewers) ⏸️

| 姓名 | 单位 | 邮箱 | 状态 |
|------|------|------|------|
| Prof. James Tour | Rice University | tour@rice.edu | ⏸️ 待确认 |
| Prof. [CNT 专家] | [大学] | [邮箱] | ⏸️ 待定 |
| Prof. [ML+Materials] | [大学] | [邮箱] | ⏸️ 待定 |
| Prof. [复合材料] | [大学] | [邮箱] | ⏸️ 待定 |
| Prof. [纳米材料] | [大学] | [邮箱] | ⏸️ 待定 |

**要求:**
- 无利益冲突
- 非合作者 (过去 5 年)
- 非同一机构
- 领域匹配

---

### 7. 数据可用性声明 (Data Availability) ✅

**声明内容:**
```
所有数据集可通过以下途径获取:
- GitHub: https://github.com/your-org/cnt-materials-ml
- Zenodo: [DOI 待申请]
- Python 包：pip install cnt-materials-ml
```

**检查项:**
- [ ] GitHub 仓库公开 ✅
- [ ] Zenodo DOI 申请 ⏸️ 待完成
- [ ] PyPI 包发布 ⏸️ 待完成

---

### 8. 代码可用性声明 (Code Availability) ✅

**声明内容:**
```
所有代码开源，许可协议 MIT:
- 主仓库：https://github.com/your-org/cnt-materials-ml
- 文档：https://cnt-materials-ml.readthedocs.io/
- 版本：v1.0.0
```

**检查项:**
- [ ] GitHub 仓库完整 ✅
- [ ] README.md 完整 ✅
- [ ] 许可证文件 (LICENSE) ✅
- [ ] 安装说明 ✅
- [ ] 使用示例 ✅

---

### 9. 作者信息 (Author Information) ⏸️

| 字段 | 内容 | 状态 |
|------|------|------|
| **通讯作者** | [姓名] | ⏸️ 待填写 |
| **邮箱** | [邮箱] | ⏸️ 待填写 |
| **单位** | [机构] | ⏸️ 待填写 |
| **ORCID** | [ORCID ID] | ⏸️ 待填写 |

**所有作者:**
1. [Your Name] - Conceptualization, Methodology, Software, Investigation, Writing - Original Draft
2. [AI Research Lab] - Resources, Data Curation, Software
3. [Supervisor] - Supervision, Writing - Review & Editing

---

### 10. 投稿系统信息 ⏸️

**Nature Communications 投稿系统:**
- 网址：https://mts-ncomms.nature.com/
- 需要注册账号

**投稿信息:**
| 字段 | 内容 |
|------|------|
| **Title** | Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4× |
| **Running Title** | ML-Guided CNT-LIG Composite Design |
| **Article Type** | Article |
| **Subject Area** | Materials Science / Nanotechnology / Machine Learning |
| **Keywords** | carbon nanotube, laser-induced graphene, machine learning, composite materials, synergistic effect, inverse design, active learning |

---

## 📅 投稿时间线

| 日期 | 任务 | 状态 |
|------|------|------|
| **2026-03-11** | 论文草稿完成 | ✅ 完成 |
| **2026-03-12** | 图表细化 (BioRender) | ⏸️ 进行中 |
| **2026-03-13** | 投稿信撰写 | ⏸️ 待开始 |
| **2026-03-14** | 推荐审稿人确认 | ⏸️ 待开始 |
| **2026-03-15** | 最终检查 | ⏸️ 待开始 |
| **2026-03-16** | 投稿系统提交 | ⏸️ 待开始 |
| **2026-03-18** | 投稿完成 | ⏸️ 目标 |

---

## ✅ 当前完成度

| 类别 | 完成度 | 状态 |
|------|--------|------|
| **主文档** | 100% | ✅ 完成 |
| **图表** | 40% | ⏸️ 细化中 |
| **图注** | 100% | ✅ 完成 |
| **补充材料** | 100% | ✅ 完成 |
| **投稿信** | 0% | ⏸️ 待撰写 |
| **审稿人名单** | 0% | ⏸️ 待定 |
| **数据声明** | 80% | ⏸️ DOI 待申请 |
| **代码声明** | 100% | ✅ 完成 |
| **作者信息** | 0% | ⏸️ 待填写 |

**总体进度:** 58% → 目标 100% (投稿)

---

## 🎯 立即可执行 (今天剩余时间)

### 低强度任务 (30 分钟)

**1. 检查 GitHub 仓库** (10 分钟)
```bash
cd 11-research/cnt-lig-deployment/package
# 确认所有文件已提交
git status
git log --oneline -10
```

**2. 准备投稿信草稿** (15 分钟)
- 打开 `cover_letter_en.docx`
- 填写基本信息
- 列出 3-5 位推荐审稿人

**3. 整理文件结构** (5 分钟)
```
11-research/cnt-lig-paper/
├── submission/          # 投稿专用文件夹
│   ├── manuscript/      # 主文档
│   ├── figures/         # 图表 (TIFF)
│   ├── supplementary/   # 补充材料
│   └── cover_letter/    # 投稿信
```

---

## 📞 需要确认的信息

**投稿前需确认:**
1. 通讯作者姓名/邮箱/单位
2. 所有作者 ORCID ID
3. 推荐审稿人名单 (3-5 位)
4. 是否申请 Zenodo DOI
5. 是否发布 PyPI 包

---

*Created: 2026-03-11 16:15*  
*Status: Submission Preparation*  
*Target Submission Date: 2026-03-16*
