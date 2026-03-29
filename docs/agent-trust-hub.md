# Gen Digital Agent Trust Hub 参考文档

> Norton LifeLock (Gen Digital) 推出的 AI Agent 安全平台

## 概述

- **官网**: https://ai.gendigital.com/ath
- **公司**: Gen Digital Inc. (Norton LifeLock 母公司)
- **技术支持**: Gen Threat Labs
- **用途**: AI Agent 技能安全扫描与验证

## 核心产品

### 1. Skill Scanner
- **功能**: 扫描 OpenClaw skills 的安全性
- **URL**: https://ai.gendigital.com/skill-scanner
- **用途**: 在安装前查看技能可以访问什么资源

### 2. Sage
- **功能**: 轻量级安全层
- **URL**: https://ai.gendigital.com/sage
- **用途**: 拦截危险命令、恶意 URL 和凭证泄露

### 3. NeoClaw
- **功能**: 一键安全部署
- **状态**: Early Access

### 4. Neo Browser
- **功能**: 隐私 AI 浏览器
- **URL**: https://neobrowser.ai

## API

### 技能验证 API
```
GET https://ai.gendigital.com/api/scan/lookup
```

## 统计数据

| 指标 | 数量 |
|------|------|
| 恶意技能检测 | 12K+ |
| 保护用户 | 500M+ |
| 每日拦截威胁 | 7.5B+ |

## 使用建议

### 与 clawskills.sh 配合使用
1. **clawskills.sh** - 查看 VirusTotal + OpenClaw 状态
2. **Agent Trust Hub** - 深度技能行为分析

### 审查流程
```
1. clawskills.sh 初筛 (Benign/Suspicious/Malicious)
2. Agent Trust Hub 深度扫描
3. 人工审查 SKILL.md 和代码
4. 决定是否安装
```

## 风险

**极低** — 官方安全工具，由 Norton LifeLock 背书

## 相关链接

- [AARTS 标准](https://www.gendigital.com/blog/news/company-news/ai-agent-runtime-security)
- [Gen Threat Labs on X](https://x.com/GenThreatLabs)
- [LinkedIn](https://www.linkedin.com/company/gendigitalinc/)