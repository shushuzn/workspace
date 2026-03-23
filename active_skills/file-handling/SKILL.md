# File Handling Skill v8.0

## ⛔ 强制规则：write_file 有 8KB 限制

## 唯一可靠的工作流

### 小文件 (< 8KB)
```python
write_file("small.py", content)
```

### 大文件 (> 8KB) - Generator Pattern

**Step 1: 写生成器**
```python
write_file("gen.py", '''
content = """大文件内容放这里"""
open("output.py", "w", encoding="utf-8").write(content)
print("✅ output.py")
''')
```

**Step 2: 执行生成器**
```python
execute_shell_command("python gen.py")
```

### 判断标准

```python
size = len(content.encode('utf-8'))
if size < 8192:
    write_file(path, content)  # 直接写
else:
    # Generator Pattern
    write_file("gen.py", f'content = {repr(content)}\nopen("{path}", "w", encoding="utf-8").write(content)')
    execute_shell_command("python gen.py")
```

## ⚠️ 警告

- 违反规则 → 文件被截断
- 其他方法（PowerShell、一行命令）→ 不可靠
- 只用 Generator Pattern 写大文件

## Tested Results

| Size | Method | Result |
|------|--------|--------|
| 230 bytes | write_file | OK |
| 7,498 bytes | write_helper --lines | OK |
| 14,779 bytes | Generator script | OK |
| 26,400 bytes | Python | OK |

## Working Tools

| Tool | Location | Purpose |
|------|----------|---------|
| write_file | Built-in | Small files <8KB |
| edit_file | Built-in | Modify existing |
| write_helper.py | 30-scripts-tools | Line generation |
| gen_*.py | Custom | Complex generation |

## Proven Workflow

### Large Module (>8KB):

**Step 1:** Create generator (small, <8KB)
```python
write_file("gen_module.py", """lines = ["class X: pass" for i in range(500)]
open("module.py", "w").write("\\n".join(lines))
""")
```

**Step 2:** Run generator
```bash
python gen_module.py
```

**Step 3:** Use it
```python
from module import ClassX
```

### Line Generation:
```bash
py write_helper.py output.py --lines 500 "def f(): pass"
# Creates 500 identical lines
```

## Quick Reference

| Task | Command |
|------|---------|
| Small new | `write_file("f.py", "code")` |
| Modify | `edit_file("f.py", old, new)` |
| Many lines | `py write_helper.py f.py --lines N "template"` |
| Complex | `write_file("gen.py", "...")` then `python gen.py` |

## Pattern

```
[Generator] -> [Large File] -> [Import]

write_file("gen.py", code)  # <8KB
python gen.py                # unlimited
import large_module          # use
```
