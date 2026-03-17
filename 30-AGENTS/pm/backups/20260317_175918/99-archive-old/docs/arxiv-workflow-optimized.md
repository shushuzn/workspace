# Arxiv 工作流优化架构 v2

**版本:** 2.0  
**日期:** 2026-03-03  
**优化目标:** 并行处理 + 上下文压缩

---

## 架构对比

### v1 架构（串行）

```
arxiv-collector → priority-scorer → paper2md(单篇) → P-Note
                                          ↓
                                    5 篇 = 25 分钟
```

### v2 架构（并行）

```
arxiv-collector → priority-scorer → 子代理池 (3-5 个) → P-Note
                                         ↓
                                   5 篇 = 5-7 分钟
```

**效率提升:** ~70%

---

## 核心组件

### 1. arxiv-collector v2
- **路径:** `D:\obsidian\Vault\scripts\arxiv-collector-v2.py`
- **功能:** 每日收集 100 篇论文（9 个领域）
- **去重:** extract_arxiv_id + check_paper_exists
- **输出:** `D:\obsidian\Vault\arxiv\daily\YYYY\MM\DD\`

### 2. priority-scorer
- **路径:** `D:\obsidian\Vault\scripts\arxiv-priority-scorer.py`
- **功能:** 基于关键词加权评分
- **阈值:** ≥10 高优先级，≥5 中优先级，<5 低优先级
- **输出:** `{date}-priority.md`

### 3. batch-processor（新增）
- **路径:** `C:\Users\华为\.openclaw\workspace\arxiv-batch-processor.py`
- **功能:** 
  - 解析优先级报告
  - 创建 P-Note 模板
  - 生成子代理任务配置
- **模式:** template / subagent

### 4. 子代理并行处理
- **运行时:** sessions_spawn(runtime="subagent")
- **并行数:** 3-5 个（根据 CPU/内存调整）
- **超时:** 600 秒/篇
- **标签:** paper-analysis-{paper-name}

---

## 工作流命令

### 步骤 1: 收集论文
```powershell
py D:\obsidian\Vault\scripts\arxiv-collector-v2.py --domains cs.AI,cs.LG,cs.CV,cs.CL,cs.IR,cs.SE,cs.DC,cs.RO,cs.SY,stat.ML
```

### 步骤 2: 优先级评分
```powershell
py D:\obsidian\Vault\scripts\arxiv-priority-scorer.py --date 2026-03-02
```

### 步骤 3: 批量处理（模板创建 + 子代理）
```powershell
# 创建 P-Note 模板
py C:\Users\华为\.openclaw\workspace\arxiv-batch-processor.py --date 2026-03-02 --mode template --max-workers 5

# 手动 spawn 子代理（或通过 OpenClaw 会话）
# 每个子代理处理 1 篇论文
```

### 步骤 4: 验证输出
```powershell
dir D:\obsidian\Vault\Medium\P-*.md
```

---

## 子代理任务模板

```python
sessions_spawn(
    task="""深度解析论文并填充 P-Note 模板。论文信息：
- arxiv_id: {arxiv_id}
- title: {title}
- score: {score}
- template_path: {template_path}

任务：
1. 读取论文源文件
2. 分析论文核心内容
3. 填充 P-Note 模板的 11 个维度
4. 保存回原文件

输出要求：
- 高密度信息，无 emoji
- 中文回复
- 结构化输出
""",
    label=f"paper-analysis-{paper_name}",
    mode="run",
    runtime="subagent",
    timeoutSeconds=600
)
```

---

## P-Note 11 维度模板

```markdown
---
type: P-Note
arxiv_id: {arxiv_id}
title: {title}
parsed_date: {date}
priority_score: {score}
tags: [arxiv, p-note, {category}]
---

# {title}

## Research Question Card
**核心问题:** [待填写]
**先验判断:** [待填写]
**重要性:** ⭐⭐⭐⭐⭐

---

## 1. 背景与动机
## 2. 核心问题定义
## 3. 方法结构
## 4. 关键创新
## 5. 实验分析
## 6. 对抗式审稿
## 7. 优势与局限
## 8. 本质抽象
## 9. 方法对比
## 10. 决策表格
## 11. 整体判断
```

---

## 性能指标

| 指标 | v1（串行） | v2（并行） | 改进 |
|------|-----------|-----------|------|
| 5 篇处理时间 | ~25 分钟 | ~5-7 分钟 | **70%+** |
| 单篇平均时间 | 5 分钟 | 5-7 分钟 | - |
| 并发度 | 1 | 3-5 | **5x** |
| 人工干预 | 每篇 | 批量 | **80% 减少** |

---

## 下一步优化

### 短期（本周）
- [ ] 集成 claude-context-mode 压缩上下文（98% 压缩率）
- [ ] 自动化子代理 spawn 逻辑
- [ ] 添加进度追踪和错误重试

### 中期（本月）
- [ ] 知识库集成（避免重复分析）
- [ ] 模糊搜索优化（快速定位相关论文）
- [ ] 渐进式搜索节流

### 长期（Q2）
- [ ] 多节点分布式处理
- [ ] 自动论文聚类（主题分组）
- [ ] 趋势预测模型

---

## 故障处理

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 子代理超时 | 论文过长/复杂 | 增加 timeoutSeconds 或分片处理 |
| 模板解析失败 | 格式不匹配 | 检查 priority report 格式 |
| 去重失效 | arxiv ID 提取错误 | 验证 extract_arxiv_id 正则 |
| 编码错误 | GBK/UTF-8 混用 | 统一使用 UTF-8，避免 emoji |

### 调试命令
```powershell
# 检查子代理状态
sessions_list --activeMinutes 10

# 查看子代理输出
sessions_history --sessionKey {key} --limit 50

# 终止子代理
subagents --action kill --target {id}
```

---

*工作流持续优化中，最后更新：2026-03-03 14:25*
