# 🎮 Star Forge Web - 星之熔炉网页版

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![React](https://img.shields.io/badge/React-19.2.4-61dafb)
![Vite](https://img.shields.io/badge/Vite-8.0.1-646cff)

一款类似星露谷的农场建造游戏网页版。使用 React 和 Vite 构建。

## 🚀 一键启动

### 方法一：双击启动脚本（推荐）

1. **交互式菜单** - 双击 `启动菜单.ps1`
   - 提供 5 种启动模式可选
   - 自动检测并安装依赖
   - 包含清理和说明功能

2. **快速开发** - 双击 `启动游戏.bat`
   - 自动打开浏览器
   - 启动开发服务器

3. **生产预览** - 双击 `预览版本.bat`
   - 使用构建后的生产版本
   - 适合测试最终效果

### 方法二：命令行启动

```bash
# 安装依赖
npm install

# 开发模式（推荐）
npm run dev

# 生产预览
npm run preview

# 构建生产版本
npm run build
```

## 🎯 游戏功能

### ⚡ 核心玩法
- **点击收集** - 点击收集能量
- **建筑系统** - 建造各种建筑自动产生能量
- **升级系统** - 购买升级提升效率
- **成就系统** - 解锁各种成就
- **永恒重置** - 重置游戏获得永久加成

### 💾 存档系统
- **自动存档** - 自动保存游戏进度
- **本地存储** - 使用浏览器 localStorage
- **导出导入** - 支持游戏数据导出和导入

### 🎨 界面功能
- **多语言支持** - 中文/英文切换
- **主题切换** - 深色/浅色模式
- **画质选项** - 低/中/高画质
- **响应式设计** - 适配各种屏幕尺寸

## 📁 项目结构

```
star-forge-web/
├── src/
│   ├── components/      # React 组件
│   │   ├── GameBoard.jsx    # 游戏主面板
│   │   ├── ResourceDisplay.jsx    # 资源显示
│   │   ├── BuildingPanel.jsx      # 建筑面板
│   │   ├── UpgradePanel.jsx       # 升级面板
│   │   ├── PrestigePanel.jsx      # 重置面板
│   │   ├── StatsPanel.jsx         # 统计面板
│   │   ├── AchievementToast.jsx    # 成就提示
│   │   ├── TabPanel.jsx          # 标签页组件
│   │   ├── SettingsPanel.jsx      # 设置面板
│   │   ├── ThemeToggle.jsx        # 主题切换
│   │   ├── LanguageToggle.jsx      # 语言切换
│   │   └── QualityToggle.jsx      # 画质切换
│   ├── hooks/           # 自定义 Hooks
│   ├── store/           # 状态管理
│   ├── i18n/            # 国际化
│   │   ├── translations.js    # 翻译文件
│   │   └── LanguageContext.jsx
│   ├── data/            # 游戏数据
│   └── styles/           # 全局样式
├── public/              # 静态资源
├── 启动菜单.ps1         # 交互式启动菜单
├── 启动游戏.bat         # 快速开发启动
├── 预览版本.bat         # 快速预览启动
└── package.json
```

## 🛠️ 技术栈

- **前端框架** - React 19.2.4
- **构建工具** - Vite 8.0.1
- **样式方案** - CSS Modules
- **状态管理** - React Context
- **国际化** - Context API

## 🎮 游戏指南

### 基础操作
1. **收集能量** - 点击中央的能量球 ⚡
2. **购买建筑** - 在建筑面板购买自动产出能量的建筑
3. **购买升级** - 在升级面板购买提升效率的升级
4. **永恒重置** - 积累足够能量后进行重置，获得永久加成

### 快捷操作
- 点击右上角 🌐 按钮切换语言
- 点击 ☀️/🌙 按钮切换主题
- 点击 ⚙️ 按钮打开设置面板
- 使用标签页切换建筑/升级/永恒面板
- 选择画质等级（低/中/高）

### 画质选项
- **🔋 低画质** - 省电模式，禁用所有动画
- **⚖️ 中画质** - 平衡模式，简化视觉效果
- **🎨 高画质** - 完整模式，保留所有效果

## 📝 可用命令

```bash
npm run dev        # 启动开发服务器
npm run build      # 构建生产版本
npm run preview    # 预览生产版本
```

## 🔧 开发指南

### 环境要求
- Node.js 18+
- npm 9+

### 首次运行
1. 双击 `启动菜单.ps1`
2. 选择选项 1 (开发模式)
3. 等待依赖安装完成
4. 自动打开浏览器

## 📄 许可证

本项目仅供学习和娱乐使用。

---

**享受 Star Forge Web！** ⚡🏗️
