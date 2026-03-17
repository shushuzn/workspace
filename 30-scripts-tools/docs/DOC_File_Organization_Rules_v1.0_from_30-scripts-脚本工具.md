# 文件组织规则

**创建日期:** 2026-03-06 23:49  
**来源:** 用户明确要求 — "我不喜欢混乱的文件"  
**状态:** ✅ 强制执行

---

## 🎯 核心原则

> **保持文件整洁有序，不能混乱**

这是用户的核心偏好，必须严格遵守。

---

## 📁 文件夹结构规则

### 1. 数字前缀分类

**标准:**
```
00-09/   → 核心配置
10-19/   → 知识核心
20-29/   → 数据报告
30-39/   → 工具脚本
40-49/   → 收集监控
50-59/   → 外部资源
90-99/   → 归档测试
```

**要求:**
- [ ] 所有文件夹必须有数字前缀
- [ ] 新文件夹必须归类到正确区域
- [ ] 不允许在根目录创建无编号文件夹

---

### 2. 根目录清理

**允许的文件 (仅限):**
```
README.md
SOUL.md
AGENTS.md
USER.md
TOOLS.md
IDENTITY.md
HEARTBEAT.md
```

**要求:**
- [ ] 根目录不能有临时文件
- [ ] 根目录不能有报告文件
- [ ] 根目录不能有日志文件
- [ ] 所有其他文件必须移动到对应文件夹

---

## 📄 文件命名规则

### 3. 命名规范

**标准:**
- [ ] 小写字母
- [ ] 使用连字符 (kebab-case)
- [ ] 日期格式：YYYY-MM-DD
- [ ] 描述清晰简洁

**示例:**
```
✅ 正确:
- 2026-03-06-meeting-notes.md
- auto-backlink-generator.ps1
- broken-links-report.md

❌ 错误:
- Meeting Notes 2026.3.6.md
- AutoBacklinkGenerator.ps1
- report1.md
```

---

### 4. 文件归类

**报告文件:**
- 临时报告 → `21-reports/`
- 分析报告 → `21-reports/analysis/`
- 审计报告 → `21-reports/audit/`

**脚本文件:**
- PowerShell → `30-scripts/`
- Python → `11-research/scripts/` 或 `30-scripts/`

**文档:**
- 项目文档 → `11-research/docs/`
- 系统文档 → `15-docs/`
- 模板 → `05-templates/`

**日志:**
- 运行日志 → `logs/`
- 审计日志 → `logs/audit/`

---

## 🧹 清理规则

### 5. 临时文件处理

**标准:**
- [ ] 临时文件必须有明确过期时间
- [ ] 过期文件必须归档或删除
- [ ] 不允许在根目录存放临时文件

**示例:**
```powershell
# 临时报告 - 使用后移动
broken-links-report.md → 21-reports/audit/
link-heat-report.md → 21-reports/analysis/
```

---

### 6. 重复文件处理

**标准:**
- [ ] 禁止重复文件
- [ ] 相似文件必须合并
- [ ] 旧版本必须归档

**检查命令:**
```powershell
# 查找重复文件
Get-ChildItem -Recurse -File | Group-Object Name | Where-Object Count -gt 1
```

---

### 7. 空文件夹处理

**标准:**
- [ ] 空文件夹必须删除
- [ ] 空文件夹如有特殊用途必须有 README.md 说明

**检查命令:**
```powershell
# 查找空文件夹
Get-ChildItem -Recurse -Directory | Where-Object { (Get-ChildItem $_.FullName).Count -eq 0 }
```

---

## 📊 当前问题文件

### 需要整理的文件

| 文件 | 问题 | 应移动到 |
|------|------|----------|
| `broken-links-report.md` | 根目录临时报告 | `21-reports/audit/` |
| `link-heat-report.md` | 根目录临时报告 | `21-reports/analysis/` |
| `auto-link-report.md` | 根目录临时报告 | `21-reports/audit/` |
| `link-recommendations.md` | 根目录临时报告 | `21-reports/analysis/` |
| `broken-link-fixes.md` | 根目录临时报告 | `21-reports/audit/` |

---

## 🔧 自动化工具

### 8. 清理脚本

**创建:** `30-scripts/cleanup-workspace.ps1`

**功能:**
- [ ] 扫描根目录违规文件
- [ ] 扫描空文件夹
- [ ] 扫描重复文件
- [ ] 自动移动到正确位置
- [ ] 生成清理报告

---

## ✅ 检查清单

### 每日检查
- [ ] 根目录无临时文件
- [ ] 新文件已归类
- [ ] 临时报告已移动

### 每周检查
- [ ] 运行清理脚本
- [ ] 审查重复文件
- [ ] 删除空文件夹

### 每月检查
- [ ] 完整文件审计
- [ ] 归档旧文件
- [ ] 更新组织规则

---

## 📝 违规处理

**发现违规:**
1. 立即整理
2. 记录原因
3. 更新自动化防止再犯

---

*文件组织规则由 Claw 制定并遵守*  
*版本:* v1.0  
*最后更新:* 2026-03-06 23:49
