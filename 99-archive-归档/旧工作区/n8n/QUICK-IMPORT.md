# n8n 工作流快速导入指南

**创建时间:** 2026-03-04 22:35  
**n8n 状态:** ✅ 运行中  
**访问地址:** http://localhost:5678

---

## 📥 方法 1: 拖拽导入 (最简单)

### 步骤:

1. **打开文件管理器**
   - 打开 `D:\OpenClaw\workspace\n8n\workflows\`

2. **打开 n8n**
   - 浏览器访问：http://localhost:5678/workflows

3. **拖拽文件**
   - 将 `openclaw-master-workflow.json` 拖到 n8n 页面

4. **激活工作流**
   - 点击右上角 **Active** 开关

---

## 📥 方法 2: 菜单导入

### 步骤:

1. **打开 n8n Workflows 页面**
   - http://localhost:5678/workflows

2. **点击 "Add new item"**
   - 左上角按钮

3. **选择 "Workflow"**

4. **点击右上角 ⋯ (更多)**

5. **选择 "Import from File"**

6. **选择文件**
   - `D:\OpenClaw\workspace\n8n\workflows\openclaw-master-workflow.json`

7. **点击 Import**

8. **激活工作流**
   - 点击右上角 **Active** 开关

---

## ✅ 验证导入成功

### 检查工作流:

1. **查看工作流列表**
   - 应该看到 "OpenClaw 主工作流 - 统一调度中心"

2. **检查 Active 状态**
   - 绿色开关 = 已激活

3. **查看触发器**
   - 应该有 7 个触发器 (每小时/每日/每周)

---

## 🕐 下一个触发时间

| 任务 | 下次执行 |
|------|----------|
| Hourly Sync | 下一小时整点 |
| arXiv Collect | 明天 2:00 AM |
| Security Audit | 明天 3:00 AM |
| Medium Watcher | 明天 4:00 AM |
| Morning Sync | 明天 9:00 AM |
| Memory Distiller | 周日 5:00 AM |
| Weekly Report | 周一 10:00 AM |

---

## 🔍 监控执行

### 查看执行历史:

1. 点击左侧 **Executions**
2. 查看工作流执行记录
3. 筛选成功/失败

### 查看日志:

1. 点击工作流进入编辑模式
2. 点击右上角 **Executions** 标签
3. 查看每次执行详情

---

## ⚠️ 常见问题

### Q: 工作流不执行？

**检查:**
- Active 开关是否打开 (绿色)
- 系统时间是否正确
- n8n 服务是否运行

### Q: 执行失败？

**检查:**
- 脚本路径是否正确
- Python/PowerShell 是否可用
- 查看执行日志错误信息

### Q: 时间不对？

**解决:**
1. 点击右上角用户头像
2. 选择 **Settings**
3. 修改 **Timezone** 为 `Asia/Hong_Kong`

---

## 📚 相关文件

- **工作流文件:** `workflows/openclaw-master-workflow.json`
- **设置指南:** `SETUP.md`
- **使用文档:** `README.md`

---

*导入完成后，自动化调度将按时执行！* 🚀
