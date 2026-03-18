# Memory Tag System - 记忆标签系统

**版本:** 1.0  
**创建:** 2026-03-18  
**状态:** 生产就绪

---

## 快速开始

### 1. 生成索引 (首次使用)

```bash
cd D:\OpenClaw\workspace
py 30-scripts-tools\memory_index_generator.py --rebuild
```

### 2. 搜索记忆

```bash
# 按标签搜索
py 30-scripts-tools\memory_tag_search.py --tag critical

# 多标签搜索 (OR 逻辑)
py 30-scripts-tools\memory_tag_search.py --tag system tool

# 按关键词搜索
py 30-scripts-tools\memory_tag_search.py --query "research"

# 列出所有标签
py 30-scripts-tools\memory_tag_search.py --list-tags
```

---

## 标签分类

### 主要标签 (必需)

| 标签 | 说明 | 示例 |
|------|------|------|
| `#identity` | 核心身份、价值观 | SOUL.md 内容 |
| `#principle` | 操作原则、规则 | 零错误原则 |
| `#lesson` | 经验教训 | 调试失败教训 |
| `#system` | 系统架构、组件 | 7-Persona 系统 |
| `#tool` | 工具、脚本 | Memory distiller |
| `#workflow` | 工作流程、流程 | 会话压缩 |
| `#research` | 研究方法 | 学术诚信 |
| `#user-pref` | 用户偏好 | 无休息建议 |
| `#project` | 活跃项目 | 飞书集成 |
| `#metric` | 指标、KPI | 创新分数 |

### 优先级标签 (可选)

| 标签 | 说明 |
|------|------|
| `#critical` | 关键优先级 |
| `#high` | 高优先级 |
| `#medium` | 中优先级 |
| `#low` | 低优先级 |

---

## 标签格式

### MEMORY.md 中的格式

```markdown
## Section Title
**Tags:** #tag1 #tag2 #priority

Content here...
```

### 示例

```markdown
## Core Principles
**Tags:** #principle #critical

### Zero Error Principle
**Tags:** #principle #critical #lesson
```

---

## 自动化

### 会话结束自动更新

`end-session.bat` 执行流程:

```
会话结束
    ↓
post_session_compress.py (会话压缩)
    ↓
memory_index_generator.py (自动更新索引)
    ↓
✅ 索引保持最新
```

**用户无需手动操作!**

---

## 最佳实践

### 添加标签
1. **1-2 个主要标签** (必需)
2. **1 个优先级标签** (推荐)
3. **最多 5 个标签** (上限)
4. **统一命名** (小写，连字符)

### 维护索引
- ✅ 会话结束自动更新
- ✅ 编辑 MEMORY.md 后重建：`--rebuild`
- ❌ 不需要每次编辑都重建

---

## 文件位置

| 文件 | 路径 |
|------|------|
| MEMORY.md | `D:\OpenClaw\workspace\MEMORY.md` |
| 索引 | `D:\OpenClaw\workspace\13-memory\memory_index.json` |
| 索引生成器 | `30-scripts-tools\memory_index_generator.py` |
| 标签搜索 | `30-scripts-tools\memory_tag_search.py` |
| 会话压缩 | `30-scripts-tools\post_session_compress.py` |

---

## 故障排除

### "Index not found"

```bash
py 30-scripts-tools\memory_index_generator.py --rebuild
```

### "No results found"

1. 检查标签拼写 (区分大小写)
2. 使用 `--list-tags` 查看可用标签
3. 索引可能过期 - 运行 `--rebuild`

---

**维护者:** Claw  
**最后更新:** 2026-03-18
