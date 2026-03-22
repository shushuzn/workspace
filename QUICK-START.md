# 🚀 OpenClaw Cursor Mode 快速参考

## ⚡ 一键启动

```bash
cd D:\OpenClaw\workspace
copaw.bat "你的编程任务"
```

---

## 📋 常用命令

| 任务类型 | 示例命令 |
|---------|---------|
| **修复 Bug** | `copaw.bat "修复 game.js 中的点击计数 bug"` |
| **添加功能** | `copaw.bat "给游戏添加连击系统"` |
| **代码重构** | `copaw.bat "重构 buildings.js 使用 ES6"` |
| **运行测试** | `copaw.bat "运行所有测试并修复失败"` |
| **项目分析** | `copaw.bat "分析项目结构和依赖关系"` |
| **查找代码** | `copaw.bat "搜索所有使用 totalClicks 的地方"` |

---

## ✅ 自动执行命令

```
✓ python/pip/pytest    ✓ npm/pnpm/yarn/node
✓ git                  ✓ cargo/go/rustc
✓ cd/dir/type/echo     ✓ copy/del/mkdir
✓ eslint/prettier      ✓ tsc/webpack/vite
```

---

## 🎯 最佳实践

### ✅ 好的描述
```
"修复 game.js 中 clickGold 函数的 bug，
点击后金币没有增加，总点击数也没有更新"
```

### ❌ 差的描述
```
"改一下代码"
```

---

## 📁 重要文件

| 文件 | 用途 |
|------|------|
| `copaw.bat` | 启动脚本 |
| `cursor-mode.bat` | 使用说明 |
| `.openclaw/config.json` | 工作区配置 |
| `CURSOR-MODE-READY.md` | 完整文档 |

---

## 🔧 故障排除

```bash
# 验证安装
test-cursor-mode.bat

# 查看日志
dir .copaw-logs

# 重新安装 MCP
npm install -g @modelcontextprotocol/server-filesystem
```

---

**开始编程！** 🎉

```bash
copaw.bat "分析当前项目，找出可以优化的代码"
```
