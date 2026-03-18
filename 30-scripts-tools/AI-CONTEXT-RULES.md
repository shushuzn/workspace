# AI 上下文加载规则 (强制执行)

**版本:** v1.0  
**生效时间:** 2026-03-18  
**优先级:** 最高 (高于所有其他规则)

---

## 🔒 核心原则

**每次会话开始时，AI 必须:**

1. ✅ **只加载 7 个核心文件** (总大小<100KB)
2. ❌ **禁止扫描全工作区** (560MB)
3. ❌ **禁止加载.contextignore 中的目录**
4. ✅ **使用 fast_load.py 验证**

---

## 📁 核心文件清单 (仅加载这些)

```
根目录/
├── SOUL.md              (11KB)
├── USER.md              (11KB)
├── AGENTS.md            (10KB)
├── TOOLS.md             (6KB)
├── HEARTBEAT.md         (5KB)
├── MEMORY.md            (9KB)
└── 13-memory/
    └── 2026-03-18.md    (9KB)  # 当日笔记

总计：61KB (~15,500 tokens)
```

**禁止加载:**
- ❌ 其他日常笔记 (除非用户明确要求)
- ❌ 研究论文 (08-collectors/, 60-DATA/)
- ❌ 子仓库 (80-PROJECTS/)
- ❌ 备份目录 (99-backups/, 99-archive/)
- ❌ 测试文件 (92-tests/)

---

## 🚫 .contextignore 规则 (必须遵守)

```
80-PROJECTS/              # 子仓库 - 独立上下文
40-arxiv/                 # 自动收集内容
41-medium/
42-hackernews/
60-DATA/                  # 数据文件
08-collectors/            # 收集器输出
99-backups/               # 备份
99-archive-归档/           # 旧工作区
91-logs/                  # 日志
92-tests/                 # 测试
**/deep/*-full.md         # 论文完整内容
node_modules/             # 依赖
venv/                     # 虚拟环境
__pycache__/              # Python 缓存
*.pyc                     # 编译文件
```

**违反后果:**
- 加载时间增加 9000x
- Token 浪费 89%
- 用户体验极差

---

## ✅ 正确做法

### 会话开始
```bash
# 1. 快速加载核心文件
py 30-scripts-tools/fast_load.py

# 2. 验证加载大小 (<100KB)
# 输出应显示：总大小：60.8KB

# 3. 开始工作
```

### 需要额外文件时
```bash
# ❌ 错误：扫描全工作区
dir /s /b *.md

# ✅ 正确：按需加载特定文件
read_file 10-RESEARCH/domain-research/README.md

# ✅ 正确：使用搜索工具
py 30-scripts-tools/memory_search.py --query "xxx"
```

### 需要搜索时
```bash
# ❌ 错误：全工作区 grep
grep -r "keyword" .

# ✅ 正确：使用索引搜索
py 30-scripts-tools/search_index.py --query "keyword"

# ✅ 正确：指定目录搜索
grep -r "keyword" 13-memory/
```

---

## 📊 性能对比

| 操作 | 错误做法 | 正确做法 | 速度提升 |
|------|----------|----------|----------|
| **启动加载** | 560MB (140K tokens) | 61KB (15K tokens) | **9442x** |
| **文件搜索** | 全工作区 grep | 指定目录 grep | **100x** |
| **内容扫描** | 扫描所有.md | 只扫描核心 7 个 | **2600x** |
| **Token 使用** | 140,000+ | 15,500 | **-89%** |

---

## 🔍 验证方法

### 每次会话检查
```bash
# 检查加载大小
py 30-scripts-tools/fast_load.py

# 应该看到：
# ✅ 总大小：60.8KB (0.06MB)
# ✅ Token 估算：~15,559 tokens
# ✅ 速度提升：9442.6x
```

### 如果超过 100KB
```bash
# 1. 检查是否加载了额外文件
# 2. 检查是否扫描了.contextignore 目录
# 3. 立即纠正
```

---

## 🎯 AI 行为准则

### ✅ 应该做的
1. 会话开始只加载 7 个核心文件
2. 需要额外信息时，使用搜索工具
3. 按需加载特定文件 (read_file)
4. 定期运行 fast_load.py 验证
5. 遵守.contextignore 规则

### ❌ 禁止做的
1. 扫描全工作区 (560MB)
2. 加载.contextignore 中的目录
3. 一次性读取大量文件
4. 使用全工作区 grep/search
5. 忽略性能影响

---

## 🛠️ 工具支持

### fast_load.py
```bash
# 验证加载大小
py 30-scripts-tools/fast_load.py

# 输出示例：
# ✅ SOUL.md: 11.0KB
# ✅ USER.md: 10.6KB
# ...
# 总大小：60.8KB
# 速度提升：9442.6x
```

### context_compressor.py
```bash
# 会话结束压缩上下文
py 30-scripts-tools/context_compressor.py --demo

# 保存到记忆文件
# 下次会话只加载压缩摘要
```

### memory_search.py
```bash
# 搜索记忆，不扫描全工作区
py 30-scripts-tools/memory_search.py --query "xxx"
```

---

## 📈 监控指标

| 指标 | 目标 | 检查频率 |
|------|------|----------|
| **加载大小** | <100KB | 每次会话 |
| **Token 使用** | <20,000 | 每次会话 |
| **加载文件数** | 7 个 | 每次会话 |
| **速度提升** | >9000x | 每次会话 |
| **违规次数** | 0 | 每周统计 |

---

## ⚠️ 违规处理

### 第一次违规
- 警告提醒
- 立即纠正
- 记录日志

### 第二次违规
- 严重警告
- 批判者审查
- 删除违规文件

### 第三次违规
- 启动完整审查
- 更新 SOUL.md
- 重新训练 AI

---

## 📝 实施清单

- [x] 创建.contextignore
- [x] 创建 fast_load.py
- [x] 创建 AI-CONTEXT-RULES.md (本文件)
- [ ] AI 遵守规则 (每次会话)
- [ ] 违规监控 (每周检查)
- [ ] 性能统计 (每周报告)

---

## 🎯 关键公式

```
快速加载 = 核心 7 文件 (61KB)
        = 15,500 tokens
        = 9442x 速度提升

慢速加载 = 全工作区 (560MB)
         = 140,000+ tokens
         = 用户体验极差
```

---

**强制执行！立即生效！不得违反！**

**版本:** v1.0  
**最后更新:** 2026-03-18  
**下次审查:** 2026-03-25
