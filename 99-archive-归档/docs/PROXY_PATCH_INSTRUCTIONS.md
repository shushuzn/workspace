# AI Research OS --proxy 参数补丁说明

## 问题
原始文件 `ai_research_os.py` 存在编码损坏，无法直接修改。

## 解决方案

### 选项 A: 从原始源恢复后应用补丁
1. 从 Git 或备份恢复原始 `ai_research_os.py`
2. 运行补丁脚本：`python apply_proxy_patch.py`

### 选项 B: 手动修改（6 处）

#### 1. 移除全局代理设置（约第 32-35 行）
```python
# 删除这 4 行：
# ============ 代理配置 (Clash) ============
PROXY_ADDR = "http://127.0.0.1:7897"
os.environ["HTTP_PROXY"] = PROXY_ADDR
os.environ["HTTPS_PROXY"] = PROXY_ADDR
# ==========================================

# 替换为：
# ============ 代理配置 ============
# 通过 --proxy 参数传入，不再硬编码全局 env
# ==================================
```

#### 2. 添加辅助函数（在 `today_iso()` 之前）
```python
def get_proxies(proxy_addr: str) -> Optional[Dict[str, str]]:
    """Build proxies dict for requests if proxy_addr is provided."""
    if not proxy_addr or not proxy_addr.strip():
        return None
    return {"http": proxy_addr, "https": proxy_addr}
```

#### 3. 添加 CLI 参数（在 argparse 部分，约第 1050 行）
```python
parser.add_argument("--proxy", default="", help="Proxy address (e.g. http://127.0.0.1:7897). If empty, no proxy.")
```

#### 4. 修改 4 个函数签名
```python
# fetch_arxiv_metadata
def fetch_arxiv_metadata(arxiv_id: str, timeout: int = 30, proxy: str = "") -> Paper:

# fetch_crossref_metadata  
def fetch_crossref_metadata(doi: str, timeout: int = 30, proxy: str = "") -> Tuple[Paper, Optional[str]]:

# download_pdf
def download_pdf(pdf_url: str, out_path: Path, timeout: int = 60, proxy: str = "") -> None:

# ai_call
def ai_call(url: str, api_key: str, model: str, system_prompt: str, user_prompt: str, timeout: int = 120, proxy: str = "") -> str:
```

#### 5. 在函数内部添加 proxies 参数
```python
# fetch_arxiv_metadata 中：
proxies = get_proxies(proxy)
r = requests.get(url, timeout=timeout, proxies=proxies)

# fetch_crossref_metadata 中：
proxies = get_proxies(proxy)
r = requests.get(url, timeout=timeout, headers={...}, proxies=proxies)

# download_pdf 中：
proxies = get_proxies(proxy)
with requests.get(pdf_url, stream=True, timeout=timeout, proxies=proxies) as r:

# ai_call 中：
proxies = get_proxies(proxy)
r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout, proxies=proxies)
```

#### 6. 在 main() 中传递 args.proxy
```python
# 所有调用处添加 proxy=args.proxy 参数
paper = fetch_arxiv_metadata(arxiv_id, proxy=args.proxy)
download_pdf(paper.pdf_url, pdf_path, proxy=args.proxy)
ai_draft = ai_call(..., proxy=args.proxy)
```

## 使用方法
```bash
# 不使用代理（默认）
python ai_research_os.py arxiv:2401.12345

# 使用代理
python ai_research_os.py arxiv:2401.12345 --proxy http://127.0.0.1:7897
```

## 测试
```bash
python -m py_compile ai_research_os.py
python ai_research_os.py --help
```
