# 🚀 PM Agent 使用指南

## 📋 快速开始

### 方法 1: 命令行运行（推荐）
```bash
cd D:\OpenClaw\workspace
python 30-scripts-tools/pm-agent.py --run
```

### 方法 2: 创建批处理文件
```bash
@echo off
cd /d "%~dp0.."
python 30-scripts-tools/pm-agent.py --run
pause
```

---

## 🔧 命令选项

### pm-agent.py - 主程序

| 命令 | 功能 | 说明 |
|------|------|------|
| `--run` | 完整分析 | 产品价值 + 整洁度 + 综合报告 |
| `--analyze-product` | 仅产品分析 | 分析工具价值 |
| `--check-cleanliness` | 仅整洁度检查 | 检查文件夹整洁度 |
| `--auto-clean` | 自动整理 | 开发中 |

### pm-duplicate-analyzer.py - 重复分析

| 命令 | 功能 | 说明 |
|------|------|------|
| `--workspace PATH` | 指定工作区 | 默认 D:\OpenClaw\workspace |
| `--output PATH` | 输出报告 | JSON 格式报告 |
| `--threshold 0.6` | 相似度阈值 | 0-1，默认 0.6 |

### pm-merge-folders.py - 合并工具

| 命令 | 功能 | 说明 |
|------|------|------|
| `--workspace PATH` | 指定工作区 | 默认 D:\OpenClaw\workspace |
| `--dry-run` | 仅模拟 | 不实际执行 |
| `--confirm` | 自动确认 | 跳过确认提示 |

---

## 📊 报告位置

所有报告都在 `agent-pm/reports/` 文件夹内：

```
D:\OpenClaw\workspace/
└── agent-pm/
    └── reports/
        ├── product-analysis/       # 产品价值分析报告
        │   └── product-analysis-YYYY-MM-DD.md
        ├── cleanliness-reports/    # 整洁度检查报告
        │   └── cleanliness-YYYY-MM-DD.md
        └── roadmaps/               # 综合路线图
            └── combined-YYYY-MM-DD.md
```

---

## 📖 报告说明

### 产品价值分析报告
**内容:**
- 工具价值分类（高/中/低）
- 使用频率估算
- 砍掉/保留建议

**使用场景:**
- 决定哪些工具值得维护
- 识别低价值工具
- 资源分配决策

### 整洁度检查报告
**内容:**
- 整洁度评分（0-100）
- 文件夹数量统计
- 重复文件夹检测
- 命名规范检查

**使用场景:**
- 每周整洁度检查
- 大重构前评估
- 追踪整洁度趋势

### 综合路线图
**内容:**
- 产品价值总结
- 整洁度总结
- 优先行动建议（P0/P1/P2）

**使用场景:**
- 每周规划
- 月度回顾
- 决策参考

---

## ⚙️ 配置说明

编辑 `agent-pm/config/config.json`:

```json
{
  "workspace": "D:\\OpenClaw\\workspace",
  "cleanliness": {
    "max_folders": 50,        // 最大文件夹数
    "auto_clean": false       // 是否自动清理
  },
  "product": {
    "min_roi_threshold": 0.5, // 最低 ROI 阈值
    "require_user_confirmation": true  // 需要用户确认
  },
  "schedule": {
    "daily_check": true,
    "weekly_audit": true
  }
}
```

---

## 📝 历史状态

**运行状态:** `agent-pm/data/pm-state.json`
- 最后运行时间
- 总运行次数
- 生成报告数
- 待处理行动

**决策历史:** `agent-pm/data/pm-history.json`
- 历史决策记录
- 决策效果追踪

---

## 🎯 最佳实践

### 每日检查（1 分钟）
```bash
python 30-scripts-tools/pm-agent.py --check-cleanliness
```
快速检查整洁度，保持工作区干净。

### 每周分析（5 分钟）
```bash
python 30-scripts-tools/pm-agent.py --run
```
完整分析，生成周报，规划下周优先级。

### 每月回顾（15 分钟）
1. 阅读本月所有报告
2. 追踪整洁度趋势
3. 审查产品价值变化
4. 调整资源配置

---

## ❓ 常见问题

**Q: 为什么整洁度评分这么低？**
A: 当前工作区有 82 个文件夹（建议≤50），26 对重复文件夹。建议合并重复文件夹。

**Q: 自动整理安全吗？**
A: 默认关闭。开启后会先请求确认，并备份后再执行。

**Q: 如何删除 PM Agent？**
A: 删除 `agent-pm/` 文件夹和 `30-scripts-tools/pm-*.py` 文件。

**Q: 报告太多怎么办？**
A: 报告都在 `agent-pm/reports/` 内，可以定期归档或删除旧报告。

**Q: 脚本在哪里？**
A: 所有脚本在 `30-scripts-tools/` 文件夹：
- `pm-agent.py` - 主程序
- `pm-duplicate-analyzer.py` - 重复分析
- `pm-merge-folders.py` - 合并工具

---

**PM Agent v3.0** | 产品价值第一 | 整洁度基础 | 工具在 30-scripts-tools
