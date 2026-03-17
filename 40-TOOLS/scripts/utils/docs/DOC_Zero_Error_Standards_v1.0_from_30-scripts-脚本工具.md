# 零错误标准

**创建日期:** 2026-03-06 23:43  
**来源:** SOUL.md - Attention to Detail  
**状态:** ✅ 强制执行

---

## 🎯 核心原则

> **不能有一丝一毫错误**

这是 Claw 的核心原则，必须严格遵守。

---

## 📋 代码质量标准

### 0. 频繁提交 (2026-03-06 23:46)

**原则:** 每一步后都推送 git，防止重大错误

**标准:**
- [ ] 每个功能完成后立即提交
- [ ] 每次修改后测试并提交
- [ ] 不要累积多个修改再提交
- [ ] 提交信息清晰描述变更

**示例:**
```powershell
# ✅ 正确 - 小步提交
edit file1.ps1
git add file1.ps1
git commit -m "Fix: encoding issue in file1"
git push

edit file2.ps1
git add file2.ps1
git commit -m "Fix: template exclusion in file2"
git push

# ❌ 错误 - 累积提交
edit file1.ps1
edit file2.ps1
edit file3.ps1
git add -A
git commit -m "Fix multiple issues"
git push
```

**来源:** 用户教导 — "你也应该在每一步后推送 git，防止重大错误"

---

### 1. 测试优先

**标准:**
- [ ] 所有脚本必须测试后提交
- [ ] 测试覆盖率 > 80%
- [ ] 边界情况必须测试
- [ ] 错误处理必须验证

**检查清单:**
```powershell
# 运行测试
.\script.ps1 -DryRun          # 干运行测试
.\script.ps1 -Verbose         # 详细输出测试
.\script.ps1                  # 正常运行测试

# 验证输出
Test-Path "output.md"         # 输出文件存在
Get-Content "output.md"       # 内容正确
```

---

### 2. 命名规范

**标准:**
- [ ] 文件名：小写 + 连字符 (kebab-case)
- [ ] 函数名：动词 - 名词 (Verb-Noun)
- [ ] 变量名：小写 + 驼峰 (camelCase)
- [ ] 常量名：大写 + 下划线 (UPPER_CASE)

**示例:**
```powershell
# ✅ 正确
$brokenLinks = @()
function Get-DocumentTopics { }
$excludeDirs = @('.git', 'node_modules')

# ❌ 错误
$BrokenLinks = @()
function get_document_topics { }
$EXCLUDEDIRS = @('.git', 'node_modules')
```

---

### 3. 参数规范

**标准:**
- [ ] 所有脚本支持 `-Path` 参数
- [ ] 所有脚本支持 `-Verbose` 参数
- [ ] 危险操作支持 `-DryRun` 参数
- [ ] 所有参数有默认值
- [ ] 参数类型明确声明

**示例:**
```powershell
param(
    [string]$Path = "D:\OpenClaw\workspace",
    [switch]$Verbose,
    [switch]$DryRun
)
```

---

### 4. 错误处理

**标准:**
- [ ] 所有外部调用有 try-catch
- [ ] 错误信息清晰可读
- [ ] 错误级别区分 (Error/Warning/Info)
- [ ] 错误日志记录

**示例:**
```powershell
try {
    $content = Get-Content $file.FullName -Raw -ErrorAction Stop
} catch {
    Write-Host "Error reading $($file.Name): $_" -ForegroundColor Red
    continue
}
```

---

### 5. 日志规范

**标准:**
- [ ] 所有脚本输出开始时间
- [ ] 所有脚本输出结束时间
- [ ] 所有脚本输出统计信息
- [ ] 日志保存到 `logs/` 目录

**示例:**
```powershell
$startTime = Get-Date
Write-Host "Start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# ... 执行 ...

$endTime = Get-Date
$duration = New-TimeSpan -Start $startTime -End $endTime
Write-Host "Duration: $($duration.Minutes)m $($duration.Seconds)s"
```

---

### 6. 文档规范

**标准:**
- [ ] 所有脚本有头部注释
- [ ] 所有函数有说明注释
- [ ] 所有参数有说明
- [ ] 提供使用示例

**示例:**
```powershell
#!/usr/bin/env pwsh
# Script Name - Brief description
# Usage: .\script.ps1 [-Path <dir>] [-Verbose]

param(
    [string]$Path = "D:\...",  # Workspace path
    [switch]$Verbose           # Enable verbose output
)
```

---

### 7. 报告格式

**标准:**
- [ ] 所有报告使用统一模板
- [ ] 所有报告包含时间戳
- [ ] 所有报告包含统计信息
- [ ] 所有报告使用统一语言 (中文)

**模板:**
```markdown
# 报告名称

**生成时间:** yyyy-MM-dd HH:mm:ss  
**扫描文件:** XXX  
**发现问题:** XXX  

---

## 详细信息

...

---

*报告由 script.ps1 自动生成*
```

---

## 🔍 代码审查清单

### 提交前检查

```markdown
- [ ] 代码已测试 (DryRun + Verbose + Normal)
- [ ] 命名符合规范
- [ ] 参数统一
- [ ] 错误处理完整
- [ ] 日志输出正确
- [ ] 文档完整
- [ ] 无中文乱码风险
- [ ] 无硬编码路径
- [ ] 无敏感信息
```

### 测试用例

```markdown
- [ ] 正常路径测试
- [ ] 空目录测试
- [ ] 大文件测试
- [ ] 特殊字符测试
- [ ] 权限不足测试
- [ ] 磁盘满测试
```

---

## 📊 质量指标

| 指标 | 目标 | 当前 | 状态 |
|------|------|------|------|
| 测试覆盖率 | >80% | ? | ⏳ |
| 文档完整率 | 100% | ? | ⏳ |
| 错误处理率 | 100% | ? | ⏳ |
| 命名规范率 | 100% | ? | ⏳ |
| 参数统一率 | 100% | ? | ⏳ |

---

## 🔄 持续改进

### 每周审查
- [ ] 审查新增代码
- [ ] 运行完整测试
- [ ] 更新文档

### 每月审查
- [ ] 代码质量评估
- [ ] 规范更新
- [ ] 工具优化

---

## 📝 违规处理

**发现违规:**
1. 立即修复
2. 记录原因
3. 更新规范防止再犯

**严重违规:**
- 未测试提交
- 硬编码密码
- 忽略错误处理

---

*零错误标准由 Claw 制定并遵守*  
*版本:* v1.0  
*最后更新:* 2026-03-06 23:43
