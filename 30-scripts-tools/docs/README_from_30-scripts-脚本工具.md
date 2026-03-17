# OpenClaw 脚本工具集 - 完整文档索引

**版本:** 1.0.0  
**最后更新:** 2026-03-10  
**维护者:** OpenClaw Team

---

## 📁 目录结构

```
30-scripts/
├── daily-brief.py              # 每日简报生成器
├── pdf-extractor/
│   ├── simple_pdf_extractor.py # PDF 提取器 (双栏检测)
│   ├── marker_extractor.py     # PDF 提取器 (Marker)
│   └── layoutlm_extractor.py   # PDF 提取器 (LayoutLM)
├── figure-enhancer/
│   ├── quality_filter.py       # 图表质量过滤器
│   ├── super_resolution.py     # 超分辨率增强
│   └── figure_enhancer.py      # 图表增强主脚本
├── graph-optimizer/
│   └── graph_renderer.html     # 图谱 WebGL 渲染器
├── api-server/
│   ├── main.py                 # FastAPI 服务器
│   ├── Dockerfile              # Docker 镜像
│   └── docker-compose.yml      # Docker Compose
└── README.md                   # 本文档
```

---

## 🚀 快速开始

### 1. 每日简报生成

```bash
# 生成昨日简报
py 30-scripts/daily-brief.py

# 生成指定日期简报
py 30-scripts/daily-brief.py --date 2026-03-10

# 生成并发送到 Feishu
py 30-scripts/daily-brief.py --send

# 查看帮助
py 30-scripts/daily-brief.py --help
```

**输出位置:** `21-reports/daily-briefs/brief-YYYY-MM-DD.md`

**详细文档:** [每日简报使用指南](daily-brief/README.md)

---

### 2. PDF 提取

```bash
# 提取 PDF (自动检测双栏)
py 30-scripts/pdf-extractor/simple_pdf_extractor.py input.pdf -o output/

# 预览前 3 页
py 30-scripts/pdf-extractor/simple_pdf_extractor.py input.pdf --preview -m 3

# 使用 Marker 提取 (需要安装 marker-pdf)
py 30-scripts/pdf-extractor/marker_extractor.py input.pdf -o output/
```

**支持功能:**
- ✅ 双栏布局自动检测
- ✅ Markdown 输出
- ✅ 公式提取 (LaTeX)
- ✅ 表格提取

**详细文档:** [PDF 提取器使用指南](pdf-extractor/README.md)

---

### 3. 图表增强

```bash
# 质量评估
py 30-scripts/figure-enhancer/quality_filter.py image.png

# 批量评估
py 30-scripts/figure-enhancer/quality_filter.py --batch figures/ -o report.json

# 超分辨率增强 (4 倍放大)
py 30-scripts/figure-enhancer/figure_enhancer.py image.png -o enhanced.png

# 批量增强
py 30-scripts/figure-enhancer/figure_enhancer.py --batch figures/ --output-dir enhanced/
```

**支持功能:**
- ✅ 模糊度检测 (Laplacian 方差)
- ✅ 分辨率检测
- ✅ 对比度检测
- ✅ Real-ESRGAN 超分辨率 (4x)
- ✅ OpenCV 备用方案

**详细文档:** [图表增强器使用指南](figure-enhancer/README.md)

---

### 4. 图谱渲染

```bash
# 在浏览器中打开
start 30-scripts/graph-optimizer/graph_renderer.html

# 或启动 HTTP 服务器
py -m http.server 8000
# 访问 http://localhost:8000/30-scripts/graph-optimizer/graph_renderer.html
```

**支持功能:**
- ✅ 分页加载 (50/100/200/500 节点/页)
- ✅ 力导向布局 (D3.js)
- ✅ 圆形/层级布局
- ✅ 节点拖拽交互
- ✅ 缩放/平移
- ✅ 性能统计 (FPS/渲染时间)

**详细文档:** [图谱渲染器使用指南](graph-optimizer/README.md)

---

### 5. API 服务器

