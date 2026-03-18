# 批判者 v5.0 审查工具使用指南

**版本:** v5.0  
**日期:** 2026-03-18  
**目标:** 将批判性思维嵌入所有关键工作流程

---

## 🎯 工具说明

**critic_v5_review.py** 提供标准化的审查流程，确保关键操作前经过严格检查。

**核心功能:**
- ✅ 8 个预定义审查场景
- ✅ 自定义审查清单
- ✅ 交互式检查
- ✅ 自动生成报告
- ✅ 阻止未通过审查的操作

---

## 📋 审查场景

### 1. 文件整理审查 (`file_organize`)

**使用场景:** 运行 file-organizer.py, folder-organizer.py 前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario file_organize
```

**检查项 (7 个，必须全部通过):**
1. 目标目录扫描完成 (确认文件数、类型分布)
2. 备份方案确认 (备份位置、恢复流程)
3. 重名处理逻辑验证 (避免__init___1_2_3_.py 模式)
4. 研究目录排除白名单 (06-research/, 10-RESEARCH/)
5. 99-backups/排除确认 (防止嵌套备份)
6. 小批量测试 (先处理 10 个文件验证)
7. 回滚方案 (出错如何恢复)

**价值:** 防止 folder-organizer 灾难重演

---

### 2. 工具优化审查 (`tool_optimize`)

**使用场景:** 运行 optimize-tools-*.py 前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario tool_optimize
```

**检查项 (7 个，必须全部通过):**
1. 工具依赖分析 (哪些工具引用此工具)
2. 功能等价验证 (合并后功能不丢失)
3. 测试覆盖率 (关键函数有测试)
4. 备份确认 (99-backups/tool-optimization-*/)
5. 版本兼容性 (Python 版本、依赖库)
6. 性能影响评估 (优化后速度变化)
7. 文档更新 (README、工具清单)

**价值:** 防止工具优化导致功能丢失

---

### 3. 数据清理审查 (`data_cleanup`)

**使用场景:** 运行 cleanup-*.py, delete-*.py 前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario data_cleanup
```

**检查项 (7 个，必须全部通过):**
1. 清理目标明确 (具体文件/目录)
2. 影响范围评估 (多少文件、多大空间)
3. 备份方案 (备份位置、保留期限)
4. 可恢复性验证 (能从备份恢复)
5. 敏感信息检查 (是否含 API key、密码)
6. 小批量测试 (先清理 10 个验证)
7. Git 状态检查 (未提交文件处理)

**价值:** 防止误删重要文件

---

### 4. 研究任务启动审查 (`research_start`)

**使用场景:** 新研究领域/新实验开始前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario research_start
```

**检查项 (8 个，必须全部通过):**
1. 研究问题有科学意义 (≥3 篇文献支持)
2. 样本量先验功效分析 (Power≥0.95)
3. 特征文献依据 (每个特征≥3 篇)
4. VIF 预分析 (<3)
5. 验证方案 (嵌套 CV+Bootstrap)
6. 外部验证方案 (真正独立≥50 样本)
7. 实验可复现性 (代码、数据公开)
8. 负面结果处理计划

**价值:** 防止低质量研究、资源浪费

---

### 5. Git 操作审查 (`git_operation`)

**使用场景:** 创建分支、合并分支、重要提交前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario git_operation
```

**检查项 (7 个，必须全部通过):**
1. 分支命名规范 (feature/xxx, bugfix/xxx)
2. 变更范围明确 (影响哪些文件)
3. 冲突检查 (与 master 分支)
4. 测试通过 (本地测试完成)
5. 代码审查 (self-review 完成)
6. 提交信息规范 (动词开头、<72 字符)
7. 远程仓库确认 (推送到正确仓库)

**价值:** 防止 Git 操作失误

---

### 6. 记忆系统操作审查 (`memory_operation`)

**使用场景:** MEMORY.md 更新、记忆蒸馏、笔记合并前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario memory_operation
```

**检查项 (7 个，必须全部通过):**
1. 更新必要性 (是否值得长期记忆)
2. 信息准确性 (事实、数据验证)
3. 去重检查 (与现有记忆不重复)
4. 结构化 (符合 MEMORY.md 格式)
5. 时效性标注 (日期、版本)
6. 大小控制 (MEMORY.md <10KB±2KB)
7. 有增有减 (删除过时内容)

**价值:** 保持记忆系统高质量

---

### 7. API/密钥管理审查 (`api_key`)

**使用场景:** 使用 API、创建密钥文件前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario api_key
```

**检查项 (7 个，必须全部通过):**
1. 必要性 (是否必须使用 API)
2. 密钥存储 (.env 文件、不提交 git)
3. 权限最小化 (只申请必要权限)
4. 过期处理 (密钥轮换计划)
5. 监控告警 (使用量监控)
6. 泄露应急 (撤销流程)
7. .env.example 模板 (不含真实密钥)

**价值:** 防止密钥泄露

---

### 8. 报告生成审查 (`report_generate`)

**使用场景:** 创建*-report-*.md, *-guide-*.md 前

**命令:**
```bash
py 30-scripts-tools\critic_v5_review.py --scenario report_generate
```

**检查项 (7 个，必须全部通过):**
1. 用户明确要求 (不是自动生成)
2. 命名规范 (-GUIDE-而非-REPORT-)
3. 内容价值 (不是重复信息)
4. 大小控制 (<10KB，避免冗长)
5. 结构化 (清晰目录、列表)
6. 可操作性 (有明确建议)
7. Git 处理 (不提交或特殊处理)

**价值:** 防止自动生成无价值报告

---

## 🔧 自定义审查

### 创建自定义检查清单

**步骤 1:** 创建 JSON 文件

```json
{
  "name": "我的自定义审查",
  "threshold": 5,
  "checks": [
    {
      "check": "检查项 1",
      "description": "说明 1"
    },
    {
      "check": "检查项 2",
      "description": "说明 2"
    },
    {
      "check": "检查项 3",
      "description": "说明 3"
    },
    {
      "check": "检查项 4",
      "description": "说明 4"
    },
    {
      "check": "检查项 5",
      "description": "说明 5"
    }
  ]
}
```

**步骤 2:** 运行审查

```bash
py 30-scripts-tools\critic_v5_review.py --custom my_checklist.json
```

---

## 📊 审查报告

**自动生成位置:**
```
21-reports/critic-reviews/YYYY-MM-DD/critic-review-<scenario>-HHMMSS.md
```

**报告内容:**
- 审查场景
- 时间戳
- 所有检查项状态
- 统计 (通过/失败/跳过)
- 最终结果
- 失败项修复建议

**示例:**
```markdown
# 批判者 v5.0 审查报告

