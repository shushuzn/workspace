# 文件命名规范 (企业级标准)

**创建日期:** 2026-03-07 00:24  
**来源:** 用户提供的专业规范  
**状态:** ✅ 强制执行  
**版本:** v2.0

---

## 🎯 命名总原则

文件名应满足四个要求：

| 原则 | 说明 |
|------|------|
| **唯一性** | 同一目录下，不应出现语义相近但难区分的名称 |
| **稳定性** | 命名结构固定，不因个人习惯改变 |
| **可读性** | 不打开文件也知道它是什么 |
| **可排序性** | 按名称排序时，时间、版本、阶段有正确顺序 |

---

## 📋 推荐标准结构

### 完整结构 (6 字段)

```
[项目]_[文档类型]_[主题]_[日期]_[版本].[扩展名]
```

### 简化结构 (5 字段)

```
[项目]_[文档类型]_[主题]_[日期].[扩展名]
```

---

## 🔤 字段定义规范

### 1. 项目字段

**用途:** 表示文件归属的业务对象

**示例:**
```
CRM          # 客户关系管理
ERP          # 企业资源计划
DataLake     # 数据湖
AIReview     # AI 审查
MobileApp    # 移动应用
WebRevamp    # 官网改版
```

**要求:**
- ✅ 使用正式项目名或系统简称
- ✅ 缩写需在团队内唯一
- ❌ 不使用口语化、临时简称

---

### 2. 文档类型字段 (枚举化)

**必须使用固定字典:**

| 类型 | 说明 | 示例 |
|------|------|------|
| `PRD` | 产品需求文档 | `CRM_PRD_线索分配规则` |
| `BRD` | 商业需求文档 | `CRM_BRD_商业计划` |
| `MRD` | 市场需求文档 | `MKT_MRD_市场需求` |
| `SOP` | 标准操作流程 | `HR_SOP_招聘流程` |
| `API` | 接口文档 | `CRM_API_客户查询` |
| `DESIGN` | 设计方案 | `MobileApp_DESIGN_登录页` |
| `ARCH` | 架构文档 | `DataLake_ARCH_元数据` |
| `TESTCASE` | 测试用例 | `CRM_TESTCASE_登录模块` |
| `TESTREP` | 测试报告 | `CRM_TESTREP_性能测试` |
| `MINUTES` | 会议纪要 | `CRM_MINUTES_需求评审` |
| `PLAN` | 计划 | `PM_PLAN_项目计划` |
| `REPORT` | 报告 | `OPS_REPORT_销售周报` |
| `POLICY` | 制度 | `HR_POLICY_考勤管理` |
| `SPEC` | 规格说明 | `RD_SPEC_技术规格` |
| `DATA` | 数据文件 | `CRM_DATA_客户明细` |
| `SQL` | SQL 脚本 | `CRM_SQL_初始化表` |
| `SCRIPT` | 脚本文件 | `DataLake_SCRIPT_导出` |
| `IMG` | 图片素材 | `WebRevamp_IMG_HomeBanner` |
| `SLIDE` | 演示文稿 | `MKT_SLIDE_季度汇报` |
| `TEMPLATE` | 模板文件 | `TEMPLATE_Paper` |
| `NOTE` | 笔记 | `NOTE_Concept` |
| `DAILY` | 每日笔记 | `DAILY_2026-03-07` |

**要求:**
- ✅ 同类文档必须统一一个类型标识
- ❌ 不允许自由发挥

---

### 3. 主题字段

**用途:** 说明文件的具体内容

**要求:**
- ✅ 用最少词表达核心对象
- ✅ 优先使用名词短语
- ✅ 一个文件只写一个主主题
- ❌ 不用口语句子
- ❌ 避免堆砌多个并列事项

**推荐:**
```
线索分配规则
客户查询接口
登录流程
年度预算
供应商准入标准
Q1 投放复盘
```

**不推荐:**
```
关于客户管理这块的一些想法
最新整理
修改版
补充说明
老板要看的
```

---

### 4. 日期字段

**格式:** `YYYY-MM-DD`

**示例:**
```
2026-03-06
2025-12-31
```

