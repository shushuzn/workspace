# 参考文献格式检查报告

**检查日期:** 2026-03-06  
**目标期刊:** Carbon (Elsevier)  
**参考文献总数:** 33 篇

---

## 📋 Carbon 期刊标准格式

Elsevier Carbon 期刊使用**数字顺序编码制**，标准格式如下：

### 期刊文章
```
[1] Author A, Author B, Author C. Title of the paper. Journal Name 2014;5(1):5714-5720.
```

或更详细的格式：
```
[1] Author A, Author B, Author C. Title of the paper. Journal Name. 2014;5(1):5714-5720.
```

### 书籍
```
[2] Author A. Title of the Book. Publisher; 2006.
```

---

## ⚠️ 当前格式问题

### 问题 1: 年份位置不正确

**当前格式 (APA 风格):**
```
[1] Lin, J., Peng, Z., Liu, Y. (2014). Laser-induced porous graphene films. Nature Communications, 5(1), 5714.
```

**Carbon 标准格式:**
```
[1] Lin J, Peng Z, Liu Y, et al. Laser-induced porous graphene films from commercial polymers. Nature Communications. 2014;5(1):5714.
```

**差异:**
- ❌ 年份不应在作者后用括号 `(2014)`
- ❌ 不应使用 `&` 连接最后作者
- ✅ 年份应放在期刊名之后 `2014;`
- ✅ 使用 `et al.` 代替多位作者

---

### 问题 2: 作者姓名格式

**当前格式:**
```
Lin, J., Peng, Z., Liu, Y., Ruiz-Zepeda, F., Ye, R., Samuel, E. L., ... & Tour, J. M.
```

**Carbon 标准:**
```
Lin J, Peng Z, Liu Y, Ruiz-Zepeda F, Ye R, Samuel ELG, Tour JM
```

或 (超过 6 位作者时):
```
Lin J, Peng Z, Liu Y, et al.
```

---

### 问题 3: 期刊名格式

**当前格式:**
```
*Nature Communications*, 5(1), 5714.
```

**Carbon 标准:**
```
Nature Communications. 2014;5(1):5714.
```

- ❌ 不需要斜体标记 `*`
- ❌ 年份不应在作者后
- ✅ 年份在期刊名后，用分号 `;`

---

### 问题 4: 页码格式

**当前格式:**
```
5(1), 5714.
```

**Carbon 标准:**
```
2014;5(1):5714.
```

或页码范围:
```
2014;5(1):5714-5720.
```

---

## ✅ 格式正确的部分

- ✅ 使用数字编号 `[1]`, `[2]`, `[3]`...
- ✅ 按引用顺序排列
- ✅ 包含完整的作者、标题、期刊、卷期、页码信息

---

## 🔧 修正建议

### 方案 A: 使用 BibTeX + 样式文件 (推荐)

1. 使用现有的 `references_formatted.bib` 文件
2. 使用 Elsevier 标准样式 `elsarticle-num.bst`
3. 自动生成符合 Carbon 格式的参考文献

**命令:**
```bash
# 使用 LaTeX + BibTeX
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

### 方案 B: 手动转换格式

转换规则:
1. 作者姓名：`Lin, J.` → `Lin J` (去掉逗号)
2. 年份移动：`(2014).` → 移到期刊名后 `2014;`
3. 多位作者：超过 6 位用 `et al.` 代替
4. 页码格式：`, 5714.` → `:5714.`

---

## 📊 需要修正的参考文献

| 编号 | 当前状态 | 修正优先级 |
|------|----------|------------|
| [1-13] | LIG 技术 | 🔴 高 |
| [14-22] | 机器学习应用 | 🔴 高 |
| [23-30] | GP 与在线学习 | 🔴 高 |
| [31-33] | 方法与工具 | 🟡 中 |

---

## 📝 修正示例

### 示例 1: 期刊文章

**修正前:**
```
[1] Lin, J., Peng, Z., Liu, Y., Ruiz-Zepeda, F., Ye, R., Samuel, E. L., ... & Tour, J. M. (2014). 
Laser-induced porous graphene films from commercial polymers. *Nature Communications*, 5(1), 5714.
```

**修正后:**
```
[1] Lin J, Peng Z, Liu Y, Ruiz-Zepeda F, Ye R, Samuel ELG, Tour JM. 
Laser-induced porous graphene films from commercial polymers. Nature Communications. 2014;5(1):5714.
```

### 示例 2: 书籍

**修正前:**
```
[32] Rasmussen, C. E., & Williams, C. K. I. (2006). *Gaussian Processes for Machine Learning*. MIT Press.
```

**修正后:**
```
[32] Rasmussen CE, Williams CKI. Gaussian Processes for Machine Learning. MIT Press; 2006.
```

---

## 🎯 下一步行动

1. **决定格式方案:** BibTeX 自动生成 vs 手动转换
2. **执行转换:** 33 篇参考文献全部修正
3. **最终校对:** 检查 DOI、页码、作者姓名拼写

---

*报告生成时间：2026-03-06 19:15*
