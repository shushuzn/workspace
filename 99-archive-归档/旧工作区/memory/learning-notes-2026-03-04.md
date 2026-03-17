# 学习笔记 - Claude Skills 与 Twitter 内容获取

**学习时间:** 2026-03-04 19:54 HKT  
**来源:** Twitter @sanbuphy + 技术实践  
**主题:** AI 辅助开发工具 + 内容获取方法

---

## 📚 第一部分：Claude Skills 学习

### 8 个推荐 Skills 详解

#### 1️⃣ Planning with Files - 任务规划
**功能:** 多文件任务规划与分解

**核心能力:**
- 读取项目文件结构
- 分析依赖关系
- 生成任务执行计划
- 追踪进度

**使用场景:**
- 大型重构项目
- 新功能开发
- 跨文件修改

**关联知识:** [AG-001] 认知 - 运行分离
- Planning = Cognitive Blueprint (认知层)
- Execution = Runtime Engine (运行层)

**实践建议:**
```
1. 上传项目文件结构
2. 描述目标功能
3. 让 Skills 生成任务清单
4. 逐项执行并验证
```

---

#### 2️⃣ Web Quality Skills - 前端质量
**功能:** 前端代码质量检查

**核心能力:**
- HTML/CSS/JS 规范检查
- 可访问性 (A11Y) 审核
- 性能优化建议
- 最佳实践遵循

**使用场景:**
- Code Review
- 上线前检查
- 技术债务清理

**实践建议:**
```
1. 粘贴前端代码
2. 运行质量检查
3. 修复高优先级问题
4. 建立质量基线
```

---

#### 3️⃣ HashiCorp Skills - Terraform
**功能:** 基础设施即代码工具

**核心能力:**
- Terraform 配置生成
- 资源依赖分析
- 最佳实践应用
- 错误诊断

**使用场景:**
- 云资源部署
- 基础设施变更
- 多环境管理

**实践建议:**
```
1. 描述基础设施需求
2. 生成 Terraform 配置
3. 运行 terraform plan 验证
4. 应用变更
```

---

#### 4️⃣ Full Delivery Workflow - 完整交付
**功能:** 端到端交付流程

**核心能力:**
- 需求分析
- 任务分解
- 代码实现
- 测试验证
- 部署发布

**使用场景:**
- 完整功能开发
- 敏捷迭代
- DevOps 流程

**实践建议:**
```
1. 描述用户需求
2. Skills 分解为任务
3. 逐项实现
4. 自动化测试
5. 部署验证
```

---

#### 5️⃣ Core Engineering - TDD 调试重构
**功能:** 核心工程实践

**核心能力:**
- 测试驱动开发 (TDD)
- 调试诊断
- 代码重构
- 设计模式应用

**使用场景:**
- 复杂逻辑开发
- Bug 修复
- 代码优化

**实践建议:**
```
TDD 流程:
1. 编写失败测试
2. 实现最小功能
3. 运行测试通过
4. 重构优化
5. 重复循环
```

---

#### 6️⃣ PR Review - 代码审查
**功能:** Pull Request 审查

**核心能力:**
- 代码质量评估
- 潜在 Bug 检测
- 最佳实践检查
- 改进建议生成

**使用场景:**
- 合并前审查
- 团队代码审核
- 学习优秀代码

**实践建议:**
```
1. 提交 PR diff
2. Skills 自动审查
3. 修复高优先级问题
4. 迭代改进
```

---

#### 7️⃣ Snyk Fix - 漏洞修复
**功能:** 安全漏洞自动修复

**核心能力:**
- 依赖漏洞扫描
- 自动修复建议
- 安全版本升级
- 影响范围评估

**使用场景:**
- 安全审计
- 依赖更新
- 合规检查

**实践建议:**
```
1. 运行 Snyk 扫描
2. 查看漏洞列表
3. 应用自动修复
4. 测试验证
```

---

#### 8️⃣ Snyk Learn Path - 安全学习
**功能:** 安全知识学习路径

**核心能力:**
- 个性化学习推荐
- 安全最佳实践
- 案例分析
- 技能评估

**使用场景:**
- 团队安全培训
- 个人技能提升
- 合规要求学习

**实践建议:**
```
1. 评估当前水平
2. 选择学习路径
3. 完成实践练习
4. 获得认证
```

---

## 🔧 第二部分：技术方法学习

### Twitter CDN API 获取方法

#### 成功方法

**端点:**
```
https://cdn.syndication.twimg.com/tweet-result?id={TWEET_ID}&token=1
```

**请求示例:**
```python
import requests

tweet_id = "2028853137822630276"
url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&token=1"

response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
data = response.json()

# 提取关键字段
text = data.get('text', '')
user = data.get('user', {}).get('name', '')
created_at = data.get('created_at', '')
favorite_count = data.get('favorite_count', 0)
```

