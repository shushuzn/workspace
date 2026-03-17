# 任务 1 完成：--proxy 参数支持

## 修改内容

### 1. 移除全局代理设置
- **位置**: 第 32-35 行
- **修改前**: 硬编码 `PROXY_ADDR = "http://127.0.0.1:7897"` 并设置全局 `os.environ`
- **修改后**: 仅保留注释说明，通过 `--proxy` 参数传入

### 2. 添加 `get_proxies()` 辅助函数
- **位置**: `today_iso()` 函数之前
- **功能**: 根据传入的 proxy 字符串构建 requests 所需的 proxies 字典
```python
def get_proxies(proxy_addr: str) -> Optional[Dict[str, str]]:
    """Build proxies dict for requests if proxy_addr is provided."""
    if not proxy_addr or not proxy_addr.strip():
        return None
    return {"http": proxy_addr, "https": proxy_addr}
```

### 3. 添加 CLI 参数
- **位置**: argparse 部分
```python
parser.add_argument("--proxy", default="", help="Proxy address (e.g. http://127.0.0.1:7897). If empty, no proxy.")
```

### 4. 修改 4 个函数签名
所有网络请求函数都添加了 `proxy: str = ""` 参数：
- `fetch_arxiv_metadata(arxiv_id, timeout=30, proxy="")`
- `fetch_crossref_metadata(doi, timeout=30, proxy="")`
- `download_pdf(pdf_url, out_path, timeout=60, proxy="")`
- `call_llm_chat_completions(..., timeout=180, proxy="")`

### 5. 在函数内部使用 proxies
每个函数内部都添加了：
```python
proxies = get_proxies(proxy)
r = requests.get(..., proxies=proxies)
```

### 6. 在 main() 中传递 args.proxy
所有函数调用都添加了 `proxy=args.proxy` 参数

## 使用方法

```bash
# 不使用代理（默认）
python ai_research_os.py arxiv:2401.12345

# 使用代理
python ai_research_os.py arxiv:2401.12345 --proxy http://127.0.0.1:7897

# 使用其他代理
python ai_research_os.py arxiv:2401.12345 --proxy http://user:pass@proxy.example.com:8080
```

## 验证

```bash
# 语法检查
python -m py_compile ai_research_os.py  # OK

# 帮助信息
python ai_research_os.py --help  # 显示 --proxy 参数
```

## 备份

原始文件已备份至：
`D:\HuaweiMoveData\Users\华为\Desktop\ai_research_os\ai_research_os.py.backup_*.py`

## 下一步

任务 1 完成。可以继续处理其他优化任务。
