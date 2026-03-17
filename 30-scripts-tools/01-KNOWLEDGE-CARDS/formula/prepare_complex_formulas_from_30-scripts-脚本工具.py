# 复杂公式数据集准备脚本

**目标:** 收集 200+ 复杂公式样本 (多行方程组/3D 矩阵/积分/求和)

---

## 数据来源

### 1. LIG 论文 (80 篇)
- 从已收集论文 PDF 提取公式
- 优先选择含数学推导的论文

### 2. 教科书/参考书
- 电磁学/材料科学/神经科学教材
- 公开教材 (OpenStax 等)

### 3. 在线资源
- arXiv 预印本
- Wikipedia 公式
- MathWorld

---

## 复杂公式分类

| 类型 | 数量目标 | 示例 |
|------|----------|------|
| **多行方程组** | 50 | `\begin{cases}...` |
| **3D 矩阵** | 30 | `\begin{bmatrix}3x3` |
| **多重积分** | 40 | `\iiint`, `\oint` |
| **求和/求积** | 40 | `\sum_{i=1}^n`, `\prod` |
| **分数嵌套** | 40 | `\frac{a}{\frac{b}{c}}` |
| **总计** | 200 | - |

---

## 使用方式

```python
# 从 PDF 提取
python prepare_complex_formulas.py --pdf-dir 90-archive/PDFs --output formula_dataset/

# 从在线资源收集
python prepare_complex_formulas.py --source wikipedia --output formula_dataset/

# 验证数据集
python prepare_complex_formulas.py --validate formula_dataset/
```

---

**状态:** 脚本框架  
**下一步:** 实际数据收集
