# 可视化仪表板

**版本:** v1.0  
**创建时间:** 2026-03-05 17:40  
**用途:** 系统监控与数据可视化

---

## 📋 仪表板说明

### 功能
- 系统状态监控
- 工作流状态展示
- 质量指标展示
- 性能指标展示
- 告警信息显示

### 访问方式

**本地访问:**
```
http://localhost/dashboard/
```

**远程访问:**
```
http://<server-ip>/dashboard/
```

---

## 📊 仪表板内容

### 系统概览
- 总工作流数
- 运行中工作流
- 成功率
- 今日处理论文数

### 工作流状态
- Level 0: 质量控制
- Level 1: 论文收集
- Level 2: 分类标注
- Level 3: 趋势分析
- Level 4: 主题聚类
- Level 5: 报告生成
- Level 6: 知识图谱

### 质量指标
- 数据验证通过率
- 质量评分
- 异常检测率
- 分类准确率

### 性能指标
- 平均处理时间
- 各层耗时
- 系统可用性

---

## 🚀 使用方法

### 启动 Web 服务器

```bash
cd D:\OpenClaw\workspace\dashboard
python -m http.server 8080
```

### 访问仪表板

```
http://localhost:8080/
```

---

## 🔌 API 集成

### 从 API 获取数据

```javascript
// 获取质量指标
fetch('/api/v1/metrics')
  .then(response => response.json())
  .then(data => {
    // 更新仪表板
    updateDashboard(data);
  });

// 获取告警
fetch('/api/v1/alerts')
  .then(response => response.json())
  .then(data => {
    // 显示告警
    showAlerts(data);
  });
```

---

## 🎨 自定义

### 修改样式

编辑 `dashboard/index.html` 中的 CSS 部分

### 添加新指标

在 HTML 中添加新的 metric div:

```html
<div class="metric">
    <span>新指标名称</span>
    <span class="metric-value">数值</span>
</div>
```

---

*最后更新：2026-03-05 17:40*
