# 文件类型 → 工具优先级 (2026-04-11)

## 原则
1. **本地工具优先**：Python/Node.js原生库 > 外部服务
2. **先检测后执行**：`python -c "import xxx"` 验证可用性
3. **按文件类型分流**：文本/图片/PDF/代码 不同处理路径

---

## 文本文件

| 文件类型 | 优先级 | 命令 |
|---------|--------|------|
| `.txt` | 1. Read工具 | 直接读取 |
| `.md` | 1. Read工具 | 直接读取 |
| `.json` | 1. Read工具 | 直接读取 |
| `.csv` | 1. Bash pandas | `python -c "import pandas; print(pandas.read_csv('file.csv'))"` |
| `.yaml/.yml` | 1. Read工具 | 直接读取 |
| `.xml` | 1. Bash xml.etree | `python -c "import xml.etree.ElementTree; ..."` |

---

## PDF文件

| 文件类型 | 优先级 | 命令 |
|---------|--------|------|
| `.pdf` | 1. **Python pdfminer** | `python -c "from pdfminer.high_level import extract_text; print(extract_text('file.pdf'))"` |
| `.pdf` | 2. Python PyPDF2 | `python -c "from PyPDF2 import PdfReader; ..."` |
| `.pdf` | 3. Browser+VLM | mcp__browser打开 → 截图 → VLM识别 |
| `.pdf` | 4. Read工具 | 直接读取（可能失败） |

---

## 图片文件

| 文件类型 | 优先级 | 命令 |
|---------|--------|------|
| `.png/.jpg/.jpeg` | 1. VLM识别 | `mcp__MiniMax__understand_image()` |
| `.png/.jpg/.jpeg` | 2. Bash PIL | `python -c "from PIL import Image; ..."` |
| `.gif` | 1. Bash PIL | `python -c "from PIL import Image; ..."` |

---

## 代码文件

| 文件类型 | 优先级 | 命令 |
|---------|--------|------|
| `.js/.mjs` | 1. Node.js | `node -e "..."` 或直接运行 |
| `.py` | 1. Python | `python file.py` |
| `.sh` | 1. Bash | `bash file.sh` |
| `.go` | 1. Go | `go run file.go` |

---

## 文档文件

| 文件类型 | 优先级 | 命令 |
|---------|--------|------|
| `.docx` | 1. Bash python-docx | `python -c "from docx import Document; ..."` |
| `.xlsx` | 1. Bash openpyxl | `python -c "from openpyxl import load_workbook; ..."` |
| `.pptx` | 1. Bash python-pptx | `python -c "from pptx import Presentation; ..."` |

---

## 压缩/特殊

| 文件类型 | 优先级 | 命令 |
|---------|--------|------|
| `.zip` | 1. Bash unzip | `unzip file.zip` |
| `.tar/.gz` | 1. Bash tar | `tar -xf file.tar.gz` |
| `.db/.sqlite` | 1. Bash sqlite3 | `sqlite3 file.db ".tables"` |

---

## 快速检测脚本

```bash
# 检测可用的文档处理工具
python -c "import pdfminer; print('pdfminer:OK')" 2>/dev/null || echo "pdfminer:X"
python -c "import PyPDF2; print('PyPDF2:OK')" 2>/dev/null || echo "PyPDF2:X"
python -c "import docx; print('docx:OK')" 2>/dev/null || echo "docx:X"
python -c "import openpyxl; print('openpyxl:OK')" 2>/dev/null || echo "openpyxl:X"
```

---

## 相关文件
- `pdf-processing-workflow.md` — PDF专项处理流程
- `MEMORY.md` — 记忆索引
