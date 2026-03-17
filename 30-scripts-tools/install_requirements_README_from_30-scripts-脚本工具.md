# install_requirements.py - 依赖安装脚本

**功能:** 自动安装项目所需 Python 依赖  
**作者:** OpenClaw Team  
**创建:** 2026-02-18  
**更新:** 2026-03-13 (文档创建)  
**版本:** v1.0.0

---

## 📖 功能描述

`install_requirements.py` 自动化 Python 依赖安装:

- **环境检测:** 检测 Python 版本和 pip 状态
- **依赖解析:** 解析 requirements.txt 文件
- **批量安装:** 批量安装所有依赖
- **错误处理:** 处理安装失败和冲突
- **验证安装:** 验证依赖是否正确安装

**适用场景:**
- 项目初始化
- 环境重建
- 依赖更新
- CI/CD 流程

---

## 🔧 依赖

**无外部依赖** - 使用 Python 标准库和 pip

---

## 🚀 使用方法

### 基本用法

```bash
# 安装所有依赖
python install_requirements.py

# 指定 requirements 文件
python install_requirements.py --requirements requirements.txt

# 升级已有依赖
python install_requirements.py --upgrade

# 验证安装
python install_requirements.py --verify
```

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--requirements` | str | requirements.txt | requirements 文件路径 |
| `--upgrade` | flag | False | 升级已有依赖 |
| `--verify` | flag | False | 验证安装 |
| `--dry-run` | flag | False | 模拟运行 (不实际安装) |

---

## 📊 输出示例

```
========================================
OpenClaw Dependency Installer
========================================

[1/3] Checking environment...
  + Python 3.11.0 detected
  + pip 23.0 detected

[2/3] Installing dependencies...
  + pandas 2.0.0
  + numpy 1.24.0
  + requests 2.28.0
  ...

[3/3] Verifying installation...
  + All 15 dependencies installed successfully

========================================
Installation Complete!
========================================
```

---

## ❓ 常见问题

### Q: 安装失败怎么办？

A: 尝试以下方法:
1. 升级 pip: `python -m pip install --upgrade pip`
2. 使用国内镜像：添加 `--index-url https://pypi.tuna.tsinghua.edu.cn/simple`
3. 查看详细日志：添加 `--verbose` 参数

### Q: 如何创建 requirements.txt？

A: 导出当前环境:
```bash
pip freeze > requirements.txt
```

---

*最后更新:* 2026-03-13 11:40  
*文档状态:* ✅ 完整
