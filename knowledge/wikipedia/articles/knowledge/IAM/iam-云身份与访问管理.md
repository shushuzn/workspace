---
id: iam-yun-shen-fen-yu-fang-wen-guan-li
title: IAM 云身份与访问管理
category: security
tags:
  - IAM
  - 云安全
  - 身份认证
  - 特权升级
created: 2026-04-07
references: []
cross-references: []
---

# IAM 云身份与访问管理

**Identity and Access Management (IAM)** — 云平台中管理"谁可以做什么"的核心安全系统。控制身份（用户、服务账号）及其对资源的访问权限。

## 核心概念

### 身份类型
- **人类用户**：需要多因素认证（MFA）的管理员和开发者账号
- **服务账号（Service Account）**：机器对机器认证，用于运行工作负载
- **角色（Role）**：一组权限的抽象集合，可被身份委托（assume）

### 权限模型
- **最小权限原则**：只授予完成工作所需的最小权限集合
- **权限继承**：通过组织单元（OU）或资源层级向下传递
- **跨账户访问**：通过信任策略允许一个 AWS 账户的角色被另一个账户的身份使用

## IAM 权限图

IAM 系统可建模为有权有向图：
- **节点**：身份（用户/角色/服务账号）+ 资源（S3/EC2/数据库）
- **有向边**：允许的权限操作（`s3:GetObject`、`ec2:DescribeInstances`、`sts:AssumeRole`）
- **边属性**：操作类型、资源ARN、条件限制

攻击者利用权限图的连通性寻找特权升级路径。

## IAM 特权升级

[[iam-te-quan-sheng-ji|IAM 特权升级]] 是 IAM 系统最高危的威胁之一。攻击路径示例：
```
ReadS3(bucket) → ListEC2 → DescribeInstance → CreateAccessKey → AdminUser
```

## 相关条目

- [[iam-te-quan-sheng-ji|IAM 特权升级]] — 权限图的攻击路径分析
- [[burau-lyapunov-zhi-shu|Burau-Lyapunov 指数]] — 量化权限图结构的数学工具
