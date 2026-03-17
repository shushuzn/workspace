# Git Hooks - 运营者检查

## 📦 安装

```bash
python 30-scripts-tools/setup-git-hooks.py
```

## ✅ 功能

### 1. 禁止自动生成报告文件

**阻止模式:**
- `21-reports/*-report-*.md`
- `21-reports/operations-report-*`
- `21-reports/*-brainstorm-*`
- `21-reports/*-summary-*`

**允许:**
- `21-reports/README.md`
- `21-reports/INDEX.md`
- `21-reports/.gitignore`

### 2. 禁止编码错误

**检查:**
- ✅ 必须 UTF-8 编码
- ✅ 禁止 BOM 头
- ⚠️ 警告中文文件名（研究目录除外）

**修复:**
1. VSCode: 右下角选择 'UTF-8' 保存
2. Notepad++: 编码 → 转为 UTF-8 无 BOM

### 3. 禁止敏感文件

**阻止:**
- `*.env`
- `*aliyun*`
- `*access_key*`
- `*secret*`
- `*.tiff`

### 4. 警告中文文件名

**允许目录:**
- `10-RESEARCH/` (研究数据)
- `99-archive/` (归档)
- `90-TESTS/` (测试)

**其他目录:** 建议英文文件名

## 🚫 禁用

紧急情况下跳过检查:

```bash
git commit --no-verify -m "消息"
```

## 🧪 测试

```bash
# 测试 1: 创建报告文件 (应阻止)
echo "# 测试" > 21-reports/test-report.md
git add 21-reports/test-report.md
git commit -m "测试"

# 测试 2: 创建 GBK 编码文件 (应阻止)
echo "测试" > test-gbk.txt
git add test-gbk.txt
git commit -m "测试"

# 测试 3: 正常文件 (应通过)
echo "# 测试" > test-normal.md
git add test-normal.md
git commit -m "测试"
```

## 📋 检查流程

```
git commit
    ↓
Git Hooks (pre-commit)
    ↓
1. 检查报告文件 → 阻止？
2. 检查敏感文件 → 阻止？
3. 检查编码 → 错误？
4. 检查文件名 → 警告？
    ↓
通过 → 提交成功
失败 → 显示错误信息
```

## 💡 常见错误

### 错误 1: 编码错误

```
❌ 编码错误：无法用 UTF-8 读取
```

**解决:** 用 UTF-8 重新保存文件

### 错误 2: 报告文件

```
❌ 阻止提交：自动生成的报告文件
```

**解决:** 删除报告或使用 `--no-verify`

### 错误 3: 敏感文件

```
❌ 阻止提交：敏感文件：.env
```

**解决:** 将敏感文件加入 `.gitignore`

## 📝 更新日志

| 日期 | 版本 | 更新 |
|------|------|------|
| 2026-03-18 | v1.0 | 初始版本 |
| | | - 报告文件检查 |
| | | - 编码检查 (UTF-8) |
| | | - 敏感文件检查 |
| | | - 中文文件名警告 |
