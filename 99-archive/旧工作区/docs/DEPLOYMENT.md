# AI+Materials 系统 - 生产部署说明

**版本:** Phase 12 Complete  
**状态:** 生产就绪  
**要求:** 真实数据和 API

---

## ⚠️ 重要说明

**本系统禁止使用模拟数据！**

所有 ML 模型和 API 客户端都要求：
1. ✅ 真实模型文件
2. ✅ 真实 API Key
3. ✅ 真实数据输入

---

## 🔑 必需配置

### 1. Materials Project API

**获取 API Key:**
1. 访问 https://materialsproject.org/dashboard
2. 注册/登录账号
3. 生成 API Key

**配置方式:**

方式 1: `.env` 文件
```bash
# 在 D:\OpenClaw\workspace\.env 创建
MP_API_KEY=your_api_key_here
MP_BASE_URL=https://api.materialsproject.org
```

方式 2: 环境变量
```powershell
# PowerShell
$env:MP_API_KEY="your_api_key_here"

# 或系统环境变量
setx MP_API_KEY "your_api_key_here"
```

**验证:**
```bash
py scripts/materials/materials-project-api.py
```

---

### 2. ML 模型依赖

#### CGCNN 模型

**安装依赖:**
```bash
pip install onnxruntime
```

**准备模型:**
1. 训练或下载 CGCNN ONNX 模型
2. 放置在 `models/cgcnn.onnx`
3. 修改配置指向模型路径

**配置:**
```python
# scripts/materials/cgcnn-model.py
config = CPUConfig()
model = get_cgcnn_model(config)
model.load_model("models/cgcnn.onnx")  # 真实模型路径
```

#### MEGNet 模型

**安装依赖:**
```bash
pip install onnxruntime matgl
```

**准备模型:**
```python
# scripts/materials/megnet-model.py
model = get_megnet_model(config)
model.load_model(pretrained="formation_energy")  # 下载真实模型
```

---

### 3. 其他依赖

#### Streamlit UI (可选)
```bash
pip install streamlit
```

#### 完整依赖列表
```bash
# 核心依赖
onnxruntime>=1.15.0
psutil>=5.9.0
requests>=2.28.0

# 材料科学
matgl>=0.9.0
pymatgen>=2023.0.0
ase>=3.22.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0

# Web UI (可选)
streamlit>=1.22.0
fastapi>=0.95.0
uvicorn>=0.22.0

# 开发工具
pytest>=7.3.0
black>=23.0.0
```

---

## 📁 数据准备

### 晶体结构数据

**格式:** CIF 文件或字典
```python
crystal_structure = {
    'lattice': {
        'a': 4.0, 'b': 4.0, 'c': 4.0,
        'alpha': 90, 'beta': 90, 'gamma': 90
    },
    'atoms': [
        {'element': 'Li', 'x': 0, 'y': 0, 'z': 0},
        {'element': 'Fe', 'x': 0.5, 'y': 0.5, 'z': 0.5},
        # ...
    ]
}
```

### 论文数据

**来源:**
- arXiv API
- Materials Project
- 本地 PDF 文件

**处理流程:**
```bash
# 1. 收集论文
py scripts/arxiv-daily.py --categories cs.AI,cs.LG,cond-mat.mtrl-sci

# 2. 下载 PDF
py scripts/materials/materials-collector.py

# 3. 解析提取
py scripts/materials/materials-ner-model.py
py scripts/materials/property-data-extractor.py
```

---

## 🧪 测试验证

### 批量测试
```bash
py scripts/materials/batch-test-all.py
```

**预期结果:**
- 核心模块：100% 通过
- 导入失败：0 (无模拟模式)
- Main 失败：仅缺少真实模型/数据时

### 单元测试
```bash
pytest scripts/materials/materials-testing.py -v
```

### 端到端测试
```bash
py scripts/materials/practical-test-full.py
```

**要求:**
- ✅ Materials Project API Key 配置
- ✅ ML 模型已加载
- ✅ 测试数据准备

---

## 🚀 生产部署

### Docker 部署

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY scripts/ ./scripts/
COPY models/ ./models/

# 配置环境变量
ENV MP_API_KEY=${MP_API_KEY}
ENV PYTHONPATH=/app

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/materials/materials-testing.py || exit 1

CMD ["python", "scripts/materials/model-serving.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  materials-api:
    build: .
    environment:
      - MP_API_KEY=${MP_API_KEY}
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    ports:
      - "8000:8000"
    restart: unless-stopped
  
  mongodb:
    image: mongo:6
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongodb_data:
```

---

## 📊 监控与日志

### 性能监控
```python
# CPU 使用
from cgcnn-model import CPUMonitor
monitor = CPUMonitor(threshold=70.0)
cpu_percent = monitor.get_cpu_percent()

# 缓存统计
cache_stats = model.cache.get_stats()
print(f"Hit rate: {cache_stats['hit_rate']}")
```

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/materials.log'),
        logging.StreamHandler()
    ]
)
```

---

## ⚠️ 故障排除

### 问题 1: API Key 错误
```
ValueError: MP_API_KEY not found!
```
**解决:** 配置环境变量或 `.env` 文件

### 问题 2: 模型加载失败
```
RuntimeError: Model not loaded
```
**解决:** 
1. 检查模型文件路径
2. 安装 `onnxruntime`
3. 验证模型格式

### 问题 3: 导入失败
```
ImportError: No module named 'xxx'
```
**解决:** `pip install -r requirements.txt`

---

## 📝 检查清单

部署前确认:

- [ ] Materials Project API Key 配置
- [ ] ML 模型文件准备
- [ ] 依赖安装完成
- [ ] 数据库配置 (MongoDB)
- [ ] 日志目录创建
- [ ] 测试验证通过
- [ ] 监控配置完成

---

*文档更新时间：2026-03-05 22:45*  
**状态：✅ 生产就绪 (无模拟数据)**
