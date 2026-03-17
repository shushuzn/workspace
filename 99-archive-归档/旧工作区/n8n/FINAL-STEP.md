# n8n 工作流导入 - 最后一步

**时间:** 2026-03-04 22:40  
**状态:** n8n 运行中，浏览器已打开

---

## ⚠️ 浏览器自动化限制

由于浏览器安全限制，文件上传需要手动完成。

---

## 📥 手动导入步骤 (30 秒)

### 方法 1: 拖拽导入 (最简单)

1. **打开文件管理器**
   - `Win + E`
   - 导航到：`D:\OpenClaw\workspace\n8n\workflows\`

2. **打开 n8n**
   - 浏览器：http://localhost:5678/workflows

3. **拖拽文件**
   - 将 `openclaw-master-workflow.json` 拖到浏览器窗口

4. **激活**
   - 点击右上角 **Active** 开关

---

### 方法 2: 菜单导入

1. **按 Ctrl+K** 打开命令面板

2. **输入:** `import`

3. **选择:** `Import workflow from file`

4. **选择文件:** 
   - `D:\OpenClaw\workspace\n8n\workflows\openclaw-master-workflow.json`

5. **激活工作流**

---

## ✅ 验证

- [ ] 工作流名称：`OpenClaw 主工作流 - 统一调度中心`
- [ ] Active 开关：绿色
- [ ] 7 个触发器节点

---

## 🕐 下次执行

| 任务 | 时间 |
|------|------|
| Hourly Sync | 下一小时整点 |
| arXiv Collect | 明天 2:00 AM |
| Security Audit | 明天 3:00 AM |
| Medium Watcher | 明天 4:00 AM |

---

*完成导入后，所有任务将自动执行！* 🚀
