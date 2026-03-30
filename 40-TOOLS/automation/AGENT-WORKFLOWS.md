# Agent 工作流集成

**创建日期:** 2026-03-27
**用途:** 将 20 个已安装 Agent 集成到工作流系统

---

## 🔄 Agent 工作流映射

### 开发工作流

```
代码提交 → [Dep Scanner] → [PR Reviewer] → [Test Writer] → 合并
         CVE扫描      代码审查      补测试
```

**触发:** `workflow.bat run dev-review <pr-url>`

---

### 内容生产工作流

```
主题 → [News Curator] → [SEO Writer] → [Echo] → 多平台发布
     抓取素材      优化      一鱼多吃
```

**触发:** `workflow.bat run content <topic>`

---

### 安全审计工作流

```
扫描 → [Vuln Scanner] → [GDPR Auditor] → 生成报告 → 通知
     漏洞检测    合规检查
```

**触发:** `workflow.bat run security-audit`

---

### 会议准备工作流

```
议程 → [Meeting Notes] → 行动项 → [Orion] → 任务分配
```

**触发:** `workflow.bat run meeting-prep <meeting-id>`

---

### 客户管理流程

```
数据 → [Churn Predictor] → 高风险 → [Personal CRM] → 跟进
    流失预警
```

**触发:** `workflow.bat run customer-care`

---

### 每日自动化流程

```
07:00 [Morning Briefing] → 日报
08:00 [News Curator] → 早间资讯
18:00 [News Curator] → 晚间资讯
22:00 [Overnight Coder] → 夜间开发
```

---

## 📝 工作流模板

### 模板 1: PR 完整审查流程

```yaml
name: pr-complete-review
steps:
  - agent: 01-lens-pr-reviewer
    input: "{pr_url}"
    output: review_report.md
  
  - agent: 04-test-writer-qa
    input: "{pr_url}"
    output: test_coverage.md
  
  - agent: 05-dep-scanner
    input: "{repo_path}"
    output: security_report.md
  
  - merge:
      files: [review_report.md, test_coverage.md, security_report.md]
      output: PR_COMPLETE_REVIEW.md
```

### 模板 2: 行业分析报告

```yaml
name: industry-analysis
steps:
  - agent: 18-news-curator
    sources: [techcrunch, hackernews, reddit]
    count: 20
    output: raw_news.md
  
  - agent: 17-seo-writer
    topic: "{industry}"
    output: seo_analysis.md
  
  - agent: 15-echo-content
    content: seo_analysis.md
    platforms: [linkedin, twitter, newsletter]
```

### 模板 3: 全量安全扫描

```yaml
name: full-security-scan
steps:
  - agent: 19-vuln-scanner
    scope: workspace
    output: vuln_report.md
  
  - agent: 20-gdpr-auditor
    scope: all_projects
    output: gdpr_compliance.md
  
  - agent: 05-dep-scanner
    scope: all_repos
    output: dep_audit.md
  
  - agent: 14-churn-predictor
    scope: production_data
    output: risk_assessment.md
```

---

## 🚀 使用方法

1. 选择工作流类型
2. 触发命令或告诉 Feishu
3. Feishu 执行各 Agent 串联
4. 输出合并报告

---

## 📂 输出位置

```
outputs/
├── pr-reviews/
├── security-reports/
├── content/
├── news-digests/
└── meeting-notes/
```
