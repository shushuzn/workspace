# 快速启动指南 - 上下文优化

**版本:** v1.0  
**生效时间:** 2026-03-18  
**目标:** 加载速度提升 9000x+

---

## 🚀 每次会话开始

### 1. 运行会话前检查
```bash
py 30-scripts-tools/pre-session-hook.py
```

**应该看到:**
```
✅ .contextignore
✅ 核心文件 (62.0KB)
✅ 禁止目录
✅ 所有检查通过！可以开始会话
```

### 2. 验证加载大小
```bash
py 30-scripts-tools/fast_load.py
```

**应该看到:**
```
总大小：60.8KB (0.06MB)
Token 估算：~15,559 tokens
速度提升：9442.6x
```

### 3. 开始工作
现在可以开始正常工作了！

---

## 📁 核心文件 (只加载这些)

```
SOUL.md           11.6KB
USER.md           10.6KB
AGENTS.md         10.7KB
TOOLS.md          5.7KB
HEARTBEAT.md      5.2KB
MEMORY.md         9.2KB
2026-03-18.md     8.9KB
────────────────────────
总计：62.0KB      (~15,500 tokens)
```

---

## 🚫 禁止扫描的目录

```
80-PROJECTS/      # 子仓库 (独立上下文)
40-arxiv/         # 自动收集内容
60-DATA/          # 数据文件
08-collectors/    # 收集器输出
99-backups/       # 备份
99-archive-归档/   # 旧工作区
**/deep/*-full.md # 论文完整内容
```

---

## ⚠️ 常见错误

### ❌ 错误：扫描全工作区
```bash
dir /s /b *.md           # 会扫描 18,346 个文件
grep -r "keyword" .      # 会搜索 560MB
```

### ✅ 正确：指定目录
```bash
dir 13-memory\*.md       # 只扫描记忆目录
grep -r "keyword" 13-memory/  # 只搜索记忆
```

### ❌ 错误：加载所有.md 文件
```python
# 会加载 560MB
for f in Path('.').rglob('*.md'):
    content = f.read_text()
```

### ✅ 正确：只加载核心文件
```python
# 只加载 62KB
core_files = [
    'SOUL.md', 'USER.md', 'AGENTS.md',
    'TOOLS.md', 'HEARTBEAT.md', 'MEMORY.md'
]
for f in core_files:
    content = Path(f).read_text()
```

---

## 🛠️ 工具清单

| 工具 | 用途 | 频率 |
|------|------|------|
| `pre-session-hook.py` | 会话前检查 | 每次会话 |
| `fast_load.py` | 验证加载大小 | 每次会话 |
| `context_compressor.py` | 会话后压缩 | 会话结束 |
| `memory_search.py` | 搜索记忆 | 按需使用 |

---

## 📊 性能对比

| 指标 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| **加载大小** | 560MB | 62KB | **-99.99%** |
| **Token 使用** | 140,000+ | 15,500 | **-89%** |
| **加载文件数** | 18,346 个 | 7 个 | **-99.96%** |
| **速度提升** | 1x | **9442x** |

---

## 🎯 检查清单

每次会话前确认:

- [ ] 运行 `pre-session-hook.py`
- [ ] 所有检查通过 (✅)
- [ ] 加载大小<100KB
- [ ] 只加载 7 个核心文件
- [ ] 未扫描禁止目录

---

## ⚡ 快速命令

```bash
# 完整启动流程
py 30-scripts-tools/pre-session-hook.py && py 30-scripts-tools/fast_load.py

# 只检查核心文件
py 30-scripts-tools/fast_load.py

# 查看.contextignore
cat .contextignore

# 查看会话状态
cat 13-memory/session-state.json
```

---

## 📈 监控指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 加载大小 | <100KB | 62KB ✅ |
| Token 使用 | <20K | ~15.5K ✅ |
| 速度提升 | >9000x | 9442x ✅ |
| 违规次数 | 0 | 0 ✅ |

---

## 🔧 故障排除

### 问题：加载还是很慢

**检查:**
1. 是否运行了 `pre-session-hook.py`?
2. 是否遵守.contextignore 规则？
3. 是否扫描了禁止目录？

**解决:**
```bash
# 重新运行检查
py 30-scripts-tools/pre-session-hook.py

# 查看加载大小
py 30-scripts-tools/fast_load.py

# 如果>100KB，检查是否加载了额外文件
```

### 问题：AI 还是扫描全工作区

**原因:** AI 未遵守.contextignore 规则

**解决:**
1. 提醒 AI 查看 `30-scripts-tools/AI-CONTEXT-RULES.md`
2. 检查 SOUL.md 和 AGENTS.md 是否更新
3. 运行 `pre-session-hook.py` 强制检查

---

## 📝 规则文档

- `30-scripts-tools/AI-CONTEXT-RULES.md` - AI 上下文规则 (强制执行)
- `SOUL.md` - 核心身份 (包含上下文加载规则)
- `AGENTS.md` - 工作区规则 (包含会话流程)
- `.contextignore` - 忽略目录列表

---

**强制执行！立即生效！不得违反！**

**最后更新:** 2026-03-18  
**下次审查:** 2026-03-25
