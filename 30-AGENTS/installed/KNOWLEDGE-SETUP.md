# 🧠 知识库配置

**创建日期:** 2026-03-27

---

## 知识库结构

```
D:\OpenClaw\workspace\knowledge\
├── roundtable/           # AI 圆桌讨论
│   ├── INDEX.md
│   └── *.md
├── superpowers/        # Agent 超能力
│   ├── specs/         # 设计文档
│   ├── plans/         # 实施计划
│   └── tests/         # 测试用例
├── domain-research/    # 领域研究
├── papers/           # 论文收藏
└── docs/            # 知识文档
```

---

## 知识分类

### 按领域

| 领域 | 路径 | 说明 |
|------|------|------|
| AI/ML | `knowledge/ai/` | AI 相关知识 |
| 开发 | `knowledge/dev/` | 开发最佳实践 |
| 产品 | `knowledge/product/` | 产品设计 |
| 商业 | `knowledge/business/` | 商业模式 |
| 安全 | `knowledge/security/` | 安全知识 |

### 按类型

| 类型 | 格式 | 示例 |
|------|------|------|
| 概念 | `.md` | 解释性文档 |
| 教程 | `.md` | 操作指南 |
| 参考 | `.md` / `.json` | API 文档 |
| 模板 | `.md` / `.yaml` | 复用模板 |

---

## 知识获取

### 搜索

```bash
# 搜索关键词
搜索 "AI agent"

# 搜索标签
grep_search "tag:productivity" knowledge/

# 全文搜索
grep_search "OpenClaw" knowledge/
```

### 更新

```bash
# 添加知识
# 直接创建 .md 文件到对应目录

# 更新知识
# 编辑现有文件

# 删除知识
# 删除文件并更新 INDEX
```

---

## 知识组织原则

### 命名规范

```
{YYYY-MM-DD}-{category}-{title}.md

示例:
2026-03-27-dev-github-workflow.md
2026-03-27-ai-llm-comparison.md
```

### 文档结构

```markdown
# 标题

## 概述
1-2 句话说明

## 详细内容
...

## 相关链接
- [链接1](url)
- [链接2](url)

## 标签
#标签1 #标签2
```

---

## RAG 配置 (可选)

如果启用检索增强生成:

```yaml
rag:
  enabled: false
  chunk_size: 512
  overlap: 50
  embedding_model: "text-embedding-ada-002"
  
  sources:
    - path: "knowledge/**/*.md"
      enabled: true
    - path: "30-AGENTS/installed/*.md"
      enabled: true
    - path: "memory/*.md"
      enabled: false  # 敏感，不启用
```

---

## 知识同步

| 来源 | 同步频率 | 状态 |
|------|----------|------|
| 本地文档 | 实时 | ✅ |
| GitHub Wiki | 每日 | ⚠️ |
| Notion | 手动 | ❌ |
| 外部 RSS | 每小时 | ❌ |

---

## 知识质量标准

### 好知识的标准

- [ ] 标题清晰
- [ ] 有概述/摘要
- [ ] 内容完整
- [ ] 有实例/代码
- [ ] 有相关链接
- [ ] 有标签分类

### 需要更新的标志

- [ ] 信息过时 (>6 个月)
- [ ] 链接失效
- [ ] 内容不完整
- [ ] 格式混乱

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `搜索知识` | 全局搜索知识库 |
| `添加知识` | 创建新知识文档 |
| `更新知识` | 更新现有文档 |
| `知识索引` | 查看知识库结构 |
