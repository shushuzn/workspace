# OpenClaw 常见问题解答 (FAQ)

---

## 📌 安装配置

### Q: Python 版本要求？

**A:** 推荐 Python 3.11+，最低 3.9。

### Q: 如何安装依赖？

**A:** 
```bash
# 核心依赖
pip install -r 30-scripts/api-server/requirements.txt

# 或单独安装
pip install fastapi uvicorn PyMuPDF opencv-python
```

### Q: Docker 无法启动？

**A:** 
1. 检查 Docker Desktop 是否运行
2. 确认端口 8000 未被占用
3. 查看日志：`docker logs openclaw-api`

---

## 📌 每日简报

### Q: 为什么 arXiv 数量为 0？

**A:** 检查 `40-arxiv/papers/日期/` 目录是否有数据，可能需要先运行收集脚本。

### Q: Feishu 推送失败？

**A:** 
1. 检查 `feishu-queue.json` 是否有积压
2. 运行 `py process-feishu-queue.py` 手动处理
3. 确认 OpenClaw message 工具配置正确

### Q: 天气数据不可用？

**A:** wttr.in 可能被临时拦截，使用备用源 Open-Meteo 已自动切换。

---

## 📌 PDF 提取

### Q: 提取乱码？

**A:** 
1. 确认 PDF 未加密
2. 尝试 Marker 提取器
3. 检查文件编码

### Q: 双栏检测不准？

**A:** 调整 `simple_pdf_extractor.py` 中的中心线阈值。

### Q: 公式提取失败？

**A:** 使用 Marker 提取器，支持 LaTeX 公式。

---

## 📌 图表增强

### Q: Real-ESRGAN 安装失败？

**A:** 使用 OpenCV 备用方案，或参考官方文档安装 CUDA 版本。

### Q: 增强后质量仍差？

**A:** 原始图像质量过低，建议重新收集高质量图像。

### Q: 处理速度慢？

**A:** 
1. 降低放大倍数 (`--scale 2`)
2. 使用 GPU 加速
3. 批量处理时减少并发

---

## 📌 图谱渲染

### Q: 页面空白？

**A:** 检查浏览器控制台，确认 D3.js CDN 可访问。

### Q: 拖拽卡顿？

**A:** 减少每页节点数，或使用更强大的 GPU。

### Q: 如何加载自定义数据？

**A:** 修改 `loadFromJSON()` 函数，参考 graph_renderer.html 注释。

---

## 📌 API 服务器

### Q: 端口被占用？

**A:** 
```bash
# 查找占用进程
netstat -ano | findstr :8000
# 杀死进程
taskkill /PID <PID> /F
# 或更换端口
uvicorn main:app --port 8001
```

### Q: API 响应慢？

**A:** 
1. 检查服务器资源使用
2. 增加内存/CPU 限制
3. 启用 Redis 缓存

### Q: CORS 错误？

**A:** 修改 `main.py` 中的 `allow_origins` 配置。

---

## 📌 性能优化

### Q: 如何加速 PDF 提取？

**A:** 
1. 限制处理页数 (`-m 10`)
2. 使用简易提取器
3. 批量处理时并行执行

### Q: 如何优化大图渲染？

**A:** 
1. 启用分页加载
2. 使用 WebGL 渲染
3. 减少同时显示节点数

### Q: API 并发能力？

**A:** 
1. 使用 uvicorn workers (`-w 4`)
2. 启用 Redis 缓存
3. 配置负载均衡

---

## 📌 其他

### Q: 如何贡献代码？

**A:** 
1. Fork 仓库
2. 创建功能分支
3. 提交 PR

### Q: 如何报告 Bug？

**A:** GitHub Issues 提交，包含：
- 复现步骤
- 错误日志
- 环境信息

### Q: 许可证？

**A:** MIT License

---

*最后更新：2026-03-10*
