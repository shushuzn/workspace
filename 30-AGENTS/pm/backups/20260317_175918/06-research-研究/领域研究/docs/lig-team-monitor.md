# LIG 研究团队监控配置

**创建日期:** 2026-03-08  
**类型:** 团队监控配置  
**数据源:** PubMed

---

## 🔬 核心研究团队

### 1. Tour 组 (LIG 发明者)

**机构:** Rice University  
**PI:** James M. Tour  
**角色:** LIG 技术发明者 (2014)  
**研究方向:** LIG 基础工艺、多领域应用

**PubMed 搜索式:**
```
"Tour JM"[Author] AND "laser induced graphene"
```

**最新论文:**
| PMID | 日期 | 标题 |
|------|------|------|
| 37724983 | 2023 | ... |
| 33900723 | 2021 | ... |
| 32830950 | 2020 | ... |

**监控频率:** 每周  
**提醒阈值:** 新论文 ≥1 篇

---

### 2. 叶汝权组 (LIG 生物医学)

**机构:** City University of Hong Kong  
**PI:** Ruquan Ye (叶汝权)  
**角色:** LIG 生物医学应用领导者  
**研究方向:** LIG 生物传感、肿瘤治疗、神经接口

**PubMed 搜索式:**
```
"Ye R"[Author] AND "laser induced graphene"
```

**最新论文:**
| PMID | 日期 | 标题 | 期刊 |
|------|------|------|------|
| 41784393 | 2026-03-05 | LIG-CuO 肿瘤贴片 | ACS Nano |
| 38597770 | 2024 | ... | ... |
| 38575649 | 2024 | ... | ... |

**监控频率:** 每周  
**提醒阈值:** 新论文 ≥1 篇

---

## 📧 PubMed 自动提醒设置

### 方法 1: MyNCBI Email Alert

1. 访问：https://www.ncbi.nlm.nih.gov/pubmed/
2. 搜索：`"Tour JM"[Author] AND "laser induced graphene"`
3. 点击 "Create alert"
4. 登录 MyNCBI 账号
5. 设置发送频率 (Weekly/Monthly)
6. 输入接收邮箱

### 方法 2: RSS Feed

**Tour 组 RSS:**
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/erss.fcgi?db=pubmed&term=%22Tour+JM%22%5BAuthor%5D+AND+%22laser+induced+graphene%22
```

**叶汝权组 RSS:**
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/erss.fcgi?db=pubmed&term=%22Ye+R%22%5BAuthor%5D+AND+%22laser+induced+graphene%22
```

**使用方法:**
- 添加到 RSS 阅读器 (Feedly, Inoreader)
- 或集成到 heartbeat 自动检查

---

## ⏰ Heartbeat 集成

### 每周检查脚本

```powershell
# lig-team-monitor.ps1
# 每周一 9AM 执行

$tourUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=`"Tour+JM`"[Author]+AND+`"laser+induced+graphene`"&retmax=5&sort=publication+date"
$yeUrl = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=`"Ye+R`"[Author]+AND+`"laser+induced+graphene`"&retmax=5&sort=publication+date"

# 获取最新 PMID
$tourPMIDs = (Invoke-RestMethod $tourUrl).eSearchResult.IdList
$yePMIDs = (Invoke-RestMethod $yeUrl).eSearchResult.IdList

# 加载已记录 PMID
$existingPMIDs = Get-Content "13-memory/lig-team-pmids.txt" -ErrorAction SilentlyContinue

# 检查新论文
$newTour = $tourPMIDs | Where-Object { $_ -notin $existingPMIDs }
$newYe = $yePMIDs | Where-Object { $_ -notin $existingPMIDs }

if ($newTour) {
    Write-Host "🔬 Tour 组新论文：$($newTour -join ', ')"
    # 添加到待分析队列
}

if ($newYe) {
    Write-Host "🔬 叶汝权组新论文：$($newYe -join ', ')"
    # 添加到待分析队列
}

# 更新已记录 PMID
($tourPMIDs + $yePMIDs) | Select-Object -Unique | Set-Content "13-memory/lig-team-pmids.txt"
```

### 定时任务

```powershell
# 每周一 9AM 执行
$action = New-ScheduledTaskAction -Execute "pwsh" `
  -Argument "-File D:\OpenClaw\workspace\30-scripts\lig-team-monitor.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -TaskName "LIG-Team-Monitor" -Action $action -Trigger $trigger
```

---

## 📊 历史论文统计

| 团队 | 总论文数 | 2026 年 | 2025 年 | 2024 年 |
|------|----------|---------|---------|---------|
| Tour 组 | ~50 | 0 | 5 | 10 |
| 叶汝权组 | ~30 | 2 | 8 | 12 |

**注:** 叶汝权组 2026 年已有 2 篇 (包括今天分析的肿瘤贴片)

---

## 🔗 相关资源

- **Tour 组主页:** https://tour.rice.edu/
- **叶汝权组主页:** https://www.cityu.edu.hk/phy/people/academic-staff/ruquan-ye
- **LIG 专利:** US Patent 9,783,409 (Tour, 2014)
- **LIG 综述:** *Adv. Mater.* 2020, 32, 1905517

---

**维护者:** Claw (AI Research OS)  
**下次检查:** 2026-03-15 (周一 9AM)
