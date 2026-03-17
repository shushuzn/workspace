# arXiv 收集器与 OpenClaw 集成指南

**目标:** 将 arXiv 收集的论文数据集成到 OpenClaw Research Agent

---

## 📊 数据格式

arXiv 收集器输出的 JSON 格式：

```json
{
  "keyword": "graph neural network molecular",
  "lastUpdated": "2026-03-13T14:15:39.414Z",
  "totalPapers": 50,
  "newPapers": 50,
  "papers": [
    {
      "id": "http://arxiv.org/abs/2603.12262v1",
      "title": "论文标题",
      "summary": "摘要",
      "authors": ["作者 1", "作者 2"],
      "categories": ["cs.LG", "cs.AI"],
      "published": "2026-03-12T17:59:51Z",
      "updated": "2026-03-12T17:59:51Z",
      "collectedAt": "2026-03-13T14:15:39.412Z"
    }
  ]
}
```

---

## 🔗 集成方式

### 方式 1: 直接读取 JSON 文件

```javascript
const fs = require('fs');
const path = require('path');

// 读取收集的论文
const papersPath = path.join(__dirname, '../41-arxiv-collector/data/papers');
const files = fs.readdirSync(papersPath);

files.forEach(file => {
    const data = JSON.parse(fs.readFileSync(path.join(papersPath, file), 'utf-8'));
    console.log(`关键词：${data.keyword}`);
    console.log(`论文数：${data.totalPapers}`);
    console.log(`新增：${data.newPapers}`);
});
```

### 方式 2: 作为 OpenClaw 数据源

在 OpenClaw 中添加 arXiv 数据源模块：

```javascript
// openclaw/sources/arxiv-source.js
class ArxivSource {
    constructor(collectorPath) {
        this.collectorPath = collectorPath;
    }
    
    async getLatestPapers(keyword, limit = 10) {
        const filePath = path.join(
            this.collectorPath,
            'data/papers',
            `${keyword.replace(/[^a-zA-Z0-9]/g, '_')}.json`
        );
        
        const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        return data.papers.slice(0, limit);
    }
    
    async searchPapers(query) {
        // 搜索所有收集的论文
        const papers = [];
        const files = fs.readdirSync(path.join(this.collectorPath, 'data/papers'));
        
        for (const file of files) {
            const data = JSON.parse(fs.readFileSync(
                path.join(this.collectorPath, 'data/papers', file),
                'utf-8'
            ));
            
            const matched = data.papers.filter(p =>
                p.title.toLowerCase().includes(query.toLowerCase()) ||
                p.summary.toLowerCase().includes(query.toLowerCase())
            );
            
            papers.push(...matched);
        }
        
        return papers;
    }
}

module.exports = { ArxivSource };
```

---

## 🔄 定时更新

### 使用 Windows 任务计划程序

1. 打开任务计划程序
2. 创建基本任务
3. 设置每天运行时间 (如 8:00 AM)
4. 操作：启动程序
   - 程序：`node.exe`
   - 参数：`arxiv-collector.js`
   - 起始于：`D:\OpenClaw\workspace\41-arxiv-collector`

### 使用 Node.js 定时任务

```javascript
// scheduler.js
const { exec } = require('child_process');
const cron = require('node-cron');

// 每天早上 8 点运行
cron.schedule('0 8 * * *', () => {
    console.log('📡 运行 arXiv 收集器...');
    exec('node arxiv-collector.js', {
        cwd: 'D:\\OpenClaw\\workspace\\41-arxiv-collector'
    }, (error, stdout, stderr) => {
        if (error) {
            console.error(`错误：${error.message}`);
            return;
        }
        console.log(stdout);
    });
});
```

---

## 📈 数据统计

### 查看收集统计

```bash
cd 41-arxiv-collector
node -e "
const fs = require('fs');
const files = fs.readdirSync('./data/papers');
let total = 0;
files.forEach(f => {
    const d = JSON.parse(fs.readFileSync('./data/papers/' + f));
    total += d.totalPapers;
    console.log(d.keyword + ': ' + d.totalPapers);
});
console.log('总计：' + total);
"
```

---

## 🎯 使用场景

### 1. 研究趋势分析
- 每日收集特定领域论文
- 分析研究热点变化
- 发现新兴方向

### 2. 论文推荐
- 基于用户兴趣关键词
- 推送最新相关论文
- 与 OpenClaw 分析集成

### 3. 文献综述辅助
- 自动收集相关文献
- 生成文献列表
- 支持批量分析

---

## 📊 当前收集统计

运行以下命令查看：

```bash
cd 41-arxiv-collector
node test-collector.js
```

---

*Created:* 2026-03-13  
*Version:* 1.0  
*Status:* ✅ 已完成
