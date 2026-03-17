# ✅ Pre-Flight Check - 操作前检查清单

**版本:** 1.0  
**生效:** 立即  
**强制:** ✅ 每次文件操作前必须检查

---

## 🎯 核心规则

### 目录使用规范
```
✅ D:\OpenClaw\workspace\    → 所有项目文件、脚本、报告、数据
✅ C:\Users\华为\.copaw\      → 仅 Agent 配置 (MEMORY.md, SOUL.md, PROFILE.md)
❌ C 盘其他位置              → 禁止创建工作文件
```

### 检查清单 (每次 write_file 前)

```markdown
## [Pre-Flight Check]

**1. 文件类型确认**
- [ ] 这是项目文件吗？ → D 盘
- [ ] 这是 Agent 配置吗？ → C 盘 (仅限 MEMORY/SOUL/PROFILE)
- [ ] 这是临时文件吗？ → D 盘 (完成后归档)

**2. 目录存在性确认**
- [ ] 目标目录存在吗？
- [ ] 有写入权限吗？
- [ ] 路径拼写正确吗？

**3. 路径验证**
- [ ] 路径以 D:\OpenClaw\workspace\ 开头？
- [ ] 路径不包含 C:\Users\华为\.copaw\ (除非是配置)？
- [ ] 路径长度 <260 字符？

**4. 备份确认**
- [ ] 如果覆盖现有文件，已备份吗？
- [ ] Git 仓库内吗？需要提交吗？

**5. 最终确认**
- [ ] 这是正确的位置吗？
- [ ] 未来能找到这个文件吗？
- [ ] 符合项目结构规范吗？
```

---

## 🔧 技术防护

### 1. 工作目录环境变量
```powershell
# PowerShell Profile (添加到此文件)
# $PROFILE 或 C:\Users\华为\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1

$env:OPENCLAW_WORKSPACE = "D:\OpenClaw\workspace"
$env:OPENCLAW_CONFIG = "C:\Users\华为\.copaw"

function cd-workspace {
    Set-Location $env:OPENCLAW_WORKSPACE
    Write-Host "🐾 OpenClaw Workspace: $env:OPENCLAW_WORKSPACE" -ForegroundColor Green
}

function cd-config {
    Set-Location $env:OPENCLAW_CONFIG
    Write-Host "⚙️ OpenClaw Config: $env:OPENCLAW_CONFIG" -ForegroundColor Yellow
}

# 快捷别名
Set-Alias cw cd-workspace
Set-Alias cc cd-config
```

**使用:**
```powershell
cw    # 快速切换到工作区
cc    # 快速切换到配置区
```

### 2. 文件创建防护脚本
```python
# D:\OpenClaw\workspace\30-scripts-tools\safedir.py
"""
安全目录检查 - 防止文件创建在错误位置
"""

import os
import sys
from pathlib import Path

WORKSPACE = r"D:\OpenClaw\workspace"
CONFIG = r"C:\Users\华为\.copaw"

ALLOWED_CONFIG_FILES = ["MEMORY.md", "SOUL.md", "PROFILE.md", "AGENTS.md"]

def check_path(file_path: str) -> bool:
    """检查路径是否合法"""
    path = Path(file_path).resolve()
    
    # 允许的配置目录
    if str(path).startswith(CONFIG):
        file_name = path.name
        if file_name not in ALLOWED_CONFIG_FILES:
            print(f"❌ 错误：C 盘只能创建配置文件: {ALLOWED_CONFIG_FILES}")
            print(f"   当前文件：{file_name}")
            print(f"   建议位置：{WORKSPACE}\\{file_name}")
            return False
        return True
    
    # 允许的工作区
    if str(path).startswith(WORKSPACE):
        return True
    
    # 其他位置 - 警告
    print(f"⚠️ 警告：文件将创建在非标准位置")
    print(f"   当前路径：{path}")
    print(f"   建议位置：{WORKSPACE}")
    response = input("继续？(y/N): ")
    return response.lower() == 'y'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if check_path(file_path):
            print(f"✅ 路径检查通过：{file_path}")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("用法：python safedir.py <文件路径>")
```

