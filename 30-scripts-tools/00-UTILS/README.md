# 00-UTILS - 通用工具

**用途:** 跨项目通用工具、缓存、备份、辅助脚本

---

## 📁 目录结构

```
00-UTILS/
├── cache/              # 缓存目录
│   └── __pycache__/    # Python 字节码缓存
├── backups/            # 备份文件
│   └── *.log           # 备份日志
├── utils/              # 工具函数库
├── tools/              # 通用工具脚本
│   ├── search.ps1      # 文件搜索
│   ├── view-tags.ps1   # 标签查看
│   └── stop.sh         # 停止脚本
└── README.md           # 本文档
```

---

## 🛠️ 工具说明

### search.ps1
在指定目录中搜索文件

**用法:**
```powershell
.\search.ps1 -Pattern "*.py" -Path "D:\OpenClaw\workspace"
```

### view-tags.ps1
查看文件标签信息

**用法:**
```powershell
.\view-tags.ps1 -File "example.py"
```

### stop.sh
停止运行中的服务

**用法:**
```bash
./stop.sh [service_name]
```

---

## 📦 缓存管理

### 清理缓存
```powershell
# 清理 Python 缓存
Remove-Item -Recurse -Force cache/__pycache__/*

# 清理所有缓存
Remove-Item -Recurse -Force cache/*
```

---

## 🗄️ 备份管理

### 查看备份
```powershell
# 列出所有备份
Get-ChildItem backups/ -File | Select-Object Name, Length, LastWriteTime
```

### 恢复备份
```powershell
# 恢复指定备份
Copy-Item backups/backup-20260311.zip -Destination "目标路径"
```

---

## 🔧 添加工具

### 新工具开发规范
1. 脚本放在 `tools/` 目录
2. 工具函数放在 `utils/` 目录
3. 必须包含 README 说明
4. 必须经过测试验证

### 模板
```python
#!/usr/bin/env python3
# tool_name.py - 工具说明

def main():
    """主函数"""
    pass

if __name__ == "__main__":
    main()
```

---

## 📊 统计信息

| 类别 | 数量 | 大小 |
|------|------|------|
| 工具脚本 | 4 | ~10KB |
| 缓存文件 | 0 | 0KB |
| 备份文件 | 0 | 0KB |
| **总计** | **4** | **~10KB** |

---

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

---

## 📄 许可证

MIT License

---

*最后更新：2026-03-11 | 版本 v1.0*
