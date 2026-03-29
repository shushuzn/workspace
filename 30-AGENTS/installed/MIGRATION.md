# 📦 迁移指南

**创建日期:** 2026-03-27

---

## 版本迁移

### v1.0 → v2.0

#### 配置文件变更

| 旧配置 | 新配置 |
|--------|--------|
| `agent.json` | `agent.json` (结构不变) |
| `.openclaw/config.json` | `.openclaw/config.json` |
| `SOUL.md` | `PROFILE.md` |

#### 数据迁移

```bash
# 1. 备份当前配置
backup.bat core

# 2. 导出数据
cp -r memory/ memory_backup/

# 3. 执行迁移
migrate.bat v1-v2

# 4. 验证
verify-migration.bat
```

---

## 工作区迁移

### 迁移步骤

```bash
# 1. 打包当前工作区
cd D:\OpenClaw
tar -czf workspace_backup.tar.gz workspace/

# 2. 传输到新环境
scp workspace_backup.tar.gz new-server:/path/

# 3. 解压
tar -xzf workspace_backup.tar.gz

# 4. 安装依赖
npm install
pip install -r requirements.txt

# 5. 验证
verify-workspace.bat
```

---

## Agent 迁移

### 导出 Agent 配置

```bash
# 导出所有 Agent
cp -r 30-AGENTS/installed/ /path/to/backup/

# 导出记忆
cp -r memory/ /path/to/backup/
```

### 导入 Agent 配置

```bash
# 复制到新位置
cp -r /path/to/backup/installed/ 30-AGENTS/

# 更新索引
update-index.bat
```

---

## 跨平台迁移

### Windows → Linux

```bash
# 1. 路径转换
# Windows: D:\OpenClaw\workspace
# Linux: /workspace

# 2. 符号链接
ln -s /workspace /root/workspace

# 3. 权限调整
chmod -R 755 /workspace
```

### Linux → Windows

```bash
# 1. 使用 WSL
wsl --import Ubuntu /path/to/wsl ./ubuntu.tar.gz

# 2. 或使用 Git Bash
# 路径自动转换
```

---

## 回滚计划

### 回滚步骤

```bash
# 1. 停止服务
pkill -f copaw

# 2. 恢复备份
backup.bat restore {backup-date}

# 3. 重启服务
copaw start

# 4. 验证
verify-rollback.bat
```

### 回滚检查清单

```
□ 配置文件恢复
□ 数据完整性
□ Agent 功能正常
□ 定时任务恢复
□ 日志正常
```

---

## 灾难恢复

### 完全重建

```bash
# 1. 克隆基础仓库
git clone https://github.com/openclaw/workspace.git

# 2. 恢复环境变量
cp .env.template .env
# 编辑 .env 填入真实值

# 3. 恢复 Agent 配置
cp -r backup/installed/ 30-AGENTS/

# 4. 恢复记忆
cp -r backup/memory/ memory/

# 5. 验证完整性
verify-all.bat
```

---

## 快捷命令

| 命令 | 用途 |
|------|------|
| `备份` | 创建完整备份 |
| `迁移` | 显示迁移指南 |
| `回滚` | 执行回滚 |
| `恢复` | 执行恢复 |
