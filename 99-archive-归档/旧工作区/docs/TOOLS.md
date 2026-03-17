# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

---

## 环境配置

### 工作区
- **主工作区:** `D:\OpenClaw\workspace`
- **Obsidian Vault:** `D:\obsidian\Vault`
- **OpenClaw 配置:** `C:\Users\华为\.openclaw` (部分已迁移到 D 盘)

### Docker 容器 (EverMemOS)
| 容器名 | 服务 | 端口 | 状态 |
|--------|------|------|------|
| memsys-mongodb | MongoDB | 27017 | ✅ healthy |
| memsys-redis | Redis | 6379 | ✅ healthy |
| memsys-elasticsearch | Elasticsearch | 19200/19300 | ✅ healthy |
| memsys-milvus-standalone | Milvus | 19530/9091 | ✅ healthy |
| memsys-milvus-minio | MinIO | 9000/9001 | ✅ healthy |
| memsys-milvus-etcd | etcd | 2379/2380 | ⚠️ unhealthy |
| evermemos-app | EverMemOS | 1995 | ✅ 运行中 |

**Docker 网络:** `memsys-network` (172.19.0.x)

### n8n 工作流
- **服务器:** http://localhost:5678
- **版本:** v2.10.3
- **工作流:** 6 个已激活
- **AI 优化:** -80% 调用

### MCP 服务器配置
| 服务器 | 模式 | 端口 | 状态 |
|--------|------|------|------|
| filesystem | HTTP | 8080 | ⏳ 待测试 |
| github | stdio | - | ⏳ 待 API Key |
| notion | stdio | - | ⏳ 待 API Key |
| tavily | stdio | - | ⏳ 待 API Key |
| fetch | stdio | - | ✅ 可用 |

**配置文件:** `mcp-config.json`, `.openclaw/mcporter-config.yaml`

### Git 仓库
- **obsidian-sync:** 自动同步 (每 2 小时)
- **工作区:** `D:\OpenClaw\workspace`

---

## 技能配置

### 已安装核心技能
- ai-research-os (论文解析)
- arxiv-daily (每日收集)
- batch-processor (批量解析)
- knowledge-graph-builder (图谱构建)
- memory-distiller (知识蒸馏)
- medium-watcher (Medium 文章)
- github-sync (Git 同步)
- notion (Notion 集成)
- ddg-web-search (网页搜索)
- pdf-extractor (PDF 提取)

### 定时任务 (n8n)
| 频率 | 任务 | AI 调用 |
|------|------|--------|
| 每 30 分钟 | 数据预处理 | ❌ |
| 每小时 | Obsidian 同步 | ❌ |
| 每 2 小时 | Git 自动提交 | ❌ |
| 每日 0AM | 日志轮转 | ❌ |
| 每日 2AM | arXiv 收集 | ✅ |
| 每日 3AM | 安全审计 | ❌ |
| 每日 4AM | Medium 收集 | ✅ |
| 每日 5AM | 文件归档 | ❌ |
| 每周日 5AM | 知识蒸馏 | ✅ |
| 每周一 10AM | 周报生成 | ✅ |

---

## 偏好设置

- **语言:** 中文
- **报告风格:** 简洁直接
- **TTS:** 未配置
- **浏览器:** Chrome (OpenClaw Browser Relay)

---

*Last updated: 2026-03-05 01:00*