**周期表达 (报表类):**
```
2026-W10      # 第 10 周
2026-Q1       # 第一季度
2026-03       # 2026 年 3 月
```

**要求:**
- ✅ 月、日必须补零
- ✅ 字符串排序即时间顺序
- ❌ 避免 `3.6`、`2026_3_6`、`06-03-2026`

---

### 5. 版本字段

**格式:** `v主版本。次版本`

**示例:**
```
v0.1    # 草稿
v0.8    # 评审中
v1.0    # 首次正式版
v1.1    # 小改动
v2.0    # 重大调整
```

**版本规则:**
- `v0.x` - 草稿/未正式发布
- `v1.0` - 首次正式版
- `v1.1` - 小改动，不改变主结构
- `v2.0` - 重大调整、重构、重要结论变更

**严禁:**
```
最终版
最新
最新版
最终确认版
最终版 2
v1-改
v1.0new
```

---

### 6. 状态字段 (可选)

**枚举值:**
```
DRAFT      # 草稿
INREVIEW   # 评审中
APPROVED   # 已确认
RELEASED   # 已发布
ARCHIVED   # 已归档
OBSOLETE   # 已废弃
SIGNED     # 已签署
```

**示例:**
```
CRM_PRD_线索分配规则_DRAFT_2026-03-01_v0.1.docx
CRM_PRD_线索分配规则_APPROVED_2026-03-06_v1.0.pdf
LEGAL_CONTRACT_供应商框架协议_SIGNED_2026-02-20_v1.0.pdf
```

---

## 🔤 字符规范

### 分隔符

**推荐:** 下划线 `_`

**示例:**
```
CRM_PRD_线索分配规则_2026-03-06_v1.0.docx
```

**要求:**
- ✅ 统一使用下划线
- ❌ 不混用多种分隔符

---

### 字符集

**推荐:**
- ✅ 结构字段用英文缩写
- ✅ 主题字段可用中文
- ❌ 禁用全角字符
- ❌ 禁用特殊符号

**禁用字符:**
```
\/:*?"<>|
& % # @ ! ~
（）【】《》
```

---

### 空格

**严格不使用空格**

**原因:**
- 链接、命令行、脚本引用容易出错
- 不同系统转义不一致

**错误:**
```
CRM PRD 登录流程 v1.docx
```

**正确:**
```
CRM_PRD_登录流程_v1.0.docx
```

---

### 大小写规则

**推荐:**
- 项目字段：大写 (`CRM`)
- 文档类型：大写 (`PRD`)
- 主题字段：中文或 PascalCase
- 日期：数字 (`2026-03-06`)
- 版本：小写 v + 数字 (`v1.0`)

---

## 📁 专用文件类型规范

### 会议纪要

```
[项目]_MINUTES_[会议主题]_[日期]_[版本]
```

**示例:**
```
CRM_MINUTES_需求评审会_2026-03-06_v1.0.docx
AIReview_MINUTES_模型上线评审_2026-03-05_v1.0.md
CRM_MINUTES_周例会_2026-W10_v1.0.docx
```

---

### 报告类

```
[部门/项目]_REPORT_[报告主题]_[周期]_[版本]
```

**示例:**
```
MKT_REPORT_投放复盘_2026-02_v1.0.pptx
FIN_REPORT_经营分析_2026-Q1_v1.0.xlsx
OPS_REPORT_履约周报_2026-W10_v1.0.docx
```

---

### 数据文件

```
[系统]_DATA_[数据主题]_[口径/范围]_[周期/日期]_[版本]
```

**示例:**
```
CRM_DATA_客户明细_全量_2026-03-06_v1.0.csv
APP_DATA_活跃用户_按日_2026-03_v1.0.xlsx
BI_DATA_订单汇总_华东区_2026-Q1_v2.0.parquet
```

---

### 模板文件

```
TEMPLATE_[类型]_[主题]_[版本]
```

**示例:**
```
TEMPLATE_Paper_Note_v1.0.md
TEMPLATE_Concept_Note_v1.0.md
TEMPLATE_Meeting_Note_v1.0.md
TEMPLATE_Daily_Note_v1.0.md
TEMPLATE_Learning_Note_v1.0.md
```

