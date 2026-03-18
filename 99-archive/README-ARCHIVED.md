# 99-archive - 归档代码

**状态:** 🗄️ ARCHIVED (不再维护)

**最后更新:** 2026-03-18

---

## 📌 说明

本目录包含历史遗留代码，**不再主动维护**。

### 问题统计

- Python 文件：~219 个
- 致命问题：部分 (不影响生产)
- 严重问题：部分 (已记录到 remediation_log.json)
- 一般问题：大量 (代码风格等)

### 包含内容

1. **creation/** - 创作相关代码 (小说、角色等)
2. **knowledge/** - 知识图谱、卡片生成等
3. **old-dashboard/** - 旧版 Dashboard
4. **plugins/skills/** - 旧技能 (medium-watcher, x-tweet-fetcher 等)
5. **security/** - 安全脚本
6. **旧工作区/** - 迁移前的旧代码
   - n8n 工作流
   - research 研究脚本
   - scripts 工具集
   - materials 材料科学代码

---

## ⚠️ 使用警告

1. **代码可能不完整** - 部分功能已迁移到新位置
2. **依赖可能缺失** - 未维护 requirements.txt
3. **测试可能失败** - 未更新测试用例
4. **安全问题未修复** - 已知但未修复

---

## 🔍 如何查找活跃代码

| 功能 | 活跃位置 |
|------|---------|
| 会话压缩 | `30-scripts-tools/post_session_compress.py` |
| 批判者 | `30-scripts-tools/auto-critic_v7.py` |
| 工具执行 | `30-scripts-tools/tool_executor.py` |
| 记忆管理 | `30-scripts-tools/memory_*.py` |
| Dashboard | `05-dashboard/` |
| 技能 | `active_skills/` |

---

## 📋 整改计划

这些问题已记录到 `15-docs/remediation-plan.md`，纳入长期清理计划。

**优先级:** 低 (不影响生产)

---

*创建日期：2026-03-18 (整改第二阶段)*