**场景:** 文件整理审查 (file_organize)
**时间:** 2026-03-18T14:30:00
**耗时:** 45.3 秒

## 审查结果

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 目标目录扫描完成 | ✅ | - |
| 备份方案确认 | ✅ | - |
| 重名处理逻辑验证 | ❌ | 发现__init___1_2_.py 模式 |
| ... | ... | ... |

**统计:**
- 通过：6 个
- 失败：1 个
- 跳过：0 个

**最终结果:** ❌ 不通过

## 建议

**失败项需修复后才能继续操作:**
- [ ] 重名处理逻辑验证：发现__init___1_2_.py 模式
```

---

## 🎯 集成到工作流程

### 方法 1: 手动调用 (推荐新手)

**在关键操作前:**
```bash
# 文件整理前
py 30-scripts-tools\critic_v5_review.py --scenario file_organize

# 如果通过，继续操作
py 30-scripts-tools\file-organizer.py --clean
```

---

### 方法 2: 脚本集成 (推荐)

**在脚本开头添加:**
```python
import subprocess
import sys

def run_critic_review(scenario: str) -> bool:
    """运行批判者审查"""
    result = subprocess.run(
        [sys.executable, '30-scripts-tools/critic_v5_review.py', 
         '--scenario', scenario],
        cwd=str(WORKSPACE)
    )
    return result.returncode == 0

# 主函数开头
if __name__ == '__main__':
    if not run_critic_review('file_organize'):
        print("[ERROR] 批判者审查未通过，中止操作")
        sys.exit(1)
    
    # 继续正常操作...
    main()
```

---

### 方法 3: Git Hook 集成 (高级)

**编辑 `.git/hooks/pre-commit`:**
```python
# 添加批判者审查
import subprocess

# Git 操作审查
result = subprocess.run(
    ['python', '30-scripts-tools/critic_v5_review.py', 
     '--scenario', 'git_operation'],
    capture_output=True
)

if result.returncode != 0:
    print("[ERROR] Git 操作审查未通过")
    sys.exit(1)
```

---

### 方法 4: 批处理包装

**创建 `safe-file-organize.bat`:**
```batch
@echo off
echo Running Critic Review first...
py 30-scripts-tools\critic_v5_review.py --scenario file_organize
if errorlevel 1 (
    echo [ERROR] Critic review failed!
    pause
    exit /b 1
)

echo Critic review passed. Running file organizer...
py 30-scripts-tools\file-organizer.py --clean
pause
```

---

## 📈 效果监控

### 审查统计

**每周检查:**
```bash
dir 21-reports\critic-reviews\*.md /s
```

**指标:**
- 审查次数
- 通过率
- 常见失败项
- 预防的问题数量

### 目标

| 指标 | 目标 | 当前 |
|------|------|------|
| 审查覆盖率 | ≥90% | 待统计 |
| 审查通过率 | ≥80% | 待统计 |
| 问题预防率 | 100% | 待统计 |
| 用户满意度 | ≥95/100 | 待统计 |

---

## ✅ 最佳实践

### 应该做的

1. **关键操作前必审查** - 文件整理、数据清理、工具优化
2. **如实回答问题** - 不要为了通过而敷衍
3. **修复失败项** - 不要跳过失败检查
4. **保存审查报告** - 方便回顾和审计
5. **持续改进检查项** - 根据经验优化模板

### 不应该做的

1. ❌ 跳过审查直接操作
2. ❌ 审查失败后使用 `--no-verify`
3. ❌ 填写虚假信息
4. ❌ 忽略失败建议
5. ❌ 不保存审查报告

---

## 🔗 相关文件

- `30-scripts-tools/critic_v5_review.py` - 主工具
- `30-scripts-tools/CRITIC-V5-EXPANSION-PLAN.md` - 扩展计划
- `21-reports/critic-reviews/` - 审查报告存储
- `SOUL.md` - 批判者原则
- `AGENTS.md` - 工作流程集成

---

## 🎯 快速参考

```bash
# 列出所有场景
py 30-scripts-tools\critic_v5_review.py --list

# 文件整理审查
py 30-scripts-tools\critic_v5_review.py --scenario file_organize

# 工具优化审查
py 30-scripts-tools\critic_v5_review.py --scenario tool_optimize

# 数据清理审查
py 30-scripts-tools\critic_v5_review.py --scenario data_cleanup

# 研究任务审查
py 30-scripts-tools\critic_v5_review.py --scenario research_start

# Git 操作审查
py 30-scripts-tools\critic_v5_review.py --scenario git_operation

# 自定义审查
py 30-scripts-tools\critic_v5_review.py --custom my_checklist.json
```

---

**最后更新:** 2026-03-18  
**维护者:** Claw (Autonomous Agent)  
**批判者评分:** 待审查
