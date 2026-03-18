# 知识卡片生成器 API 文档

**版本:** v2.5  
**最后更新:** 2026-03-11  
**基础 URL:** `http://127.0.0.1:5000/api/v1`

---

## 📋 目录

1. [概述](#概述)
2. [认证](#认证)
3. [端点](#端点)
4. [数据模型](#数据模型)
5. [错误码](#错误码)
6. [速率限制](#速率限制)
7. [示例代码](#示例代码)

---

## 概述

知识卡片生成器 API 提供从学术论文 PDF 自动生成结构化 HTML 知识卡片的功能。

**核心功能:**
- 元数据提取 (标题/作者/年份/arXiv ID)
- 章节解析 (自动识别 Introduction/Methods 等)
- 参考文献提取与验证
- HTML 卡片生成
- BibTeX 导出

---

## 认证

当前版本无需认证 (本地部署)。

未来版本可能支持 API Key 认证：
```http
Authorization: Bearer YOUR_API_KEY
```

---

## 端点

### 1. 健康检查

**GET** `/health`

检查 API 服务状态。

**响应示例:**
```json
{
  "status": "healthy",
  "version": "2.5",
  "timestamp": "2026-03-11T12:00:00Z"
}
```

---

### 2. 上传 PDF

**POST** `/upload`

上传单个 PDF 文件进行处理。

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | ✅ | PDF 文件 (最大 100MB) |
| `validate` | boolean | ❌ | 是否验证参考文献 (默认：true) |
| `export_bibtex` | boolean | ❌ | 是否导出 BibTeX (默认：true) |
| `concurrent` | boolean | ❌ | 是否启用并发验证 (默认：true) |
| `workers` | integer | ❌ | 并发线程数 (默认：5, 范围：1-20) |
| `render_latex` | boolean | ❌ | 是否渲染 LaTeX 公式 (默认：true) |

**响应示例:**
```json
{
  "task_id": "task_20260311_120000_001",
  "status": "processing",
  "message": "PDF 已接收，开始处理",
  "estimated_time": 30
}
```

---

### 3. 批量上传

**POST** `/upload/batch`

批量上传多个 PDF 文件。

**请求参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | file[] | ✅ | PDF 文件数组 (最大 50 个) |
| `validate` | boolean | ❌ | 是否验证参考文献 (默认：true) |
| `batch_report` | boolean | ❌ | 是否生成批量报告 (默认：true) |

**响应示例:**
```json
{
  "batch_id": "batch_20260311_120000",
  "status": "processing",
  "total_files": 10,
  "message": "批量任务已创建"
}
```

---

### 4. 查询任务状态

**GET** `/task/{task_id}`

查询任务处理进度。

**路径参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务 ID |

**响应示例:**
```json
{
  "task_id": "task_20260311_120000_001",
  "status": "processing",
  "progress": 65,
  "current_step": "validating_references",
  "steps_completed": [
    "metadata_extraction",
    "chapter_parsing",
    "reference_extraction"
  ],
  "estimated_remaining": 10
}
```

**状态说明:**
- `pending` - 等待处理
- `processing` - 处理中
- `completed` - 完成
- `failed` - 失败

---

### 5. 下载结果

**GET** `/result/{task_id}`

下载处理结果 (ZIP 压缩包)。

**路径参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务 ID |

**响应:**
- Content-Type: `application/zip`
- 文件名：`{task_id}_results.zip`

**ZIP 内容:**
```
task_20260311_120000_001_results.zip
├── paper.card.html      # HTML 知识卡片
├── paper.bib            # BibTeX 文件 (如启用)
├── validation_report.json  # 验证报告
└── metadata.json        # 元数据
```

---

### 6. 查询 API 配额

**GET** `/quota`

查询当前 API 配额使用情况。

**响应示例:**
```json
{
  "crossref": {
    "used": 45,
    "limit": 600,
    "remaining": 555,
    "reset_at": "2026-03-11T13:00:00Z"
  },
  "arxiv": {
    "used": 32,
    "limit": 600,
    "remaining": 568,
    "reset_at": "2026-03-11T13:00:00Z"
  }
}
```

---

### 7. 缓存管理

**GET** `/cache/stats`

查询缓存统计信息。

**响应示例:**
```json
{
  "total_entries": 1250,
  "hit_rate": 0.45,
  "size_mb": 15.6,
  "oldest_entry": "2026-03-10T08:00:00Z",
  "newest_entry": "2026-03-11T11:55:00Z"
}
```

**DELETE** `/cache/clear`

清理过期缓存。

**响应示例:**
```json
{
  "cleared_entries": 350,
  "freed_mb": 4.2,
  "message": "缓存清理完成"
}
```

---

## 数据模型

### Task

```json
{
  "task_id": "string",
  "status": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "progress": "number",
  "current_step": "string",
  "steps_completed": ["string"],
  "estimated_remaining": "number"
}
```

### ValidationResult

```json
{
  "doi": "string",
  "status": "verified|manual|failed",
  "journal": "string",
  "year": "number",
  "citations": "number",
  "verified_at": "ISO8601"
}
```

### Metadata

```json
{
  "title": "string",
  "authors": ["string"],
  "year": "number",
  "arxiv_id": "string",
  "doi": "string",
  "journal": "string",
  "pages": "number"
}
```

---

## 错误码

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `INVALID_FILE` | 文件格式无效 (非 PDF) |
| 400 | `FILE_TOO_LARGE` | 文件超过 100MB |
| 404 | `TASK_NOT_FOUND` | 任务 ID 不存在 |
| 429 | `RATE_LIMIT_EXCEEDED` | 超出 API 速率限制 |
| 500 | `PROCESSING_ERROR` | 处理过程中发生错误 |
| 503 | `SERVICE_UNAVAILABLE` | 服务暂时不可用 |

**错误响应示例:**
```json
{
  "error": {
    "code": "INVALID_FILE",
    "message": "上传的文件不是有效的 PDF 格式",
    "details": "请确保文件扩展名为 .pdf 且内容有效"
  }
}
```

---

## 速率限制

| API | 限制 | 重置周期 |
|-----|------|----------|
| CrossRef | 600 请求/小时 | 每小时整点 |
| arXiv | 600 请求/小时 | 每小时整点 |

**速率限制响应头:**
```http
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 555
X-RateLimit-Reset: 1710158400
```

---

## 示例代码

### Python 示例

```python
import requests

# 上传 PDF
files = {'file': open('paper.pdf', 'rb')}
data = {'validate': True, 'export_bibtex': True}
response = requests.post('http://127.0.0.1:5000/api/v1/upload', files=files, data=data)
task_id = response.json()['task_id']

# 查询状态
while True:
    response = requests.get(f'http://127.0.0.1:5000/api/v1/task/{task_id}')
    status = response.json()['status']
    if status == 'completed':
        break
    time.sleep(2)

# 下载结果
response = requests.get(f'http://127.0.0.1:5000/api/v1/result/{task_id}')
with open('results.zip', 'wb') as f:
    f.write(response.content)
```

### cURL 示例

```bash
# 上传 PDF
curl -X POST http://127.0.0.1:5000/api/v1/upload \
  -F "file=@paper.pdf" \
  -F "validate=true" \
  -F "export_bibtex=true"

# 查询状态
curl http://127.0.0.1:5000/api/v1/task/task_20260311_120000_001

# 下载结果
curl -O http://127.0.0.1:5000/api/v1/result/task_20260311_120000_001
```

### JavaScript 示例

```javascript
// 上传 PDF
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('validate', 'true');

const response = await fetch('http://127.0.0.1:5000/api/v1/upload', {
  method: 'POST',
  body: formData
});

const { task_id } = await response.json();

// 轮询状态
while (true) {
  const statusResponse = await fetch(`http://127.0.0.1:5000/api/v1/task/${task_id}`);
  const { status } = await statusResponse.json();
  if (status === 'completed') break;
  await new Promise(resolve => setTimeout(resolve, 2000));
}
```

---

## 📊 性能指标

| 指标 | 目标 | 实测 |
|------|------|------|
| 单篇处理时间 | <30 秒 | 待测试 |
| 内存使用 | <500MB | 待测试 |
| 并发速度提升 | ≥3x | 待测试 |
| API 配额效率 | ≥80% | 待测试 |
| 测试覆盖率 | ≥80% | 待测试 |

---

## 🔗 相关文档

- [README.md](../README.md) - 使用指南
- [FAQ.md](./FAQ.md) - 常见问题
- [LIMITATIONS.md](./LIMITATIONS.md) - 局限性说明

---

*最后更新：2026-03-11*
