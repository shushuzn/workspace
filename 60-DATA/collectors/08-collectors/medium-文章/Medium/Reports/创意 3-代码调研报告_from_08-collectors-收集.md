# 创意 3 验证 - 代码调研报告

**调研日期:** 2026-03-07  
**阶段:** 2/4 (代码调研)  
**目的:** 评估信念探针早退机制实现可行性

---

## 🔧 技术方案

### 1. HuggingFace 探针实现

**状态:** ✅ 可行

**可用资源:**
- `transformers` 库支持提取任意层激活
- `hooks` 机制可注册激活捕获
- 现成 probing 教程可用

**核心代码:**
```python
# 方法 1: 输出隐藏状态
outputs = model(input_ids, output_hidden_states=True)
hidden_states = outputs.hidden_states[layer_id]

# 方法 2: 注册 hook (推荐)
activations = []
def hook_fn(module, input, output):
    activations.append(output.detach())
handle = model.layer[layer_id].register_forward_hook(hook_fn)

# 推理后移除 hook
handle.remove()
```

**参考链接:**
- https://github.com/huggingface/transformers/tree/main/examples/research_projects
- https://huggingface.co/docs/transformers/internal/generation_utils

---

### 2. Transformer 激活提取

**状态:** ✅ 可行

**三种方法:**

| 方法 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| `output_hidden_states` | 获取所有层 | 简单直接 | 内存开销大 |
| `register_forward_hook` | 指定层 | 灵活，内存友好 | 需要手动管理 |
| `get_intermediate_layers` | ViT 专用 | 封装好 | 仅 ViT 支持 |

**推荐:** `register_forward_hook` — 灵活且内存友好

---

### 3. MMLU 数据集获取

**状态:** ✅ 可行

**获取方式:**
1. **HuggingFace Datasets** (推荐)
   ```python
   from datasets import load_dataset
   dataset = load_dataset("cais/mmlu", "all")
   ```

2. **官方 GitHub**
   - https://github.com/hendrycks/test
   - 包含 57 个学科，14000+ 题目

3. **本地缓存**
   - 约 50MB (纯文本)
   - 格式：CSV/JSON

**MVP 推荐:** 使用 MMLU subset (100-500 题)

---

### 4. 计算资源需求

**状态:** ✅ 可行 (消费级 GPU)

**最低配置:**
- **GPU:** RTX 3060 12GB (或同等)
- **内存:** 16GB RAM
- **存储:** 50GB (模型 + 数据集)

**推荐配置:**
- **GPU:** RTX 4090 24GB / A100 40GB
- **内存:** 32GB RAM
- **存储:** 100GB SSD

**模型选择:**
| 模型 | 参数量 | GPU 需求 | 适合场景 |
|------|--------|----------|----------|
| Llama-7B | 7B | 单卡 16GB | MVP 验证 |
| Llama-13B | 13B | 单卡 24GB | 正式实验 |
| Llama-70B | 70B | 多卡/量化 | 生产环境 |

**MVP 推荐:** Llama-7B (INT4 量化后 ~5GB)

---

### 5. 时间估算

**MVP 实现 (最小可行产品):**

| 任务 | 预计时间 | 优先级 |
|------|----------|--------|
| 环境搭建 | 1 小时 | P0 |
| 激活提取代码 | 2 小时 | P0 |
| 探针训练 | 2 小时 | P0 |
| 早退逻辑 | 2 小时 | P0 |
| 对比实验 | 4 小时 | P1 |
| 结果分析 | 2 小时 | P1 |
| **总计** | **13 小时** | - |

**分阶段执行:**
- **阶段 2 (今日):** 代码调研 — 1 小时 ✅
- **阶段 3 (投稿后):** MVP 实现 — 7 小时
- **阶段 4 (投稿后):** 实验分析 — 6 小时

---

## 📋 待办清单

### 立即可做 (不影响投稿)
- [x] 搜索 HuggingFace 探针实现
- [x] 查找激活提取方法
- [ ] 下载 MMLU subset (100 题)
- [ ] 搭建测试环境

### 投稿后执行
- [ ] 实现激活提取
- [ ] 训练信念探针
- [ ] 实现早退逻辑
- [ ] 运行对比实验
- [ ] 分析结果

---

## ⚠️ 风险提示

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 代码复现困难 | 低 | 中 | HuggingFace 生态成熟 |
| GPU 资源不足 | 中 | 中 | 使用量化模型 |
| 效果不达预期 | 低 | 低 | 论文明确报告 80% 节省 |
| 影响 Carbon 投稿 | 低 | 高 | 限制时间 ≤2 小时/天 |

---

## 💭 我的建议

**技术可行性:** ⭐⭐⭐⭐⭐
- HuggingFace 生态完善
- 代码示例丰富
- 消费级 GPU 可运行

**时间可行性:** ⭐⭐⭐⭐
- MVP 约 13 小时
- 可分阶段执行
- 不影响投稿

**建议行动:**
1. **今日:** 完成调研，记录技术细节 ✅
2. **明日:** 准备 Zenodo 上传 (优先)
3. **投稿前:** 仅做环境搭建 (≤2 小时/天)
4. **投稿后:** 完整实验验证

---

*调研报告 by Claw | 2026-03-07*
