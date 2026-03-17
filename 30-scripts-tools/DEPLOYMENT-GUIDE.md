# 🚀 Memory Core v2.0 生产部署指南

**版本:** 2.0.0  
**部署日期:** 2026-03-17  
**状态:** 生产就绪

---

## 📋 部署清单

### 部署前检查

- [x] 所有模块集成完成
- [x] 测试全部通过
- [x] 文档完整
- [x] Git 提交完成
- [ ] 推送到远程仓库
- [ ] 更新现有脚本
- [ ] 配置生产环境
- [ ] 设置监控

---

## 🔧 部署步骤

### 1. 环境准备

```bash
# 检查工作目录
cd D:\OpenClaw\workspace

# 确认当前分支
git branch
# 应该在 master 分支

# 查看最新提交
git log --oneline -5
```

**预期输出:**
```
dd15cdc 📄 Add Memory Core v2.0 completion report
ea8a07b 🧩 Integrate all memory modules into MemoryCore
a18aa77 🧠 Create Memory Core v2.0 - Unified Memory System
```

---

### 2. 推送到远程仓库

由于分支保护，需要手动确认：

```bash
# 方式 1: 正常推送 (需要确认)
git push origin master

# 方式 2: 使用 SSH (如果遇到 HTTPS 问题)
git remote set-url origin git@github.com:shushuzn/obsidian-sync.git
git push origin master

# 方式 3: 强制推送 (谨慎使用)
git push origin master --force-with-lease
```

**推送后验证:**
```bash
# 查看远程状态
git status

# 查看远程分支
git branch -r
```

---

### 3. 配置生产环境

创建生产配置文件:

```bash
# 创建配置目录
mkdir -p 03-config

# 创建生产配置
cat > 03-config/memory_core_config.json << 'EOF'
{
  "workspace": "D:\\OpenClaw\\workspace",
  "memory_dir": "13-memory-记忆系统",
  "quality_threshold": 0.5,
  "low_quality_threshold": 0.3,
  "high_quality_threshold": 0.8,
  "max_associations": 10,
  "enable_cache": true,
  "cache_ttl": 300,
  "cache_max_size": 1000,
  "parallel_processing": true,
  "max_workers": 4,
  "auto_forget": false,
  "enable_logging": true,
  "log_level": "INFO",
  "log_file": "memory_core.log"
}
EOF
```

---

### 4. 更新现有脚本

创建迁移脚本，将旧脚本迁移到 MemoryCore:

**示例：更新 memory_search_v2.py**

```python
# 旧代码
from memory_search_v2 import MemorySearch
search = MemorySearch()
results = search.query("query")

# 新代码
from memory_core import MemoryCore
core = MemoryCore()
results = core.search("query")
```

---

### 5. 创建生产入口脚本

```python
#!/usr/bin/env python3
"""
Memory Core 生产入口
用于日常记忆管理任务
"""

import sys
import argparse
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / '30-scripts-tools'))

from memory_core import MemoryCore, MemoryConfig


def main():
    parser = argparse.ArgumentParser(description='Memory Core CLI')
    
    parser.add_argument('--process', '-p', type=str, help='处理记忆')
    parser.add_argument('--search', '-s', type=str, help='搜索记忆')
    parser.add_argument('--stats', action='store_true', help='显示统计')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径')
    parser.add_argument('--batch', '-b', type=str, help='批量处理文件')
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        config = MemoryConfig(config_path=args.config)
    
    # 初始化核心
    core = MemoryCore(config=config)
    
    # 处理记忆
    if args.process:
        memory = core.process(args.process)
        print(f"✓ 记忆已处理")
        print(f"  ID: {memory.id}")
        print(f"  分数：{memory.score:.2f}")
        print(f"  内容：{memory.content[:100]}...")
    
    # 搜索记忆
    elif args.search:
        results = core.search(args.search, limit=10)
        print(f"✓ 找到 {len(results)} 个结果:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.content[:80]}... (score={r.score:.2f})")
    
    # 显示统计
    elif args.stats:
        stats = core.get_stats()
        print("📊 记忆统计:")
        print(f"  总数：{stats['total']}")
        print(f"  平均分：{stats['avg_score']:.2f}")
        print(f"  高质量：{stats['high_quality']}")
        print(f"  低质量：{stats['low_quality']}")
    
    # 批量处理
    elif args.batch:
        with open(args.batch, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        memories = core.batch_process(lines, parallel=True)
        print(f"✓ 批量处理完成")
        print(f"  处理数量：{len(memories)}")
        print(f"  平均分：{sum(m.score for m in memories)/len(memories):.2f}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
```

