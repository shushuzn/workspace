# Tool Naming Convention

## 规范

### 文件名
```
tool_name_001.py
```
- snake_case
- 3位数字后缀 _001

### 类名
```
ToolName001
```
- PascalCase
- 3位数字后缀 001

### 方法/函数
```
tool_name()
```
- snake_case
- 无数字后缀

---

## 示例

| 工具功能 | 文件名 | 类名 |
|---------|--------|------|
| 工具发现 | auto_discover_001.py | AutoDiscover001 |
| 工作流市场 | workflow_market_001.py | WorkflowMarket001 |
| 自然语言 | nl_workflow_001.py | NlWorkflow001 |
| 安全编码 | safe_coder_001.py | SafeCoder001 |

---

## 工具

- `tool_namer_001.py` - 命名检查与转换
- `batch_rename_001.py` - 批量重命名
- `snippet_001.py` - 代码片段库
- `safe_coder_001.py` - 安全代码生成

---

## 重命名规则

```bash
# 扫描不符合规范的文件
py tool_namer_001.py --scan

# 查看重命名建议
py tool_namer_001.py --suggest

# 批量重命名 (dry-run)
py batch_rename_001.py --dry 10

# 批量重命名 (正式)
py batch_rename_001.py 10
```
