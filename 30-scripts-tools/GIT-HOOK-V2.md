# Git Hook v2.0 增强文档

**更新日期:** 2026-03-18  
**版本:** v2.0 (嵌套备份防护)

---

## 🛡️ 防护规则

### 阻止提交 (BLOCKED)

| 类型 | 检测模式 | 示例 |
|------|----------|------|
| **报告文件** | `21-reports/*-report-*` | `21-reports/file-organization-report.md` |
| **敏感文件** | `.env`, `aliyun`, `access_key`, `secret` | `.env`, `aliyun-config.py` |
| **大文件** | `>50MB` | `large-dataset.zip` |
| **嵌套备份** | 备份目录深度>3 层 | `99-backups/backup/backup/file.txt` |
| **重复文件** | `*_from_*` 模式 | `file_from_backup.txt` |
| **编码错误** | 非 UTF-8 或有 BOM 头 | GBK 编码文件 |

### 警告 (WARNING)

| 类型 | 检测模式 | 示例 |
|------|----------|------|
| **中文文件名** | 研究目录外的中文 | `docs/我的文档.md` |
| **报告文件** | `21-reports/` 非白名单 | `21-reports/new-file.md` |

### 白名单 (ALLOWED)

**21-reports/ 允许的文件:**
- `README.md`
- `INDEX.md`
- `.gitignore`

**允许中文文件名的目录:**
- `10-RESEARCH/`
- `99-archive/`
- `90-TESTS/`

---

## 🔧 新增功能 (v2.0)

### 1. 嵌套备份检测

**检测逻辑:**
```python
# 计算路径中 backup 关键词出现次数
backup_keywords = ['backup', 'backups', '_backup', '.backup']
depth = sum(1 for part in path_parts if any(kw in part for kw in backup_keywords))

# 深度>2 即阻止
if depth > 2:
    BLOCKED
```

**示例:**
- ✅ `99-backups/auto/backup-20260318.zip` (深度=1)
- ❌ `99-backups/auto/backup/backup/file.txt` (深度=3)

### 2. _from_ 重复文件检测

**检测逻辑:**
```python
if '_from_' in filename:
    BLOCKED
```

**示例:**
- ✅ `file.txt`
- ❌ `file_from_backup.txt`

### 3. 大文件检测

**检测逻辑:**
```python
if file_size > 50MB:
    BLOCKED
```

**示例:**
- ✅ `dataset.csv` (30MB)
- ❌ `model.zip` (100MB)

---

## 📋 错误处理

### 遇到 BLOCKED 时

**选项 1: 删除文件**
```bash
git reset HEAD <file>
rm <file>
```

**选项 2: 强制提交 (不推荐)**
```bash
git commit --no-verify
```

### 遇到编码错误时

**选项 1: VSCode 修复**
1. 打开文件
2. 右下角选择 "UTF-8"
3. 保存

**选项 2: Notepad++ 修复**
1. 打开文件
2. 编码 → 转为 UTF-8 无 BOM
3. 保存

**选项 3: 脚本修复**
```bash
py 30-scripts-tools/utils/remove-bom.py <file>
```

---

## 🧪 测试方法

### 测试嵌套备份阻止
```bash
mkdir -p 99-backups/test/backup/deep
echo "test" > 99-backups/test/backup/deep/file.txt
git add 99-backups/test/backup/deep/file.txt
git commit -m "test"
# 应该被阻止
```

### 测试 _from_ 阻止
```bash
echo "test" > test_from_backup.txt
git add test_from_backup.txt
git commit -m "test"
# 应该被阻止
```

### 测试大文件阻止
```bash
# 创建 60MB 文件
fsutil file createnew large.bin 62914560
git add large.bin
git commit -m "test"
# 应该被阻止
```

---

## 📊 统计信息

**查看被阻止的提交尝试:**
```bash
# 查看 git log 中的 --no-verify 提交
git log --oneline --all | grep -i "no-verify"
```

**查看 Hook 日志:**
```bash
# Hook 输出会显示在 git commit 时
git commit -m "test"
```

---

## 🔗 相关文件

| 文件 | 说明 |
|------|------|
| `.git/hooks/pre-commit` | Hook 脚本 |
| `30-scripts-tools/install-git-hooks.py` | 安装脚本 |
| `30-scripts-tools/backup-strategy-restructure.py` | 备份重构脚本 |
| `99-backups/backup-config.json` | 备份配置 |

---

## 🎯 最佳实践

### 备份文件
1. 使用 `99-backups/auto/` 存放自动备份
2. 使用 `99-backups/manual/` 存放手动备份
3. 使用 `99-backups/archive/` 存放归档备份
4. **避免** 在备份目录内再创建备份目录

### 命名规范
1. **避免** 使用 `_from_` 模式
2. **避免** 中文文件名 (研究目录除外)
3. **使用** 时间戳命名：`backup-20260318-143022.zip`

### 大文件处理
1. >50MB 文件应压缩
2. 数据集应使用 Git LFS 或外部存储
3. 模型文件应上传到 HuggingFace/zenodo

---

*文档版本：v2.0*  
*最后更新：2026-03-18*