```bash
# 本地运行
cd 30-scripts/api-server
pip install -r requirements.txt
uvicorn main:app --reload

# Docker 运行
docker-compose up -d

# 访问 API 文档
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

**API 端点:**
- `GET /api/v1/health` - 健康检查
- `POST /api/v1/pdf/extract` - PDF 提取
- `POST /api/v1/figure/enhance` - 图表增强
- `POST /api/v1/brief/generate` - 每日简报

**详细文档:** [API 服务器使用指南](api-server/README.md)

---

## 📊 功能对比

| 功能 | 脚本 | API | Docker | 状态 |
|------|------|-----|--------|------|
| 每日简报 | ✅ | ✅ | ✅ | 完成 |
| PDF 提取 | ✅ | ✅ | ✅ | 完成 |
| 图表增强 | ✅ | ✅ | ✅ | 完成 |
| 图谱渲染 | ✅ | ⏸️ | ⏸️ | 完成 |
| 知识图谱 | ✅ | ⏸️ | ⏸️ | 完成 |

---

## 🔧 环境配置

### Python 版本
- **推荐:** Python 3.11+
- **最低:** Python 3.9

### 系统依赖
```bash
# Windows
# 无特殊要求

# Linux
sudo apt-get install -y poppler-utils libgl1-mesa-glx

# macOS
brew install poppler
```

### Python 依赖
```bash
# 核心依赖
pip install fastapi uvicorn pydantic PyMuPDF opencv-python numpy pillow requests

# 可选依赖 (图表增强)
pip install realesrgan basicsr facexlib gfpgan

# 可选依赖 (PDF 提取)
pip install marker-pdf
```

---

## 📝 使用场景

### 场景 1: 每日自动简报

```bash
# 配置定时任务 (Windows)
schtasks /create /tn "DailyBrief" /tr "py D:\OpenClaw\workspace\30-scripts\daily-brief.py --send" /sc daily /st 08:00 /d MON,TUE,WED,THU,FRI

# 或通过 API
curl -X POST http://localhost:8000/api/v1/brief/generate \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-10", "send": true}'
```

### 场景 2: 批量 PDF 处理

```bash
# 处理整个目录
for file in papers/*.pdf; do
  py 30-scripts/pdf-extractor/simple_pdf_extractor.py "$file" -o output/
done
```

### 场景 3: 图表质量筛选

```bash
# 评估所有图表
py 30-scripts/figure-enhancer/quality_filter.py --batch figures/ -o quality_report.json

# 只增强低质量图表
# (查看报告后手动处理)
```

### 场景 4: 大规模图谱可视化

```bash
# 打开浏览器
start 30-scripts/graph-optimizer/graph_renderer.html

# 加载 1000+ 节点
# 使用分页功能流畅浏览
```

---

## 🐛 故障排查

### 问题 1: PDF 提取失败

**症状:** `FileNotFoundError` 或乱码

**解决:**
1. 确认文件路径正确 (使用绝对路径)
2. 检查 PDF 是否加密
3. 尝试使用 Marker 提取器

### 问题 2: 图表增强慢

**症状:** 处理时间 >30 秒/图

**解决:**
1. 降低放大倍数 (`--scale 2`)
2. 使用 OpenCV 备用方案
3. 批量处理时减少并发数

### 问题 3: API 无法启动

**症状:** `Address already in use`

**解决:**
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 杀死进程
taskkill /PID <PID> /F

# 或更换端口
uvicorn main:app --port 8001
```

### 问题 4: Docker 构建失败

**症状:** `no matching manifest`

**解决:**
```bash
# 清理缓存
docker builder prune

# 重新构建
docker build --no-cache -t openclaw-api:latest .
```

---

## 📚 相关资源

- [OpenClaw 文档](https://docs.openclaw.ai)
- [GitHub 仓库](https://github.com/openclaw/openclaw)
- [社区 Discord](https://discord.com/invite/clawd)
- [技能市场](https://clawhub.com)

---

## 📝 更新日志

### v1.0.0 (2026-03-10)
- ✅ 每日简报功能完成
- ✅ PDF 提取器完成 (双栏检测)
- ✅ 图表增强器完成 (质量过滤 + 超分辨率)
- ✅ 图谱渲染器完成 (WebGL + 分页)
- ✅ API 服务器完成 (FastAPI + Docker)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

*最后更新：2026-03-10*