保存为：`memory_core_cli.py`

---

### 6. 设置定时任务

**Windows 任务计划程序:**

```powershell
# 创建定时任务 - 每天凌晨 2 点运行记忆蒸馏
$action = New-ScheduledTaskAction -Execute "python" -Argument "memory_core_cli.py --stats"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "MemoryCore-DailyStats" -Action $action -Trigger $trigger -Principal $principal
```

**或者使用 cron (如果有):**

```bash
# 编辑 crontab
crontab -e

# 添加任务 - 每天早上 7 点发送统计
0 7 * * * cd /d/OpenClaw/workspace && python memory_core_cli.py --stats >> memory_core.log 2>&1
```

---

## 📊 监控配置

### 1. 性能监控

创建监控脚本 `monitor_memory_core.py`:

```python
#!/usr/bin/env python3
"""
Memory Core 性能监控
"""

import psutil
import json
from datetime import datetime
from pathlib import Path

def monitor():
    """监控系统资源"""
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('D:').percent,
    }
    
    # 保存到监控日志
    log_file = Path('20-data-reports/memory_core_monitor.json')
    
    if log_file.exists():
        with open(log_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    
    history.append(metrics)
    
    # 保留最近 1000 条记录
    history = history[-1000:]
    
    with open(log_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print(f"✓ 监控数据已记录")
    print(f"  CPU: {metrics['cpu_percent']}%")
    print(f"  内存：{metrics['memory_percent']}%")
    print(f"  磁盘：{metrics['disk_usage']}%")

if __name__ == '__main__':
    monitor()
```

---

### 2. 错误监控

创建错误日志分析脚本:

```python
#!/usr/bin/env python3
"""
Memory Core 错误日志分析
"""

import re
from pathlib import Path
from datetime import datetime, timedelta

def analyze_errors(log_file='memory_core.log', hours=24):
    """分析最近 N 小时的错误"""
    
    log_path = Path(log_file)
    if not log_path.exists():
        print("日志文件不存在")
        return
    
    errors = []
    cutoff = datetime.now() - timedelta(hours=hours)
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 解析日志行
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)', line)
            if match:
                timestamp_str, level, message = match.groups()
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                if timestamp >= cutoff and level in ['ERROR', 'WARNING']:
                    errors.append({
                        'timestamp': timestamp,
                        'level': level,
                        'message': message
                    })
    
    # 统计
    print(f"📊 错误分析 (最近 {hours} 小时):")
    print(f"  总错误数：{len([e for e in errors if e['level'] == 'ERROR'])}")
    print(f"  总警告数：{len([e for e in errors if e['level'] == 'WARNING'])}")
    
    # 显示最近的错误
    if errors:
        print("\n最近的错误:")
        for error in errors[-5:]:
            print(f"  [{error['timestamp']}] {error['level']}: {error['message']}")

if __name__ == '__main__':
    analyze_errors()
```

---

## 🔄 迁移现有脚本

### 迁移清单

| 旧脚本 | 新 API | 状态 |
|--------|--------|------|
| memory_search_v2.py | core.search() | 待迁移 |
| memory_quality_scorer.py | core.quality.evaluate() | 待迁移 |
| memory_distiller_v2.py | core.distiller.compress() | 待迁移 |
| memory_association.py | core.association.find() | 待迁移 |
| memory_forgetting.py | core.forgetting.execute() | 待迁移 |
| memory_conflict_detector.py | core.conflict.detect() | 待迁移 |

### 迁移示例

**memory_search_v2.py → MemoryCore**

```python
# 旧代码
from memory_search_v2 import MemorySearch
search = MemorySearch()
results = search.query("Python", limit=10)

# 新代码
from memory_core import MemoryCore
core = MemoryCore()
results = core.search("Python", limit=10)
```

