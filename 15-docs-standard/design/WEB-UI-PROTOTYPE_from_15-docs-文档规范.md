# AI Research OS - Web 界面原型

**版本:** v0.1 (原型)  
**创建时间:** 2026-03-05 12:52  
**技术栈:** HTML + 简单 JS (无需服务器)

---

## 📄 单文件 Web 界面

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Research OS - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { color: #666; font-size: 14px; margin-bottom: 10px; }
        .card .value { font-size: 32px; font-weight: bold; color: #333; }
        .card .desc { color: #999; font-size: 12px; margin-top: 5px; }
        .status { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-top: 10px; }
        .status.good { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #0056b3; }
        .btn-secondary { background: #6c757d; }
        .btn-success { background: #28a745; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Research OS - Dashboard</h1>
        
        <!-- 关键指标 -->
        <div class="grid">
            <div class="card">
                <h2>📊 今日论文</h2>
                <div class="value" id="paper-count">322</div>
                <div class="desc">2026-03-05 收集</div>
                <span class="status good">✅ 正常</span>
            </div>
            <div class="card">
                <h2>🧠 知识观点</h2>
                <div class="value">185+</div>
                <div class="desc">MEMORY.md</div>
                <span class="status good">✅ 正常</span>
            </div>
            <div class="card">
                <h2>📁 交付文档</h2>
                <div class="value">30</div>
                <div class="desc">脚本 + 文档</div>
                <span class="status good">✅ 正常</span>
            </div>
            <div class="card">
                <h2>⚙️ 系统状态</h2>
                <div class="value">🟢</div>
                <div class="desc">稳定运行</div>
                <span class="status good">✅ 100%</span>
            </div>
        </div>

        <!-- 快捷操作 -->
        <div class="card" style="margin-bottom: 20px;">
            <h2>⚡ 快捷操作</h2>
            <div class="actions" style="margin-top: 15px;">
                <button class="btn" onclick="alert('运行 arXiv 收集...')">📥 收集 arXiv</button>
                <button class="btn" onclick="alert('运行系统监控...')">🔍 系统监控</button>
                <button class="btn btn-success" onclick="alert('生成今日报告...')">📊 生成报告</button>
                <button class="btn btn-secondary" onclick="alert('查看 FAQ...')">❓ 帮助</button>
            </div>
        </div>

        <!-- 最近文件 -->
        <div class="card">
            <h2>📄 最近文件</h2>
            <table>
                <thead>
                    <tr><th>文件</th><th>类型</th><th>时间</th></tr>
                </thead>
                <tbody>
                    <tr><td>2026-03-05-summary.md</td><td>arXiv 摘要</td><td>01:29</td></tr>
                    <tr><td>monitor-report-2026-03-05.md</td><td>系统监控</td><td>12:27</td></tr>
                    <tr><td>daily-report-2026-03-05.md</td><td>每日报告</td><td>03:17</td></tr>
                    <tr><td>data-quality-2026-03-05.md</td><td>质量检查</td><td>12:27</td></tr>
                </tbody>
            </table>
        </div>

        <div style="margin-top: 20px; text-align: center; color: #999; font-size: 12px;">
            AI Research OS v1.0 | 最后更新：2026-03-05 12:52
        </div>
    </div>

    <script>
        // 简单交互
        console.log('AI Research OS Dashboard Loaded');
        // 实际部署时可添加 API 调用刷新数据
    </script>
</body>
</html>
```

---

## 🚀 使用方式

1. **保存文件:** `D:\OpenClaw\workspace\web\dashboard.html`
2. **双击打开:** 在浏览器中查看
3. **功能:** 查看关键指标，快捷操作按钮

---

## 🔧 未来扩展

- [ ] 连接本地 API 获取实时数据
- [ ] 添加图表可视化
- [ ] 任务执行进度条
- [ ] 历史数据对比

---

*最后更新：2026-03-05 12:52*
