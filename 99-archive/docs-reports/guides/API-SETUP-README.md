# 🔐 API 密钥配置指南

**位置:** `D:\OpenClaw\workspace\.env`  
**模板:** `.env.example`  
**状态:** ✅ 已创建 (2026-03-13)

---

## 📋 快速开始

### 1. 复制模板
```bash
cd D:\OpenClaw\workspace
copy .env.example .env
```

### 2. 填写密钥
编辑 `.env` 文件，替换 `your_xxx_here` 为真实密钥。

### 3. 验证配置
```bash
python 30-scripts-脚本工具\10-DOMAIN-RANKING\core\domain_data_collector.py --test
```

---

## 🔑 必需 API 密钥 (P0 优先级)

以下 API 是学科学术段位系统 v3.0 自动化数据收集的核心：

| API | 用途 | 获取链接 | 必需 |
|-----|------|----------|------|
| `SEMANTIC_SCHOLAR_API_KEY` | 论文引用/理论基础 | [申请](https://www.semanticscholar.org/product/api) | ✅ P0 |
| `GITHUB_TOKEN` | 开源贡献统计 | [申请](https://github.com/settings/tokens) | ✅ P0 |
| `OPENAI_API_KEY` | LLM 分析/创新能力 | [申请](https://platform.openai.com/api-keys) | ✅ P0 |
| `FEISHU_WEBHOOK_URL` | 每日简报推送 | [飞书机器人](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN) | ✅ P0 |

---

## 📊 推荐 API 密钥 (P1 优先级)

| API | 用途 | 获取链接 |
|-----|------|----------|
| `OPENALEX_API_BASE_URL` | 学术数据综合 (免费) | [OpenAlex](https://openalex.org/) |
| `GOOGLE_CLOUD_API_KEY` | 专利统计 | [Google Cloud](https://cloud.google.com/patents) |
| `HUGGINGFACE_TOKEN` | 模型/数据集统计 | [Hugging Face](https://huggingface.co/settings/tokens) |
| `ORCID_CLIENT_ID` | 研究者信息 | [ORCID](https://orcid.org/developer-tools) |

---

## 🗺️ 可选 API 密钥 (P2 优先级)

| API | 用途 |
|-----|------|
| `SERPAPI_KEY` | Google Scholar 数据 |
| `CRUNCHBASE_API_KEY` | 公司/产业数据 |
| `COURSERA_API_KEY` | 课程统计 |
| `DIMENSIONS_API_KEY` | 商业学术数据 |
| `TWITTER_BEARER_TOKEN` | 领域动态追踪 |

---

## 🔒 安全最佳实践

### ✅ 应该做的
- 将 `.env` 加入 `.gitignore` (已完成)
- 使用环境变量加载密钥
- 定期轮换密钥
- 限制 API 密钥权限范围

### ❌ 不应该做的
- 不要将 `.env` 提交到 Git
- 不要在代码中硬编码密钥
- 不要分享密钥截图
- 不要使用个人主账号密钥 (创建专用账号)

---

## 📝 Python 加载示例

```python
from pathlib import Path
from dotenv import load_dotenv
import os

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 使用 API 密钥
semantic_api_key = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
github_token = os.getenv('GITHUB_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')

# 验证
if not semantic_api_key:
    raise ValueError("⚠️ SEMANTIC_SCHOLAR_API_KEY 未配置")
```

---

## 🧪 测试配置

```bash
# 安装依赖
pip install python-dotenv

# 测试加载
python -c "from dotenv import load_dotenv; load_dotenv('.env'); import os; print('✅' if os.getenv('GITHUB_TOKEN') else '❌')"
```

---

## 📁 文件清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `.env` | 真实密钥配置 | ✅ 已创建 |
| `.env.example` | 模板 (可安全分享) | ✅ 已创建 |
| `.gitignore` | 已配置忽略 .env | ✅ 已更新 |
| `API-SETUP-README.md` | 本文档 | ✅ 已创建 |

---

## 🆘 常见问题

### Q: API 密钥申请被拒？
A: 检查邮箱验证、填写使用场景、使用机构邮箱。

### Q: API 限流怎么办？
A: 实现缓存机制、多数据源冗余、降低请求频率。

### Q: 密钥泄露了？
A: 立即在对应平台撤销密钥，重新生成。

---

*最后更新：2026-03-13 | 版本 v1.0*