**memory_quality_scorer.py → MemoryCore**

```python
# 旧代码
from memory_quality_scorer import MemoryQualityScorer
scorer = MemoryQualityScorer()
score = scorer.evaluate(memory)

# 新代码
from memory_core import MemoryCore
core = MemoryCore()
score = core.evaluate(memory)
```

---

## 📈 性能基准

创建基准测试脚本 `benchmark_memory_core.py`:

```python
#!/usr/bin/env python3
"""
Memory Core 性能基准测试
"""

import time
from memory_core import MemoryCore

def benchmark():
    core = MemoryCore()
    
    # 测试 1: 单个处理
    start = time.time()
    for i in range(100):
        core.process(f"测试记忆 {i}")
    duration = time.time() - start
    print(f"✓ 单个处理 (100 个): {duration:.2f}s ({duration/100*1000:.2f}ms/个)")
    
    # 测试 2: 批量处理
    memories = [f"批量测试 {i}" for i in range(100)]
    start = time.time()
    core.batch_process(memories, parallel=False)
    duration = time.time() - start
    print(f"✓ 批量串行 (100 个): {duration:.2f}s ({duration/100*1000:.2f}ms/个)")
    
    # 测试 3: 批量并行
    start = time.time()
    core.batch_process(memories, parallel=True)
    duration = time.time() - start
    print(f"✓ 批量并行 (100 个): {duration:.2f}s ({duration/100*1000:.2f}ms/个)")
    
    # 测试 4: 搜索
    start = time.time()
    for _ in range(10):
        core.search("测试", limit=10)
    duration = time.time() - start
    print(f"✓ 搜索 (10 次): {duration:.2f}s ({duration/10*1000:.2f}ms/次)")
    
    # 测试 5: 缓存命中率
    if core.cache:
        stats = core.cache.get_stats()
        print(f"✓ 缓存命中率：{stats['hit_rate']}")
    
    # 性能报告
    print("\n📊 性能报告:")
    print(core.get_performance_report())

if __name__ == '__main__':
    benchmark()
```

---

## 🎯 验收标准

### 功能验收

- [ ] 处理记忆功能正常
- [ ] 搜索功能正常
- [ ] 质量评估正常
- [ ] 关联分析正常
- [ ] 遗忘管理正常
- [ ] 冲突检测正常
- [ ] 缓存工作正常
- [ ] 性能监控正常

### 性能验收

- [ ] 单个处理 < 50ms
- [ ] 批量处理 < 10ms/个 (并行)
- [ ] 搜索 < 100ms/次
- [ ] 缓存命中率 > 50%
- [ ] 内存占用 < 500MB

### 稳定性验收

- [ ] 连续运行 24 小时无崩溃
- [ ] 错误率 < 0.1%
- [ ] 日志记录完整
- [ ] 监控数据正常

---

## 🚨 回滚方案

如果部署失败，回滚到旧版本:

```bash
# 1. 停止所有 Memory Core 相关进程
taskkill /F /IM python.exe

# 2. 恢复备份
git checkout HEAD~3  # 回滚到阶段 1 之前

# 3. 恢复旧脚本
xcopy /E /I backup\memory-scripts\ 30-scripts-tools\

# 4. 验证旧系统
python memory_search_v2.py --help
```

---

## 📞 支持与反馈

### 问题报告

如果遇到问题:

1. 查看日志文件 `memory_core.log`
2. 运行诊断脚本 `diagnose_memory_core.py`
3. 查看错误分析 `analyze_errors.py`
4. 提交 issue 到 GitHub

### 性能优化

如果性能不达标:

1. 增加缓存大小
2. 调整并行工作线程数
3. 减少关联数量限制
4. 优化查询语句

---

## 🎉 部署完成检查

部署完成后，运行验证脚本:

```bash
python verify_deployment.py
```

**预期输出:**
```
✓ Memory Core v2.0 部署验证
✓ 所有模块加载成功
✓ 基础功能测试通过
✓ 性能基准达标
✓ 监控系统正常
✓ 日志系统正常
✓ 部署完成！
```

---

*Memory Core v2.0 Production Deployment Guide* 🐾  
**2026-03-17**
