# 报告系统使用规则（强制性）

**生效日期:** 2026-03-17  
**版本:** 1.0  
**执行:** 强制

---

## 📋 核心规则

### 规则 1: 创建报告必须使用模板
```bash
# ❌ 禁止：手动创建 markdown 文件
# ✅ 必须：使用生成器

python 30-scripts-tools\report_generator.py --create "报告标题" --type <类型>
```

**验收标准:**
- [ ] 报告 ID 自动生成
- [ ] 模板完整填充
- [ ] 元数据完整（日期/作者/类型/状态）
- [ ] 质量预检查 >70%

**违反处理:** 报告被打回重写

---

### 规则 2: 提交前必须通过质量检查
```bash
# ❌ 禁止：未检查直接提交
# ✅ 必须：质量评分>70%

python 30-scripts-tools\report_quality_scorer.py --score "report.md"
```

**质量门槛:**
| 等级 | 分数 | 处理 |
|------|------|------|
| 优秀 | 90-100% | ✅ 直接提交 |
| 良好 | 70-89% | ✅ 可提交 |
| 需改进 | 50-69% | ⚠️ 修改后提交 |
| 不合格 | <50% | ❌ 禁止提交 |

**违反处理:** Git 预提交钩子拒绝

---

### 规则 3: 命名必须符合规范
```bash
# ❌ 禁止：lig-risk-report-20260317.md
# ✅ 必须：REPORT-LIG-RISK-20260317.md

标准格式：
<类型>-<主题>-<日期>.md

类型前缀：
- REPORT: 一般报告
- TEST: 测试报告
- COMPLETE: 完成报告
- WEEKLY: 周报
- MONTHLY: 月报
```

**违反处理:** 监控脚本自动告警

---

### 规则 4: 每周必须执行质量评估
```bash
# Heartbeat 任务（每周一执行）

python 30-scripts-tools\report_quality_scorer.py --batch
python 30-scripts-tools\report_quality_scorer.py --report
```

**输出:**
- 质量报告生成到 `21-reports/quality-reports/`
- 低分报告列表（<70%）
- 改进建议

**违反处理:** Heartbeat 告警

---

### 规则 5: 每月必须执行存储优化
```bash
# Heartbeat 任务（每月 1 日执行）

python 30-scripts-tools\report_storage.py --analyze
python 30-scripts-tools\report_storage.py --duplicates
python 30-scripts-tools\report_storage.py --archive --execute
```

**输出:**
- 存储使用报告
- 重复报告列表
- 归档执行结果

**违反处理:** Heartbeat 告警

---

### 规则 6: 敏感报告必须保护
```bash
# 创建时自动分类

python 30-scripts-tools\report_access.py --classify

# 手动保护
python 30-scripts-tools\report_access.py --protect "report.md" --level confidential
```

**敏感模式:**
- SECURITY, PASSWORD, SECRET → INTERNAL
- FINANCIAL, LEGAL, HR → CONFIDENTIAL
- ADMIN, ROOT, SYSTEM → RESTRICTED

**违反处理:** 访问控制自动拦截

---

### 规则 7: 删除前必须备份
```bash
# ❌ 禁止：直接 rm/del
# ✅ 必须：使用备份

备份位置：backup/reports-cleanup/
格式：[原文件名]-[时间戳].backup
```

**违反处理:** Git 回滚 + 警告

---

### 规则 8: Git 提交必须频繁
```bash
# ❌ 禁止：累积大量更改一次提交
# ✅ 必须：每步提交

每个任务完成后立即：
1. git add <files>
2. git commit -m "<规范消息>"
3. git push origin master
```

**违反处理:** 提交消息不规范被打回

---

## 🔧 自动化检查

### Git 预提交钩子
```python
# .git/hooks/pre-commit
1. 检查报告命名规范
2. 检查质量评分（新报告>70%）
3. 检查敏感报告保护
4. 检查备份存在性
```

### Heartbeat 集成
```markdown
# HEARTBEAT.md
- 每周一：质量评估
- 每月 1 日：存储优化
- 每季度：访问审计
```

### 部署检查
```python
# deploy_production.py
Step 9: 规则合规检查
- 检查所有脚本可执行
- 检查配置文件完整
- 运行测试验证
```

---

## 📊 违规记录

| 日期 | 违规类型 | 处理 | 状态 |
|------|----------|------|------|
| - | - | - | - |

---

## 🎯 执行方式

**自动执行:**
1. Git 预提交钩子
2. Heartbeat 定时任务
3. 部署流程检查

**手动执行:**
```bash
# 合规检查
python 30-scripts-tools\monitor_reports.py

# 质量检查
python 30-scripts-tools\report_quality_scorer.py --batch

# 存储检查
python 30-scripts-tools\report_storage.py --analyze
```

---

## 📈 合规指标

| 指标 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 模板使用率 | 100% | 0% | ❌ |
| 质量合格率 | >85% | 26.7% | ❌ |
| 命名规范率 | 100% | 100% | ✅ |
| 敏感报告保护 | 100% | 100% | ✅ |
| 备份执行率 | 100% | 100% | ✅ |

---

**批准:** 系统自动生成  
**审查:** 每周一自动审查  
**更新:** 规则修订时自动更新
