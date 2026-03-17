# 知识卡片生成器 - Android 版

**本地离线运行，无需网络**

---

## 📱 安装

### 方法 1: 直接安装 APK

```
1. 下载 APK (从 bin/ 文件夹)
2. 允许"未知来源"
3. 安装
4. 打开使用
```

### 方法 2: 自己编译

```bash
# 安装 Buildozer
pip install buildozer

# 初始化
buildozer init

# 编译 APK
buildozer -v android debug

# APK 位置：bin/*.apk
```

---

## 🚀 使用

1. 打开 App
2. 选择 PDF 文件
3. 点击"生成知识卡片"
4. 等待处理
5. 查看结果 (HTML 格式)

---

## 📦 功能

- ✅ PDF 自动解析
- ✅ 元数据提取
- ✅ 章节识别
- ✅ 参考文献提取
- ✅ HTML 导出
- ✅ 本地存储
- ✅ 离线使用

---

## ⚙️ 权限

- `READ_EXTERNAL_STORAGE` - 读取 PDF
- `WRITE_EXTERNAL_STORAGE` - 保存结果

---

## 📊 系统要求

- Android 5.0+ (API 21+)
- 存储空间：100MB+
- 内存：512MB+

---

## 🛠️ 开发

### 环境要求

- Python 3.8+
- Kivy 1.11.1
- Buildozer 1.4+
- Linux/macOS (Windows 需要 WSL)

### 编译步骤

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Buildozer
pip install buildozer

# 编译
buildozer -v android debug

# 清理
buildozer android clean
```

---

## 📝 注意事项

1. **首次编译慢** - 需要下载 Android SDK/NDK (约 2GB)
2. **Windows 用户** - 建议使用 WSL 或 Linux 虚拟机
3. **APK 大小** - 约 50-80MB (包含 Python 运行时)

---

## 📄 许可证

MIT License

---

*知识卡片生成器 - Android 版 v1.0*
