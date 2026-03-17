# CNT PubMed 检索实施指南

**创建日期:** 2026-03-13 18:44  
**版本:** v1.0

---

## 🔍 PubMed 检索式

### 基础检索式

```
("carbon nanotube" OR "CNT" OR "SWCNT" OR "MWCNT") 
AND ("conductivity" OR "conductive" OR "electrical property") 
AND ("prediction" OR "model" OR "machine learning")
AND ("2020/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
```

### 精简检索式 (如果结果过少)

```
("carbon nanotube" OR "CNT") 
AND ("conductivity" OR "electrical")
AND ("2020/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
```

### 扩展检索式 (如果结果过多)

```
("carbon nanotube" OR "CNT" OR "SWCNT" OR "MWCNT") 
AND ("conductivity" OR "conductive" OR "electrical property") 
AND ("prediction" OR "model" OR "machine learning" OR "regression" OR "neural network")
AND ("2020/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
AND ("full text"[Filter])
```

---

## 📋 检索步骤

### 步骤 1: 访问 PubMed

**URL:** https://pubmed.ncbi.nlm.nih.gov/

### 步骤 2: 输入检索式

复制基础检索式到搜索框

### 步骤 3: 筛选结果

**筛选条件:**
- 发表年份：2020-2026
- 文章类型：Journal Article
- 语言：English, Chinese

### 步骤 4: 导出文献

**导出格式:** PMID, 标题，摘要，作者，期刊，发表日期

**导出数量:** 每次最多 10000 条

---

## 📊 纳入/排除标准

### 纳入标准

1. 报告 CNT 导电性数据
2. 提供 CNT 物理参数 (长度/直径/纯度等)
3. 人类语言：英文或中文
4. 发表年份：2020-2026
5. 全文可获取

### 排除标准

1. 仅定性描述，无定量数据
2. 综述文章 (除非引用原始数据)
3. 无法获取全文
4. 数据不完整
5. 重复发表

---

## 📝 数据提取模板

| 字段 | 来源 | 说明 |
|------|------|------|
| PMID | PubMed ID | 文献唯一标识 |
| 标题 | 文献标题 | - |
| 摘要 | 文献摘要 | 用于初步筛选 |
| 作者 | 作者列表 | 识别核心研究团队 |
| 期刊 | 期刊名称 | 评估期刊质量 |
| 发表日期 | 发表日期 | 时间趋势分析 |
| CNT 类型 | 全文 | SWCNT/MWCNT |
| 长度 | 全文 | μm |
| 直径 | 全文 | nm |
| 纯度 | 全文 | % |
| 导电性 | 全文 | S/m |

---

## 🔧 自动化工具

### 1. Biopython Entrez

```python
from Bio import Entrez

Entrez.email = "your_email@example.com"
handle = Entrez.esearch(
    db="pubmed",
    term="YOUR_SEARCH_QUERY",
    retmax=10000
)
record = Entrez.read(handle)
pmids = record["IdList"]
```

### 2. PubMed API (直接 HTTP)

```python
import requests

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
params = {
    "db": "pubmed",
    "term": "YOUR_SEARCH_QUERY",
    "retmax": 10000,
    "retmode": "json"
}
response = requests.get(url, params=params)
data = response.json()
```

---

## ⚠️ 注意事项

1. **API 限制:** PubMed API 有请求频率限制 (每秒不超过 10 次)
2. **邮箱必填:** Entrez 需要邮箱地址
3. **数据备份:** 定期备份检索结果
4. **去重:** 不同检索式可能有重复结果

---

## 📊 预期结果

| 检索式 | 预计结果 | 目标纳入 |
|--------|----------|----------|
| 基础检索式 | 500-1000 篇 | 150+ 篇 |
| 精简检索式 | 2000-5000 篇 | 200+ 篇 |
| 扩展检索式 | 200-500 篇 | 100+ 篇 |

---

*Created:* 2026-03-13 18:44  
*Status:* ✅ PubMed 检索实施指南完成  
*Next:* 执行检索 + 数据提取
