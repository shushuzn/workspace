# 知识卡片生成器 - GitHub Pages 部署指南

**部署时间:** 2026-03-12  
**目标:** 2 小时内上线

---

## 📦 部署步骤

### 1. 准备文件

**需要部署的文件:**
```
product-landing-pages/
├── index.html              # 主页面 (从 knowledge-card-landing-page.html 复制)
├── demo-video.mp4          # 演示视频 (可选)
└── README.md               # 本文件
```

### 2. 复制为 index.html

```bash
# 复制为主文件名
cp knowledge-card-landing-page.html index.html
```

### 3. 推送到 GitHub

**选项 A: 当前仓库 (obsidian-sync)**
- 路径：`/32-workflows-工作流/product-landing-pages/`
- GitHub Pages 源：选择该文件夹

**选项 B: 独立仓库 (推荐)**
- 创建新仓库：`knowledge-card-generator`
- 推送文件到 `main` 分支
- GitHub Pages 源：`main` 分支根目录

### 4. 启用 GitHub Pages

1. GitHub 仓库 → Settings → Pages
2. Source: 选择分支 (main)
3. Folder: 选择根目录或 `/docs`
4. 保存

**获得域名:** `https://your-username.github.io/repo-name/`

---

## 🎨 自定义

### 修改邮箱收集

**当前:** 前端 alert 演示  
**实际部署:** 连接后端 API

**方案 1: Formspree (免费)**
```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
    <input type="email" name="email" placeholder="输入邮箱">
    <button type="submit">申请内测</button>
</form>
```

**方案 2: Google Forms (免费)**
- 创建 Google Form
- 嵌入到页面

**方案 3: 自建后端**
- Railway 部署 Flask 后端
- 接收邮箱存储到数据库

---

## 📊 访问统计

**免费方案:**
- Google Analytics (免费)
- Cloudflare Web Analytics (免费)
- GitHub Pages 自带访问统计 (有限)

---

## ⏱️ 时间估算

| 任务 | 用时 |
|------|------|
| 复制文件 | 2 分钟 |
| 推送 GitHub | 5 分钟 |
| 启用 Pages | 3 分钟 |
| DNS 生效 | 5-10 分钟 |
| **总计** | **15-20 分钟** |

---

## ✅ 上线检查清单

- [ ] index.html 存在
- [ ] 页面能正常访问
- [ ] 表单能提交
- [ ] 移动端适配正常
- [ ] 加载速度<3 秒

---

*部署指南完成*
