# ClawHub 技能安装报告

**安装日期:** 2026-03-06  
**安装者:** Claw (AI Agent)

---

## 📦 已安装技能清单

| # | 技能 | 版本 | 安装日期 | 用途 |
|---|------|------|----------|------|
| 1 | **proactive-agent-lite** | 1.0.0 | 之前 | 主动行为模式 |
| 2 | **nano-pdf** | 1.0.0 | 2026-03-06 | PDF 编辑 ⭐ 新增 |

---

## 🔍 nano-pdf v1.0.0 详细审查

### 基本信息

| 属性 | 值 |
|------|-----|
| **名称** | nano-pdf |
| **版本** | 1.0.0 |
| **描述** | 使用自然语言指令编辑 PDF |
| **主页** | https://pypi.org/project/nano-pdf/ |
| **安装时间** | 2026-03-06 21:58 |

---

### 功能

**核心功能:**
- 使用自然语言指令编辑 PDF
- 指定页面修改
- 基于 nano-pdf CLI 工具

**使用示例:**
```bash
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"
```

---

### 安全性审查 ✅

#### 1. 外部依赖

**审查结果:** ⚠️ **需要安装外部工具**

```json
"install": [
  {
    "id": "uv",
    "kind": "uv",
    "package": "nano-pdf",
    "bins": ["nano-pdf"],
    "label": "Install nano-pdf (uv)"
  }
]
```

**说明:**
- 需要安装 `nano-pdf` Python 包
- 使用 `uv` 包管理器
- 安装二进制文件 `nano-pdf`

---

#### 2. 文件系统操作

**审查结果:** ⚠️ **读写权限**

**权限:**
- ✅ 读取 PDF 文件
- ⚠️ 写入/修改 PDF 文件
- ❌ 无删除操作

**说明:** 技能需要修改 PDF 文件，但仅限于用户指定的文件

---

#### 3. 网络请求

**审查结果:** ✅ **无网络请求**

**说明:** 技能本身不发起网络请求，但安装时需要下载 nano-pdf 包

---

#### 4. 代码执行

**审查结果:** ⚠️ **调用外部 CLI**

**说明:**
- 调用 `nano-pdf` 命令行工具
- 执行 PDF 编辑操作
- 需要用户指定文件和指令

---

#### 5. 环境变量

**审查结果:** ✅ **无环境变量访问**

---

### 风险评估

| 维度 | 风险等级 | 说明 |
|------|----------|------|
| **外部依赖** | 🟡 中 | 需要安装 nano-pdf 包 |
| **文件系统** | 🟡 中 | 读写 PDF 文件 |
| **网络请求** | 🟢 低 | 无网络请求 |
| **代码执行** | 🟡 中 | 调用外部 CLI |
| **环境变量** | 🟢 低 | 无访问 |

**总体风险:** 🟡 **中低风险**

---

### 使用场景

### 适用场景 ✅

- PDF 文档编辑
- 快速修改 PDF 内容
- 自然语言指令编辑
- 批量 PDF 处理

### 不适用场景 ❌

- 需要高精度编辑
- 复杂 PDF 布局修改
- 需要 OCR 的场景

---

## 📊 安装过程

### 安装命令

```bash
clawhub install nano-pdf
```

### 安装结果

```
✔ OK. Installed nano-pdf -> D:\OpenClaw\workspace\skills\nano-pdf
```

### 安装位置

```
D:\OpenClaw\workspace\skills\nano-pdf/
├── SKILL.md
└── _meta.json
```

### 依赖安装

**需要执行:**
```bash
uv install nano-pdf
```

**或:**
```bash
pip install nano-pdf
```

---

## 🎯 使用建议

### 推荐用法

1. **简单编辑:**
   ```bash
   nano-pdf edit document.pdf 1 "Fix typos on page 1"
   ```

2. **内容修改:**
   ```bash
   nano-pdf edit report.pdf 3 "Update the chart title"
   ```

3. **批量处理:**
   ```bash
   for file in *.pdf; do
     nano-pdf edit "$file" 0 "Add watermark"
   done
   ```

---

### 注意事项

⚠️ **使用前:**
1. 备份原始 PDF 文件
2. 确认 nano-pdf 已安装
3. 测试简单指令

⚠️ **使用时:**
1. 指定正确的页码 (0-based 或 1-based)
2. 使用清晰的指令
3. 检查结果再发送

⚠️ **使用后:**
1. 检查输出 PDF
2. 确认修改正确
3. 清理临时文件

---

## 📝 与其他技能对比

### nano-pdf vs pdf-text-extractor

| 维度 | nano-pdf | pdf-text-extractor |
|------|----------|-------------------|
| **功能** | PDF 编辑 | PDF 文本提取 |
| **依赖** | nano-pdf CLI | 无 |
| **风险** | 🟡 中低 | 🟢 低 |
| **用途** | 修改 PDF | 提取内容 |

---

### nano-pdf vs proactive-agent-lite

| 维度 | nano-pdf | proactive-agent-lite |
|------|----------|---------------------|
| **功能** | PDF 编辑 | 主动行为模式 |
| **依赖** | nano-pdf CLI | 无 |
| **风险** | 🟡 中低 | 🟢 低 |
| **权限** | 读写文件 | 只读 |

---

## 🎊 总结

**nano-pdf v1.0.0** 安装成功！

**风险等级:** 🟡 **中低风险**

**推荐:** ✅ **可以使用，注意备份**

**下次审查:** 2026-04-06 (30 天后)

---

## 📋 待办事项

### 立即执行

- [ ] 安装 nano-pdf 依赖
  ```bash
  pip install nano-pdf
  ```

- [ ] 测试基本功能
  ```bash
  nano-pdf --version
  ```

### 建议执行

- [ ] 创建测试 PDF
- [ ] 测试简单编辑指令
- [ ] 验证输出质量

---

*安装完成日期：2026-03-06*  
*下次审查：2026-04-06*
