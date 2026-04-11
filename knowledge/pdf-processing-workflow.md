# PDF处理工作流 (2026-04-11)

## 问题
当用户上传PDF文件时，Read工具可能失败（pdftoppm不可用）。

## 工具优先级（从高到低）

### 方案1：Python pdfminer（最优先）
```bash
python -c "from pdfminer.high_level import extract_text; print(extract_text('文件路径'))"
```
**速度：10秒提取54页，比VLM快100倍**

### 方案2：Python pdfminer + 结构化提取
```python
from pdfminer.high_level import extract_text
text = extract_text('文件路径')
# 按页分割
pages = text.split('\x0c')  # PDF分页符
```

### 方案3：Python PyPDF2
```bash
python -c "from PyPDF2 import PdfReader; reader = PdfReader('文件路径'); print(len(reader.pages))"
```

### 方案4：Browser + VLM（仅备选）
当Python方案不可用时才用：
```
PDF → mcp__browser打开 → 截图 → VLM识别
```
问题：需要翻页、VLM限制、耗时是Python的100倍+

## 关键教训

- **本地Python永远最优先**：pdfminer > PyPDF2 > Browser+VLM
- **先问系统有什么工具**：不要先用复杂方案
- **bash测试工具可用性**：`python -c "import xxx"`
```javascript
mcp__plugin_chrome-devtools-mcp_chrome-devtools__new_page({
  url: "file:///文件路径"
})
```

### Step 2: 截图
```javascript
mcp__plugin_chrome-devtools-mcp_chrome-devtools__take_screenshot({
  filePath: "保存路径.png"
})
```

### Step 3: VLM识别
```javascript
mcp__MiniMax__understand_image({
  prompt: "详细描述这张截图的内容...",
  image_source: "截图文件路径"
})
```

### Step 4: 翻页
```javascript
// 点击"下一页"按钮，或在页码输入框输入页码
mcp__plugin_chrome-devtools-mcp_chrome-devtools__click({
  target: "按钮uid"
})
```

## 关键教训

- **不要等用户**：工具失败时立即尝试备用方案
- **工具链思维**：A失败→B→C→D，不停留
- **发散路径**：文本路径/图像路径/浏览器路径分开尝试

## 其他可尝试的备用方案

1. **Bash方式**
   ```bash
   node -e "const pdf=require('pdf-parse'); ..."
   ```

2. **Python方式**
   ```bash
   python -c "import PyPDF2; ..."
   ```

3. **WebFetch** (如果是在线PDF)
   ```javascript
   WebFetch({ url: "在线PDF链接" })
   ```

## 相关文件
- 记忆系统: MEMORY.md