### 3. Git 钩子 (防止错误提交)
```bash
# D:\OpenClaw\workspace\.git\hooks\pre-commit
#!/bin/bash

# 检查是否有 C 盘文件被添加
C_FILES=$(git diff --cached --name-only | grep "^C:" || true)

if [ ! -z "$C_FILES" ]; then
    echo "❌ 错误：检测到 C 盘文件"
    echo "$C_FILES"
    echo ""
    echo "请将文件移动到 D:\\OpenClaw\\workspace\\"
    exit 1
fi

echo "✅ 预提交检查通过"
```

---

## 📋 操作流程优化

### 标准文件创建流程

```
1. 确定文件类型
   │
   ├─ 项目文件 → D:\OpenClaw\workspace\
   ├─ 配置文件 → C:\Users\华为\.copaw\ (仅限 MEMORY/SOUL/PROFILE)
   └─ 临时文件 → D:\OpenClaw\workspace\tmp\
   │
2. 运行 Pre-Flight Check
   │
   ├─ 目录存在吗？
   ├─ 路径正确吗？
   └─ 符合规范吗？
   │
3. 创建文件
   │
   └─ write_file(路径，内容)
   │
4. 验证
   │
   ├─ 文件存在吗？
   ├─ 内容正确吗？
   └─ Git 提交
```

### 错误纠正流程

```
发现错误
   │
1. 立即停止当前操作
   │
2. 记录错误到 MEMORY.md [SYS-XXX]
   │
3. 移动文件到正确位置
   │
4. 更新相关引用
   │
5. 添加防护机制 (防止再次发生)
   │
6. 测试防护机制
```

---

## 🎯 记忆强化

### 关键教训编号

| 编号 | 主题 | 内容 |
|------|------|------|
| **SYS-010** | 工作站位置 | D 盘是主工作站 |
| **SYS-011** | 配置目录 | C 盘仅存储配置 |
| **SYS-012** | Git 分离 | 两盘独立 Git 仓库 |
| **SYS-013** | 文件操作前检查 | 确认目录再操作 |
| **SYS-014** | 错误纠正 | 立即移动 + 记录 |
| **SYS-015** | 防护机制 | 自动化检查 |
| **SYS-016** | 工作目录混淆 | 默认路径问题 |
| **SYS-017** | Pre-Flight Check | 操作前强制检查 |

### 每日提醒 (HEARTBEAT.md)

```markdown
## 每日检查 (23:00)

- [ ] 所有新文件在 D 盘吗？
- [ ] C 盘只有配置文件吗？
- [ ] Git 提交包含错误路径吗？
- [ ] 有 SYS-XXX 教训需要记录吗？
```

---

## 📊 监控指标

### 错误追踪
```
目标：
- 文件位置错误：0 次/周
- 路径混淆：0 次/周
- 防护触发：>5 次/周 (说明在工作)

实际 (2026-03-14):
- 文件位置错误：1 次 (SYS-016)
- 防护机制：实施中
```

### 改进趋势
```
周次 | 错误数 | 防护触发 | 改进
-----|--------|----------|------
W1   | 1      | 0        | 基线
W2   | 0 (目标) | >5      | Pre-Flight Check
```

---

## 🚀 实施清单

### 立即实施 (今天)
- [x] 创建 Pre-Flight Check 文档
- [ ] 安装 PowerShell 快捷命令
- [ ] 创建 safedir.py 检查脚本
- [ ] 更新 HEARTBEAT.md 添加检查
- [ ] 记录教训 [SYS-017]

### 本周实施
- [ ] Git 钩子配置
- [ ] 自动化测试
- [ ] 监控指标追踪

### 长期优化
- [ ] AI 辅助路径建议
- [ ] 自动纠正机制
- [ ] 零错误目标

---

## 🎯 承诺

**我承诺:**
1. ✅ 每次文件操作前执行 Pre-Flight Check
2. ✅ 严格区分 D 盘 (工作) 和 C 盘 (配置)
3. ✅ 发现错误立即纠正并记录
4. ✅ 持续优化防护机制
5. ✅ 目标：零文件位置错误

---

**版本:** 1.0  
**生效:** 2026-03-14  
**下次审查:** 2026-03-21

---

*🐾 错误是学习机会 - 每次错误都让系统更强大！*
