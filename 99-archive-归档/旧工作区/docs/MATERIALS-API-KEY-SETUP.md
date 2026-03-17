# 🔑 Materials Project API Key 配置指南

**配置时间:** 2026-03-05 14:24  
**API Key:** `BZa02Shw2FdYQ8YOHkKdg7CeK3KIlWAj`  
**状态:** ✅ 已配置

---

## 📋 配置步骤

### 1. 创建 .env 文件

已在项目根目录创建 `.env` 文件：

```bash
# Materials Project API
MP_API_KEY=BZa02Shw2FdYQ8YOHkKdg7CeK3KIlWAj
MP_BASE_URL=https://api.materialsproject.org
```

### 2. 验证配置

```bash
cd D:\OpenClaw\workspace
python scripts/test-mp-api.py
```

### 3. 使用 API

```python
from materials_project_api import MaterialsProjectClient

client = MaterialsProjectClient()  # 自动从.env 读取 API Key

# 搜索材料
materials = client.search_materials(formula="LiCoO2")

# 获取详情
details = client.get_material_details("mp-1234")

# 获取性能
properties = client.get_properties("mp-1234")
```

---

## 🔒 安全提示

### ⚠️ 重要
- **不要**将 `.env` 文件提交到 Git
- **不要**在公开场合分享 API Key
- **定期**轮换 API Key

### ✅ 已配置
- `.env` 已添加到 `.gitignore`
- API Key 从环境变量读取
- 代码中无硬编码密钥

---

## 📊 API 使用限制

| 等级 | 请求限制 | 当前等级 |
|------|----------|----------|
| Free | 1,000 请求/日 | ✅ |
| Academic | 10,000 请求/日 | 可申请 |
| Commercial | 自定义 | 需联系 |

**当前配额:** 1,000 请求/日  
**预计日用量:** ~200 请求  
**配额使用:** ~20%

---

## 🔍 测试 API 连接

运行测试脚本：

```bash
python scripts/test-mp-api.py
```

**预期输出:**
```
✅ API Key 有效
✅ 连接成功
✅ 可查询材料数据
```

---

## 📚 相关文档

- [Materials Project API 文档](https://docs.materialsproject.org)
- [API 使用示例](https://github.com/materialsproject/pymatgen)
- [本地配置指南](MATERIALS-API-DESIGN.md)

---

*最后更新：2026-03-05 14:24*
