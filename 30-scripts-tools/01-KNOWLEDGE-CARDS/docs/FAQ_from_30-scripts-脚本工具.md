# 知识卡片生成器 - 常见问题解答 (FAQ)

**版本:** v2.5  
**最后更新:** 2026-03-11

---

## 📋 目录

1. [安装与配置](#安装与配置)
2. [基本使用](#基本使用)
3. [参考文献验证](#参考文献验证)
4. [性能优化](#性能优化)
5. [错误排查](#错误排查)
6. [Web UI](#web-ui)
7. [API 使用](#api-使用)
8. [高级功能](#高级功能)

---

## 安装与配置

### Q1: 需要安装哪些依赖？

**A:** 运行以下命令安装所有依赖：

```bash
pip install -r requirements.txt
```

**核心依赖:**
- `PyMuPDF` - PDF 解析
- `requests` - API 调用
- `Flask` - Web UI (可选)
- `tqdm` - 进度条
- `Pillow` - 图像处理
- `opencv-python` - 图像质量过滤
- `real-esrgan` - 超分辨率 (可选)

---

### Q2: API 密钥如何配置？

**A:** CrossRef 和 arXiv API 无需密钥，但有速率限制：

- **CrossRef:** 600 请求/小时
- **arXiv:** 600 请求/小时

如需更高配额，请注册 CrossRef API 密钥：
https://www.crossref.org/documentation/metadata-plus/metadata-plus-keys/

---

### Q3: 如何配置缓存？

**A:** 缓存配置在 `.cache_config.json` 文件中：

```json
{
  "max_entries": 1000,
  "ttl_hours": 24,
  "cache_dir": "./cache"
}
```

---

## 基本使用

### Q4: 如何处理单个 PDF？

**A:** 使用命令行：

```bash
py 30-scripts/knowledge-card-generator.py paper.pdf --validate -o output/
```

**输出:**
- `paper.card.html` - HTML 知识卡片
- `paper.bib` - BibTeX 文件
- `validation_report.json` - 验证报告

---

### Q5: 如何批量处理多个 PDF？

**A:** 使用批量模式：

```bash
py 30-scripts/knowledge-card-generator.py --batch papers/ --validate -o cards/
```

**输出:**
- 每个 PDF 对应的 HTML 卡片
- `batch-report.html` - 批量汇总报告
- `batch-stats.json` - 统计数据

---

### Q6: 如何禁用参考文献验证？

**A:** 添加 `--no-validate` 参数：

```bash
py 30-scripts/knowledge-card-generator.py paper.pdf --no-validate
```

---

## 参考文献验证

### Q7: 验证成功率是多少？

**A:** 典型验证成功率：

- **DOI 文献:** 70-80% (CrossRef)
- **arXiv 预印本:** 85-95% (arXiv API)
- **无 DOI/arXiv:** 需人工核实

---

### Q8: 验证失败的原因有哪些？

**A:** 常见失败原因：

1. **DOI 错误** - DOI 格式不正确或不存在
2. **API 限制** - 超出速率限制
3. **网络问题** - 连接超时
4. **文献太新** - 尚未被数据库收录
5. **非标准引用** - 引用格式不规范

**解决方案:**
- 手动核实文献信息
- 等待 API 配额重置
- 检查网络连接
- 使用 Google Scholar 手动搜索

---

### Q9: 如何查看验证缓存？

**A:** 使用缓存查看命令：

```bash
py 30-scripts/knowledge-card-generator.py --view-cache
```

**输出示例:**
```
缓存统计:
  总条目数：1250
  命中率：45%
  大小：15.6 MB
  最早条目：2026-03-10 08:00
  最新条目：2026-03-11 11:55
```

---

### Q10: 如何清理缓存？

**A:** 使用缓存清理命令：

```bash
py 30-scripts/knowledge-card-generator.py --cleanup-cache
```

**输出示例:**
```
清理完成:
  删除条目：350
  释放空间：4.2 MB
```

---

## 性能优化

### Q11: 如何提高处理速度？

**A:** 优化建议：

1. **启用并发验证** (默认开启)：
   ```bash
   py knowledge-card-generator.py paper.pdf --validate --workers 10
   ```

2. **使用缓存** (默认开启)：
   - 重复验证时速度提升 50%

3. **禁用不必要的功能**：
   ```bash
   py knowledge-card-generator.py paper.pdf --no-bibtex --no-latex
   ```

4. **限制处理页数**：
   ```bash
   py knowledge-card-generator.py paper.pdf --max-pages 10
   ```

---

### Q12: 内存使用过高怎么办？

**A:** 优化建议：

1. **限制并发线程数**：
   ```bash
   py knowledge-card-generator.py paper.pdf --workers 2
   ```

2. **分批处理大文件**：
   ```bash
   py knowledge-card-generator.py paper.pdf --max-pages 20
   ```

3. **关闭图像处理** (如果不需要)：
   ```bash
   py knowledge-card-generator.py paper.pdf --no-figures
   ```

---

### Q13: 并发线程数设置多少合适？

**A:** 推荐配置：

| 场景 | 线程数 | 说明 |
|------|--------|------|
| 轻量使用 | 2-3 | 低内存占用 |
| 默认配置 | 5 | 平衡速度与资源 |
| 高性能 | 10-15 | 快速处理批量任务 |
| 极限 | 20 | 最大并发 (不推荐) |

---

## 错误排查

### Q14: 遇到 "PDF parsing error" 怎么办？

**A:** 可能原因：

1. **文件损坏** - 重新下载 PDF
2. **加密 PDF** - 需要解密
3. **非标准 PDF** - 不支持的格式

**解决方案:**
```bash
# 检查 PDF 完整性
py 30-scripts/pdf/check_layout.py paper.pdf

# 尝试简单提取器
py 30-scripts/pdf/simple_pdf_extractor.py paper.pdf
```

---

### Q15: 遇到 "API rate limit exceeded" 怎么办？

**A:** 等待配额重置：

- **CrossRef:** 每小时整点重置
- **arXiv:** 每小时整点重置

**临时解决方案:**
```bash
# 使用缓存模式 (不发起新请求)
py knowledge-card-generator.py paper.pdf --cache-only
```

---

### Q16: 遇到 "LaTeX rendering failed" 怎么办？

**A:** 可能原因：

1. **MathJax CDN 不可达** - 检查网络连接
2. **LaTeX 语法错误** - 手动检查公式
3. **浏览器不支持** - 更新浏览器

**解决方案:**
- 禁用公式渲染：`--no-latex`
- 使用本地 MathJax: 下载并部署到本地

---

## Web UI

### Q17: 如何启动 Web UI？

**A:** 运行命令：

```bash
py 30-scripts/knowledge-card-webui.py --port 5000
```

**访问:** http://127.0.0.1:5000

---

### Q18: Web UI 支持哪些功能？

**A:** Web UI 功能：

- ✅ 拖拽上传 PDF (支持批量)
- ✅ 处理选项配置 (验证/BibTeX/并发/公式)
- ✅ 实时进度显示
- ✅ API 配额监控
- ✅ 结果下载 (ZIP 压缩包)

---

### Q19: Web UI 卡住不动怎么办？

**A:** 排查步骤：

1. **检查后端日志** - 查看错误信息
2. **刷新页面** - 重新连接 WebSocket
3. **重启服务** - 关闭后重新启动
4. **检查浏览器控制台** - 查看 JavaScript 错误

---

## API 使用

### Q20: 如何调用 REST API？

**A:** API 端点：

```bash
# 健康检查
curl http://127.0.0.1:5000/api/v1/health

# 上传 PDF
curl -X POST http://127.0.0.1:5000/api/v1/upload \
  -F "file=@paper.pdf" \
  -F "validate=true"

# 查询状态
curl http://127.0.0.1:5000/api/v1/task/task_20260311_120000_001

# 下载结果
curl -O http://127.0.0.1:5000/api/v1/result/task_20260311_120000_001
```

详见 [API.md](./API.md)

---

### Q21: API 有速率限制吗？

**A:** 有，限制如下：

| API | 限制 | 重置周期 |
|-----|------|----------|
| CrossRef | 600 请求/小时 | 每小时整点 |
| arXiv | 600 请求/小时 | 每小时整点 |

**查询配额:**
```bash
curl http://127.0.0.1:5000/api/v1/quota
```

---

## 高级功能

### Q22: 如何导出缓存备份？

**A:** 使用导出命令：

```bash
py knowledge-card-generator.py --export-cache backup.json
```

**导入备份:**
```bash
py knowledge-card-generator.py --import-cache backup.json
```

---

### Q23: 如何生成批量汇总报告？

**A:** 使用批量处理模式：

```bash
py knowledge-card-generator.py --batch papers/ --validate --batch-report -o cards/
```

**报告内容:**
- 处理概览 (总数/成功/失败/成功率)
- 验证统计 (已验证/需人工/失败/缓存命中)
- 可视化饼图 (验证分布)
- 处理详情表 (每篇论文的状态)

---

### Q24: 支持哪些 PDF 格式？

**A:** 支持的格式：

- ✅ 单栏 PDF (标准学术论文)
- ✅ 双栏 PDF (会议论文)
- ✅ 多栏/混合布局
- ✅ 含表格 PDF
- ✅ 含公式 PDF (LaTeX)
- ✅ 含图表 PDF

**不支持的格式:**
- ❌ 加密 PDF (需先解密)
- ❌ 扫描版 PDF (OCR 不支持)
- ❌ 损坏的 PDF

详见 [LIMITATIONS.md](./LIMITATIONS.md)

---

### Q25: 如何自定义 HTML 模板？

**A:** 修改模板文件：

```
30-scripts/01-KNOWLEDGE-CARDS/templates/card_template.html
```

**可自定义:**
- CSS 样式
- 布局结构
- 颜色主题
- 字体设置

---

## 📞 其他问题

如遇到未列出的问题，请：

1. 查看 [README.md](../README.md) - 完整使用指南
2. 查看 [API.md](./API.md) - API 详细文档
3. 查看 [LIMITATIONS.md](./LIMITATIONS.md) - 局限性说明
4. 查看 GitHub Issues - 已知问题和解决方案
5. 联系开发者 - 提交 Issue 或 Pull Request

---

*最后更新：2026-03-11*
