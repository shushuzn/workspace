---
name: "work"
description: "Find and fix real engineering problems. Use when user says 工作/继续工作."
---

# Work

找真实工程问题并修复。找不到就诚实停止。

## When To Use

- User says: "工作", "继续工作"

## 什么是值得解决的问题

| 类别 | 信号 |
|------|------|
| Bug | 代码行为错误 |
| Crash风险 | Nil解引用、panic、竞态 |
| 安全 | 注入、密钥泄露、不安全反序列化 |
| 逻辑漏洞 | 未处理的边界、假设错误 |
| 性能 | 热路径O(n²)、不必要的分配 |

## 不值得做

- 为代码加测试 — 除非代码有bug
- 加注释 — 除非代码本身有问题
- 重命名变量 — 除非会引起bug
- 格式化改动
- 提取只重复2次的代码
- 任何没有实际影响的工作

## 过程

1. Survey：`git status && git log --oneline -5`
2. 找问题 — 找 Bug/Crash/Security/Logic/Performance
3. 找到？→ 修复 → 验证 → 提交
4. 没找到？→ **停止，诚实说"没找到"**

## 停止条件

- 找到并修复了真实问题
- 仔细检查后没找到任何影响用户/工程师的问题
- ~1小时

**找不到不丢脸。虚假繁忙才丢脸。**
