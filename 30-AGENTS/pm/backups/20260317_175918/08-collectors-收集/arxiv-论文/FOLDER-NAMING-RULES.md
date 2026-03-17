# 40-arxiv 文件夹命名规范

**版本:** v1.0  
**更新日期:** 2026-03-11

---

## 📁 一级文件夹（40-arxiv 直接子目录）

### ✅ 允许的文件夹

| 文件夹 | 用途 | 说明 |
|--------|------|------|
| `daily/` | 每日收集的论文 | 按日期分子文件夹 |
| `lig-outreach/` | LIG 科普笔记 | 领域特定输出 |
| `Archive/` | 归档文件 | 历史数据/备份 |

### ❌ 禁止的命名

- ❌ 中文字符（如 `lig 科普/`）
- ❌ 乱码字符
- ❌ 临时文件夹（如 `temp/`, `migr/`）
- ❌ 无意义命名

---

## 📁 二级文件夹规范

### daily/ 结构

```
40-arxiv/daily/
├── 2026-03-05/          # 日期格式：YYYY-MM-DD
│   ├── csAI/            # arXiv 分类代码
│   ├── csLG/
│   └── csCV/
├── 2026-03-06/
└── 2026-03-07/
```

**规则:**
1. 日期文件夹：`YYYY-MM-DD` 格式
2. 学科分类：使用 arXiv 官方分类代码（csAI, csLG, csCV, csCL 等）
3. 文件名：`{arXivID}-{标题前 50 字}.md`

### Archive/ 结构

```
40-arxiv/Archive/
├── 2026-03/             # 月份归档
│   ├── 2026-03-02-priority.md
│   └── 2026-03-03/      # 按日期分子目录
└── lig-outreach-backup/ # 临时备份（完成后删除）
```

**规则:**
1. 月份文件夹：`YYYY-MM` 格式
2. 临时备份：任务完成后立即删除

### 领域特定文件夹

```
40-arxiv/
├── lig-outreach/        # LIG 科普笔记
├── graphene-analysis/   # 石墨烯分析（示例）
└── cnt-research/        # 碳纳米管研究（示例）
```

**命名规则:**
1. 全小写英文
2. 连字符分隔：`domain-type`
3. 避免缩写（除非通用如 AI/ML）

---

## 📄 文件命名规范

### 科普笔记

```
lig-outreach-01.md       # ✅ 两位数字编号
lig-outreach-02.md
...
lig-outreach-32.md
README.md                # 索引文件
```

### 每日论文

```
2026-03-05-125206-ODAR Principled Adaptive Routing for LLM Reasoning.md
```

**格式:** `{日期}-{arXivID}-{标题}.md`

### 数据文件

```
lig-papers-20260309-143807.json    # 时间戳精确到秒
LIG-domain-data-20260310-224319.json
```

**格式:** `{领域}-{数据类型}-{YYYYMMDD-HHMMSS}.{ext}`

---

## 🧹 清理规则

### 定期清理

| 类型 | 保留期限 | 操作 |
|------|----------|------|
| `daily/`临时文件 | 7 天 | 迁移后删除 |
| `Archive/*-backup/` | 任务完成 | 立即删除 |
| `__pycache__/` | - | 每次 Git 前清理 |
| `*.pyc` | - | 每次 Git 前清理 |

### Git 前检查

```bash
# 检查乱码文件夹
ls 40-arxiv/ | grep -P '[^\x00-\x7F]'

# 检查临时文件夹
ls 40-arxiv/ | grep -E '(temp|migr|backup|old)'

# 清理 Python 缓存
find 40-arxiv/ -name "__pycache__" -type d -exec rm -rf {} +
```

---

## ✅ 当前状态 (2026-03-11)

```
40-arxiv/
├── Archive/                 ✅ 规范
│   └── 2026-03/            ✅ 规范
├── daily/                   ✅ 规范
│   ├── 2026-03-05/         ✅ 规范
│   ├── 2026-03-06/         ✅ 规范
│   ├── 2026-03-07/         ✅ 规范
│   └── 2026-03-08/         ✅ 规范
└── lig-outreach/            ✅ 规范
    ├── README.md
    └── lig-outreach-01.md → lig-outreach-46.md
```

**已清理:**
- ❌ `lig 科普/` (中文命名)
- ❌ `lig/` (乱码)
- ❌ `daily/2026/03/` (嵌套错误)
- ❌ `daily/migr/at/` (临时文件夹)
- ❌ `Archive/lig-outreach-backup/` (临时备份)

---

## 🔧 维护脚本

### 检查脚本

```bash
# 检查不规范命名
py 30-scripts/check-folder-naming.py 40-arxiv/
```

### 自动清理

```bash
# 清理临时文件
py 30-scripts/cleanup-arxiv-dir.py
```

---

**违规处理:** 发现不规范命名立即整改，Git 提交前必须检查。