**返回数据结构:**
```json
{
  "__typename": "Tweet",
  "lang": "zh",
  "favorite_count": 57,
  "created_at": "2026-03-03T15:20:56.000Z",
  "text": "推文内容...",
  "user": {
    "id_str": "...",
    "name": "Sanbu",
    "screen_name": "sanbuphy"
  }
}
```

#### 失败方法总结

| 方法 | 状态 | 原因 |
|------|------|------|
| vxtwitter.com | ❌ | 重定向回原站 |
| nitter.net | ❌ | 连接超时 |
| fixupx.com | ❌ | 无法访问 |
| bird.fans | ❌ | SSL 错误 |
| indiebird.com | ❌ | 落地页重定向 |
| Twitter API v1.1 | ❌ | 需要认证 |

#### 关键洞察

**为什么 CDN API 有效？**
1. **公开内容分发:** Twitter CDN 用于公开推文分发
2. **无需认证:** 设计用于嵌入式场景
3. **速率限制宽松:** 相比正式 API 更宽松
4. **JSON 格式:** 结构化数据易于解析

**使用注意事项:**
- ⚠️ 仅限公开推文
- ⚠️ 可能有速率限制
- ⚠️ API 可能变更
- ⚠️ 遵守 Twitter 使用条款

---

## 🧠 第三部分：知识整合

### 关联现有知识体系

#### [MCP-001] MCP 正在成为 LLM 与外部系统连接的标准协议

**Claude Skills 与 MCP 的关系:**
- Skills = MCP 工具的具体应用
- 标准化接口 = MCP 协议
- 工具生态 = MCP 服务器网络

**证据:**
- Skills 提供标准化工具调用
- 覆盖开发全流程
- 可组合使用

#### [AG-001] 认知 - 运行分离是 Agentic AI 的必要架构

**Planning with Files 的体现:**
- Planning Agent = 认知层 (做什么)
- Execution Agent = 运行层 (怎么做)
- 文件作为中间表示

**证据:**
- 先规划后执行
- 任务分解清晰
- 进度可追踪

#### [MCP-005] Claude Skills 是 MCP 生态的开发者工具应用

**新增观点 (今日学习):**
- 8 个 Skills 覆盖完整工作流
- 从规划到交付闭环
- 安全与质量并重

---

## 📋 第四部分：实践计划

### 高优先级 (本周)

- [ ] **测试 Planning with Files**
  - 选择一个实际项目
  - 让 Skills 生成任务计划
  - 执行并记录效果

- [ ] **研究 Skills 与 MCP 关系**
  - 对比 Skills 与 MCP 工具
  - 分析架构差异
  - 输出对比报告

- [ ] **评估 PR Review 效果**
  - 提交真实 PR
  - 对比人工审查
  - 记录准确率

### 中优先级 (本月)

- [ ] **对比 Copilot vs Claude Skills**
  - 功能对比
  - 价格对比
  - 效果对比

- [ ] **集成到 OpenClaw**
  - 评估可行性
  - 设计集成方案
  - 实现原型

- [ ] **创建使用指南**
  - 8 个 Skills 详细教程
  - 最佳实践案例
  - 常见问题解答

### 低优先级 (季度)

- [ ] **建立 Skills 评估框架**
  - 质量指标
  - 效率指标
  - 用户满意度

- [ ] **收集更多 Skills**
  - 社区推荐
  - 官方发布
  - 自定义 Skills

- [ ] **团队培训计划**
  - 培训材料
  - 实践工作坊
  - 效果评估

---

## 📊 学习成果

### 知识点掌握

| 主题 | 掌握程度 | 下一步 |
|------|----------|--------|
| Claude Skills 概览 | ✅ 了解 | 实践应用 |
| Twitter API 获取 | ✅ 掌握 | 自动化集成 |
| MCP 生态关联 | ✅ 理解 | 深度研究 |
| 认知 - 运行分离 | ✅ 强化 | 架构设计 |

### 技能提升

- ✅ **信息获取:** Twitter CDN API 方法
- ✅ **知识整合:** 关联现有知识体系
- ✅ **实践规划:** 明确学习路径

### 产出文档

- ✅ `memory/Twitter-2026-03-04-sanbuphy.md` - 推文分析
- ✅ `MEMORY.md` - +[MCP-005] 核心观点
- ✅ `memory/learning-notes-2026-03-04.md` - 本学习笔记

---

## 🎯 下一步行动

**立即执行 (今天):**
1. 提交 Git 学习笔记
2. 更新 TODO 清单
3. 规划明日实践

**明日实践:**
1. 测试 Planning with Files
2. 研究 Skills API
3. 对比 MCP 工具

**本周目标:**
1. 完成 3 个 Skills 深度测试
2. 输出对比报告
3. 集成到工作流

---

*学习完成 · 2026-03-04 19:54 HKT*