---

### 脚本文件

```
[项目]_SCRIPT_[功能]_[日期]_[版本].[扩展名]
```

**示例:**
```
CRM_SCRIPT_ExportCustomer_2026-03-06_v1.0.py
DataLake_SCRIPT_ExportOrder_2026-03_v1.0.py
```

---

### 研究文档

```
[项目]_[类型]_[主题]_[日期]_[版本]
```

**示例:**
```
LIG_PRD_PaperDraft_v2_2026-03-06.md
LIG_REPORT_GPModel_2026-03-06.md
CNT_PLAN_LiteratureReview_2026-03-07.md
```

---

## 🚫 禁止的命名方式

```
❌ 新建文档.docx
❌ 需求.docx
❌ 会议纪要最新版.docx
❌ 最终版.docx
❌ 最终版 2.docx
❌ 这个先用这个.xlsx
❌ 老板看这个.pptx
❌ toB 项目新方案改过真的最终版.pptx
```

**问题:**
- 无法搜索
- 无法排序
- 无法追踪版本
- 无法交接
- 无法自动化处理

---

## 📊 命名字典 (团队统一)

### 项目简称表

| 缩写 | 全称 | 说明 |
|------|------|------|
| `CRM` | Customer Relationship | 客户关系管理 |
| `LIG` | Laser-Induced Graphene | LIG 研究项目 |
| `CNT` | Carbon Nanotube | 碳纳米管研究 |
| `AI` | Artificial Intelligence | AI 研究 |

### 文档类型表

| 类型 | 说明 |
|------|------|
| `PRD` | 产品/论文需求文档 |
| `REPORT` | 报告 |
| `MINUTES` | 会议纪要 |
| `PLAN` | 计划 |
| `SPEC` | 规格说明 |
| `DATA` | 数据文件 |
| `SCRIPT` | 脚本 |
| `TEMPLATE` | 模板 |
| `NOTE` | 笔记 |

### 状态表

| 状态 | 说明 |
|------|------|
| `DRAFT` | 草稿 |
| `INREVIEW` | 评审中 |
| `APPROVED` | 已确认 |
| `RELEASED` | 已发布 |

---

## 📋 命名示例

### 核心文件

```
README.md
SOUL.md
AGENTS.md
USER.md
TOOLS.md
IDENTITY.md
HEARTBEAT.md
```

### 模板文件

```
TEMPLATE_Paper_Note_v1.0.md
TEMPLATE_Concept_Note_v1.0.md
TEMPLATE_Meeting_Note_v1.0.md
TEMPLATE_Daily_Note_v1.0.md
TEMPLATE_Learning_Note_v1.0.md
TEMPLATE_Index_v1.0.md
```

### 研究文档

```
LIG_PRD_PaperDraft_v2_2026-03-06.md
LIG_REPORT_GPModel_2026-03-06.md
CNT_PLAN_LiteratureReview_2026-03-07.md
```

### 脚本文件

```
check-broken-links_2026-03-06_v1.0.ps1
analyze-link-heat_2026-03-06_v1.0.ps1
auto-backlink-generator_2026-03-06_v1.0.ps1
```

### 报告文件

```
audit-report_2026-03-06_v1.0.md
link-heat-report_2026-03-06_v1.0.md
naming-audit_2026-03-07_v1.0.md
```

---

## 🔄 落地建议

### 1. 统一模板
新建文档直接从模板创建，模板里写好命名示例

### 2. 提交检查
共享盘/项目库上传前按规范检查

### 3. 归档规则
正式版转 PDF，旧版本移入 Archive 文件夹

---

## ✅ 检查清单

### 提交前检查

```markdown
- [ ] 使用下划线分隔
- [ ] 项目字段大写
- [ ] 文档类型大写
- [ ] 日期格式 YYYY-MM-DD
- [ ] 版本格式 vX.X
- [ ] 无空格
- [ ] 无特殊字符
- [ ] 主题清晰简洁
```

---

*文件命名规范由用户提供，Claw 记录并执行*  
*版本:* v2.0  
*最后更新:* 2026-03-07 00:24
