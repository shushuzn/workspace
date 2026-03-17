# Medium 研究笔记：Intent Engineering

**日期:** 2026-03-07  
**文章:** Intent Engineering: The Missing Layer in AI Systems  
**作者:** Luna  
**来源:** Towards AI  
**URL:** https://pub.towardsai.net/intent-engineering-the-missing-layer-in-ai-systems-08fb2bf71453  
**互动:** 39 claps, 1 response  
**发布:** 22 hours ago

---

## 📌 核心观点

### AI 系统设计的三阶段演进

| 阶段 | 焦点 | 核心问题 |
|------|------|----------|
| 1. Prompt Engineering | 与模型对话 | How do we talk to the model? |
| 2. Context Engineering | 设计输入环境 | What context does the model receive? |
| 3. Intent Engineering | 编码系统目标 | What is the system actually trying to achieve? |

### 关键洞察

1. **AI 系统缺少"意图工程"层**
   - 当前 AI 代理系统过于依赖 prompt engineering
   - 缺少明确编码系统目标的机制

2. **可靠性问题**
   - 可靠 AI 代理不再依赖 prompt 或上下文
   - 关键是如何编码系统真正想要实现的目标

3. **意图 vs 提示**
   - Prompt: 告诉模型"怎么做"
   - Intent: 定义系统"想要什么"

4. **意图工程的价值**
   - 帮助 AI 系统优化正确的目标
   - 仅靠上下文，代理可能理解情况但仍选择错误行动
   - 明确的意图使决策与目标对齐

---

## 🔗 与创意 3 验证的关联

| 概念 | 信念探针 | 意图工程 |
|------|----------|----------|
| 目标 | 检测模型确定性 | 定义系统目标 |
| 方法 | 激活向量分析 | 意图编码 |
| 应用 | 早退机制 | 代理可靠性 |

**潜在整合:**
- 信念探针可作为"意图实现度"检测器
- 意图工程提供早退决策的语义基础
- 两者结合实现更智能的计算资源分配

---

## 💡 关键洞察

1. **早退机制的语义基础**
   - 当前早退基于置信度阈值
   - 加入意图理解可提升决策质量

2. **意图 - 信念对齐**
   - 模型信念是否对齐系统意图？
   - 可作为早退的额外判断条件

3. **未来研究方向**
   - 意图编码器设计
   - 意图 - 信念对齐度量化
   - 基于意图的自适应早退

---

## ⚠️ 待办事项

- [ ] 获取完整文章内容 (网络获取失败)
- [ ] 深入分析意图工程框架
- [ ] 设计意图 - 信念整合方案
- [ ] 实验验证整合效果

---

## 📚 相关研究

- 创意 3 验证：信念探针早退机制
- 阈值优化：最佳 0.80，节省 14.6%
- 事实类早退：75%，错误全模型：100%

---

*初步笔记，待补充完整内容分析*
