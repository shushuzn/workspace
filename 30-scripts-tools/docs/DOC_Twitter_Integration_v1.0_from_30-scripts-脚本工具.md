# Twitter 监听集成文档

**创建时间:** 2026-03-05 02:40  
**任务:** 1.4 与现有系统集成  
**状态:** ✅ 完成

---

## 🔗 集成点

### 1. 知识蒸馏集成

**触发条件:** 新推文收集后

**流程:**
```
Twitter Watcher
    ↓
收集推文 (190 条/日)
    ↓
保存为 Markdown
    ↓
触发 knowledge-distiller
    ↓
提取观点 → MEMORY.md
```

**配置:**
- 监控目录：`Twitter/YYYY-MM-DD/`
- 触发方式：文件变化检测
- 蒸馏频率：每 4 小时

---

### 2. 论文关联

**功能:** 自动关联推文提到的论文

**实现:**
1. 提取推文中的 arXiv 链接
2. 匹配本地论文库
3. 创建双向引用

**示例:**
```markdown
**相关论文:**
- [2603.00267] Multi-Sourced, Multi-Agent Evidence Retrieval
```

---

### 3. 专家识别

**功能:** 识别 AI 领域专家

**标准:**
- 推文质量 (点赞/转发比)
- 话题相关性 (AI/ML)
- 影响力指标

**输出:**
```json
{
  "username": "karpathy",
  "expertise": ["LLM", "Computer Vision"],
  "influence_score": 0.95
}
```

---

## 📁 目录结构

```
Twitter/
├── 2026-03-05/
│   ├── elonmusk-2026-03-05.md
│   ├── sama-2026-03-05.md
│   └── ...
├── experts.json
└── integration-config.yaml
```

---

## ⏭️ 下一步

**任务 1.5:** 定时任务配置
- 每 4 小时检查更新
- 失败重试机制
- 日志记录

---

*最后更新：2026-03-05 02:40*
