# 🌐 浏览器自动化配置

**创建日期:** 2026-03-27

---

## 可用操作

| 操作 | 用途 |
|------|------|
| `start` | 启动浏览器 |
| `open` | 打开 URL |
| `navigate` | 导航到页面 |
| `snapshot` | 获取页面元素快照 |
| `screenshot` | 截图 |
| `click` | 点击元素 |
| `type` | 输入文本 |
| `evaluate` | 执行 JavaScript |
| `wait_for` | 等待条件 |
| `tabs` | 管理标签页 |
| `cookies_*` | 管理 Cookies |

---

## 快捷任务模板

### 任务 1: 抓取网页内容

```javascript
// 1. 打开页面
open(url)

// 2. 等待加载
wait_for("body", 3000)

// 3. 截图保存
screenshot(path, full_page=true)

// 4. 提取内容
evaluate(() => document.body.innerText)
```

### 任务 2: 自动填表

```javascript
// 1. 打开页面
open("https://example.com/form")

// 2. 填表单
fill_form({
  "username": "user@example.com",
  "password": "password123"
})

// 3. 点击提交
click("button[type='submit']")
```

### 任务 3: 监控页面变化

```javascript
// 1. 打开页面
open(url)

// 2. 截图
screenshot(path)

// 3. 等待变化
wait_for("更新内容", 60000)

// 4. 再截图
screenshot(path + "_updated")
```

---

## 常用网站模板

### Hacker News

```javascript
open("https://news.ycombinator.com/")
snapshot()
```

### GitHub PR

```javascript
open("https://github.com/user/repo/pull/123")
snapshot()
```

### RSS 阅读

```javascript
open("https://feeds.example.com/feed.xml")
```

---

## 有头模式 vs 无头模式

| 模式 | 用途 | 触发 |
|------|------|------|
| **无头 (默认)** | 后台操作、截图、内容抓取 | `browser_use` 默认 |
| **有头** | 需要可视化操作、调试 | `headed=True` |

```javascript
// 启动可见浏览器
browser_use(action="start", headed=True)

// 然后正常操作
open(url)
snapshot()
```

---

## 错误处理

| 错误 | 解决 |
|------|------|
| `Page not found` | 使用 `open` 而非 `navigate` |
| `Element not found` | 增加 `wait_for` 等待加载 |
| `Timeout` | 增加等待时间或检查网络 |
| `Selector invalid` | 用 `snapshot` 重新获取元素 |

---

## 常用快捷命令

| 命令 | 执行 |
|------|------|
| `截图 <url>` | 打开页面并截图 |
| `抓取内容 <url>` | 获取页面文本内容 |
| `打开 <url>` | 在浏览器中打开 |
| `填表 <url>` | 打开并准备填表 |

---

## 浏览器状态

| 项目 | 状态 |
|------|------|
| 无头模式 | ✅ 可用 |
| 有头模式 | ✅ 可用 |
| 多标签页 | ✅ 支持 |
| Cookie 管理 | ✅ 支持 |
