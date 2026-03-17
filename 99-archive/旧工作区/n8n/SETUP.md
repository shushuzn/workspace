# n8n 设置指南

**创建时间:** 2026-03-04 22:30  
**n8n 状态:** ✅ 已安装并运行  
**访问地址:** http://localhost:5678

---

## 🔐 首次设置 (需要手动完成)

### 1. 打开 n8n

在浏览器中打开：**http://localhost:5678**

---

### 2. 设置管理员账户

填写以下信息：

| 字段 | 建议值 |
|------|--------|
| **Email** | `admin@openclaw.local` |
| **First Name** | `OpenClaw` |
| **Last Name** | `Admin` |
| **Password** | `OpenClaw2026!` (或自定义) |
| **接收更新** | 可选勾选 |

点击 **Next** 继续。

---

### 3. 导入工作流

设置完成后：

1. 点击左侧菜单 **Workflows**
2. 点击右上角 **Add Workflow**
3. 点击右上角 **⋯** (更多选项)
4. 选择 **Import from File**
5. 选择文件：`D:\OpenClaw\workspace\n8n\workflows\openclaw-master-workflow.json`
6. 点击 **Import**

---

### 4. 激活工作流

1. 导入后点击工作流右上角的 **Active** 开关
2. 确认激活

---

## 📋 已配置的工作流

### OpenClaw 主工作流

**触发器:**
| 时间 | 任务 |
|------|------|
| 每小时 | Obsidian 同步 |
| 每日 2:00 AM | arXiv 收集 |
| 每日 3:00 AM | 安全审计 |
| 每日 4:00 AM | Medium 收集 |
| 每日 9:00 AM | 早晨同步 |
| 每周日 5:00 AM | 知识蒸馏 |
| 每周一 10:00 AM | 周报生成 |

---

## 🔧 可选配置

### 修改时区

n8n 默认使用 UTC 时间。如需使用香港时间 (Asia/Hong_Kong):

1. 点击右上角用户头像
2. 选择 **Settings**
3. 修改 **Timezone** 为 `Asia/Hong_Kong`

---

### 配置通知 (可选)

如需邮件/Slack 通知：

1. 点击左侧 **Credentials**
2. 添加相应凭据
3. 在工作流中添加通知节点

---

## 📊 监控

### 查看执行历史

1. 点击左侧 **Executions**
2. 查看所有工作流执行记录
3. 筛选成功/失败执行

---

### 查看工作流状态

1. 点击左侧 **Workflows**
2. 查看 **Active** 列状态
3. 绿色 = 已激活

---

## 🛡️ 安全建议

1. **修改默认密码** - 首次登录后修改
2. **不要暴露公网** - 除非必要
3. **使用 HTTPS** - 生产环境
4. **定期备份** - 工作流和凭据

---

## 📚 相关文件

- **工作流文件:** `workflows/openclaw-master-workflow.json`
- **使用文档:** `README.md`
- **HEARTBEAT.md:** 定时任务清单

---

## ✅ 检查清单

- [ ] 打开 http://localhost:5678
- [ ] 设置管理员账户
- [ ] 导入 openclaw-master-workflow.json
- [ ] 激活工作流
- [ ] 修改时区为 Asia/Hong_Kong
- [ ] 验证第一个触发器执行

---

*n8n 已就绪！完成上述设置后，自动化调度将开始运行！* 🚀
