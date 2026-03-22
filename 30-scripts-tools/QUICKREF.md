# Quick Reference - 工作区快速参考

## 工作流命令

```bash
# 开始任务
py workflow.py start "任务名"

# 保存进度
py workflow.py save "进度描述"

# 运行测试
py workflow.py test

# 查看状态
py workflow.py status

# 结束会话
py workflow.py end "完成描述"
```

## Stock PRO

```python
from stock_pro import analyze, gen_report

# 单股票分析
analyze('NVDA')

# 批量分析 (178x加速)
analyze_multiple_parallel(['NVDA', 'META', 'AAPL'])

# 生成报告
gen_report('NVDA')
```

**测试:** `py 30-scripts-tools/stock_pro/test_all.py` → 18/18

## Skills (16个)

| Skill | 用途 |
|-------|------|
| [workflow](active_skills/workflow/) | 会话管理 |
| [coding](active_skills/coding/) | 编程工作流 |
| [stock-pro](active_skills/stock-pro/) | 股票分析 |
| [pdf](active_skills/pdf/) | PDF处理 |
| [xlsx](active_skills/xlsx/) | 电子表格 |
| [docx](active_skills/docx/) | Word文档 |
| [pptx](active_skills/pptx/) | PowerPoint |
| [cron](active_skills/cron/) | 定时任务 |
| [himalaya](active_skills/himalaya/) | 邮件管理 |
| [news](active_skills/news/) | 新闻查询 |
| [browser_visible](active_skills/browser_visible/) | 可见浏览器 |
| [file_reader](active_skills/file_reader/) | 文件读取 |
| [file-handling](active_skills/file-handling/) | 文件操作 |
| [guidance](active_skills/guidance/) | 安装指导 |
| [agent-spectrum](active_skills/agent-spectrum/) | Agent评分 |
| [dingtalk_channel](active_skills/dingtalk_channel/) | 钉钉集成 |

## 文件位置

| 类型 | 路径 |
|------|------|
| 核心配置 | SOUL.md, USER.md, AGENTS.md |
| 内存 | 13-memory/, MEMORY.md |
| 工具 | 30-scripts-tools/ |
| 归档 | 30-scripts-tools/archive_001/ (435 files) |

## 快捷命令

```bash
# 快速测试
py 30-scripts-tools/stock_pro/test_all.py

# 检查状态
py 30-scripts-tools/workflow.py status

# 上下文加载
py 30-scripts-tools/fast_load.py
```

## 四阶段编程

```
┌─────────────────────────────────────┐
│ 1. ARCHITECT  - 架构设计             │
│    Purpose, Data Flow, Files        │
├─────────────────────────────────────┤
│ 2. CODE       - 编写代码             │
│    Implementation, DEBUG comments   │
├─────────────────────────────────────┤
│ 3. ASK        - 自我审查             │
│    Edge cases, Error handling       │
├─────────────────────────────────────┤
│ 4. DEBUG      - 测试验证             │
│    Unit, Integration, Edge cases   │
└─────────────────────────────────────┘
```

## 归档统计

| 目录 | 文件数 |
|------|--------|
| archive_001 | 435 |
| workflow_archive | 65 |
| 99-archive | 2,068 |
| 99-backups | 1,697 |
| **总计** | **4,265** |
