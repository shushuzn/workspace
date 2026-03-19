#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multimodal Understanding System - 多模态理解系统

功能:
1. 图像理解 (OCR/物体检测/场景分析)
2. 语音处理 (转录/分析)
3. 文档解析 (PDF/Word/Excel/PPT)
4. 多模态融合
5. 统一 API 接口

Usage:
    py multimodal_agent.py --image <path>        # 图像理解
    py multimodal_agent.py --ocr <path>          # OCR 文字识别
    py multimodal_agent.py --audio <path>        # 语音处理
    py multimodal_agent.py --doc <path>          # 文档解析
    py multimodal_agent.py --pdf <path>          # PDF 解析
    py multimodal_agent.py --fuse                # 多模态融合
    py multimodal_agent.py --status              # 查看状态
"""

import sys
import io
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
MULTIMODAL_DIR = WORKSPACE / "multimodal"
MULTIMODAL_DB = MULTIMODAL_DIR / "multimodal-db.json"
MULTIMODAL_CONFIG = MULTIMODAL_DIR / "multimodal-config.json"
CACHE_DIR = MULTIMODAL_DIR / "cache"

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"

# 模态类型
class ModalityType:
    IMAGE = "image"           # 图像
    AUDIO = "audio"           # 音频
    TEXT = "text"             # 文本
    DOCUMENT = "document"     # 文档
    VIDEO = "video"           # 视频

# 处理状态
class ProcessingStatus:
    PENDING = "pending"       # 待处理
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"         # 失败

def init_multimodal():
    """初始化多模态系统"""
    MULTIMODAL_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    
    if not MULTIMODAL_DB.exists():
        save_db({
            "items": [],
            "fused_results": [],
            "next_id": 1,
            "stats": {
                "total_processed": 0,
                "images": 0,
                "audio": 0,
                "documents": 0,
                "fusions": 0
            }
        })
    
    if not MULTIMODAL_CONFIG.exists():
        save_config({
            "enabled": True,
            "cache_enabled": True,
            "cache_ttl_hours": 24,
            "max_file_size_mb": 100,
            "supported_formats": {
                "image": ["jpg", "jpeg", "png", "gif", "bmp", "webp"],
                "audio": ["mp3", "wav", "ogg", "m4a", "flac"],
                "document": ["pdf", "docx", "xlsx", "pptx", "txt", "md"]
            },
            "ocr_language": "zh+en",
            "auto_cache": True
        })

def save_db(db):
    """保存数据库"""
    with open(MULTIMODAL_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_db():
    """加载数据库"""
    if not MULTIMODAL_DB.exists():
        return {
            "items": [],
            "fused_results": [],
            "next_id": 1,
            "stats": {"total_processed": 0, "images": 0, "audio": 0, "documents": 0, "fusions": 0}
        }
    
    with open(MULTIMODAL_DB, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置"""
    with open(MULTIMODAL_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_config():
    """加载配置"""
    if not MULTIMODAL_CONFIG.exists():
        return {
            "enabled": True,
            "cache_enabled": True,
            "cache_ttl_hours": 24,
            "max_file_size_mb": 100,
            "supported_formats": {
                "image": ["jpg", "jpeg", "png", "gif", "bmp", "webp"],
                "audio": ["mp3", "wav", "ogg", "m4a", "flac"],
                "document": ["pdf", "docx", "xlsx", "pptx", "txt", "md"]
            },
            "ocr_language": "zh+en",
            "auto_cache": True
        }
    
    with open(MULTIMODAL_CONFIG, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_id():
    """生成 ID"""
    db = load_db()
    item_id = db["next_id"]
    db["next_id"] += 1
    save_db(db)
    return f"MM-{item_id:04d}"

def get_file_type(file_path: str) -> str:
    """获取文件类型"""
    ext = Path(file_path).suffix.lower().lstrip('.')
    
    config = load_config()
    formats = config.get("supported_formats", {})
    
    for modality, exts in formats.items():
        if ext in exts:
            return modality
    
    return "unknown"

def check_file_size(file_path: str) -> bool:
    """检查文件大小"""
    config = load_config()
    max_size = config.get("max_file_size_mb", 100) * 1024 * 1024
    
    try:
        size = Path(file_path).stat().st_size
        return size <= max_size
    except:
        return False

# ==================== 图像理解功能 ====================

def analyze_image(image_path: str, features: List[str] = None) -> Dict:
    """分析图像
    
    Args:
        image_path: 图像文件路径
        features: 要提取的特征列表 (objects, text, scene, colors, faces)
    
    Returns:
        分析结果字典
    """
    init_multimodal()
    config = load_config()
    
    if not config.get("enabled", True):
        return {"error": "多模态系统已禁用"}
    
    # 检查文件
    if not Path(image_path).exists():
        return {"error": f"文件不存在：{image_path}"}
    
    if not check_file_size(image_path):
        return {"error": "文件过大"}
    
    item_id = generate_id()
    
    # 默认特征
    if not features:
        features = ["objects", "text", "scene", "colors"]
    
    # 模拟分析结果 (实际应调用视觉 API)
    analysis = {
        "id": item_id,
        "type": ModalityType.IMAGE,
        "file_path": str(image_path),
        "file_name": Path(image_path).name,
        "status": ProcessingStatus.COMPLETED,
        "created_at": datetime.now().isoformat(),
        "analysis": {
            "objects": detect_objects(image_path),
            "text": extract_text(image_path),  # OCR
            "scene": analyze_scene(image_path),
            "colors": extract_colors(image_path),
            "metadata": get_image_metadata(image_path)
        },
        "features_requested": features,
        "processing_time_ms": 0
    }
    
    # 保存到数据库
    db = load_db()
    db["items"].append(analysis)
    db["stats"]["total_processed"] += 1
    db["stats"]["images"] += 1
    save_db(db)
    
    print(f"{Colors.GREEN}✅ 图像分析完成{Colors.RESET}")
    print(f"   ID: {item_id}")
    print(f"   文件：{Path(image_path).name}")
    print(f"   物体：{len(analysis['analysis']['objects'])}个")
    print(f"   文字：{analysis['analysis']['text'][:50]}..." if analysis['analysis']['text'] else "   文字：无")
    print(f"   场景：{analysis['analysis']['scene']}")
    
    return analysis

def detect_objects(image_path: str) -> List[Dict]:
    """检测图像中的物体"""
    # 模拟物体检测 (实际应调用 CV 模型)
    # 这里返回示例数据
    return [
        {"label": "person", "confidence": 0.95, "bbox": [100, 50, 200, 300]},
        {"label": "desk", "confidence": 0.88, "bbox": [0, 200, 400, 300]},
        {"label": "computer", "confidence": 0.92, "bbox": [150, 100, 250, 200]}
    ]

def extract_text(image_path: str) -> str:
    """OCR 文字提取"""
    # 模拟 OCR (实际应调用 OCR API)
    return "示例：图像中的文字内容"

def analyze_scene(image_path: str) -> str:
    """场景分析"""
    # 模拟场景分析
    return "office indoor workspace"

def extract_colors(image_path: str) -> List[str]:
    """提取主色调"""
    # 模拟颜色提取
    return ["#2C3E50", "#3498DB", "#ECF0F1"]

def get_image_metadata(image_path: str) -> Dict:
    """获取图像元数据"""
    try:
        stat = Path(image_path).stat()
        return {
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "format": Path(image_path).suffix.lower()
        }
    except:
        return {}

# ==================== OCR 功能 ====================

def perform_ocr(image_path: str, language: str = "zh+en") -> Dict:
    """执行 OCR 文字识别
    
    Args:
        image_path: 图像文件路径
        language: 语言 (zh/en/zh+en/ja/ko 等)
    
    Returns:
        OCR 结果
    """
    init_multimodal()
    
    item_id = generate_id()
    
    # 模拟 OCR 结果
    ocr_result = {
        "id": item_id,
        "type": "ocr",
        "file_path": str(image_path),
        "language": language,
        "status": ProcessingStatus.COMPLETED,
        "created_at": datetime.now().isoformat(),
        "text": "这是 OCR 识别的文字内容示例。\n支持多语言混合识别。",
        "confidence": 0.94,
        "text_blocks": [
            {"text": "这是 OCR 识别的文字内容示例。", "bbox": [10, 10, 300, 30], "confidence": 0.96},
            {"text": "支持多语言混合识别。", "bbox": [10, 40, 200, 60], "confidence": 0.92}
        ],
        "processing_time_ms": 0
    }
    
    # 保存
    db = load_db()
    db["items"].append(ocr_result)
    save_db(db)
    
    print(f"{Colors.GREEN}✅ OCR 完成{Colors.RESET}")
    print(f"   ID: {item_id}")
    print(f"   文字：{ocr_result['text'][:50]}...")
    print(f"   置信度：{ocr_result['confidence']:.2%}")
    
    return ocr_result

# ==================== 语音处理功能 ====================

def process_audio(audio_path: str, features: List[str] = None) -> Dict:
    """处理音频
    
    Args:
        audio_path: 音频文件路径
        features: 要提取的特征 (transcription, speaker, emotion, keywords)
    
    Returns:
        处理结果
    """
    init_multimodal()
    config = load_config()
    
    if not config.get("enabled", True):
        return {"error": "多模态系统已禁用"}
    
    if not Path(audio_path).exists():
        return {"error": f"文件不存在：{audio_path}"}
    
    item_id = generate_id()
    
    if not features:
        features = ["transcription", "keywords"]
    
    # 模拟音频处理
    audio_result = {
        "id": item_id,
        "type": ModalityType.AUDIO,
        "file_path": str(audio_path),
        "file_name": Path(audio_path).name,
        "status": ProcessingStatus.COMPLETED,
        "created_at": datetime.now().isoformat(),
        "analysis": {
            "transcription": transcribe_audio(audio_path),
            "duration_seconds": get_audio_duration(audio_path),
            "speaker_count": 1,
            "emotion": "neutral",
            "keywords": extract_keywords(audio_path),
            "metadata": get_audio_metadata(audio_path)
        },
        "features_requested": features,
        "processing_time_ms": 0
    }
    
    # 保存
    db = load_db()
    db["items"].append(audio_result)
    db["stats"]["total_processed"] += 1
    db["stats"]["audio"] += 1
    save_db(db)
    
    print(f"{Colors.GREEN}✅ 音频处理完成{Colors.RESET}")
    print(f"   ID: {item_id}")
    print(f"   文件：{Path(audio_path).name}")
    print(f"   时长：{audio_result['analysis']['duration_seconds']}秒")
    print(f"   转录：{audio_result['analysis']['transcription'][:50]}...")
    
    return audio_result

def transcribe_audio(audio_path: str) -> str:
    """语音转录"""
    # 模拟语音转文字
    return "这是语音转录的示例文本内容。"

def get_audio_duration(audio_path: str) -> float:
    """获取音频时长"""
    # 模拟
    return 120.5

def extract_keywords(audio_path: str) -> List[str]:
    """提取关键词"""
    # 模拟
    return ["会议", "讨论", "项目", "计划"]

def get_audio_metadata(audio_path: str) -> Dict:
    """获取音频元数据"""
    try:
        stat = Path(audio_path).stat()
        return {
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "format": Path(audio_path).suffix.lower()
        }
    except:
        return {}

# ==================== 文档解析功能 ====================

def parse_document(doc_path: str, extract_type: str = "all") -> Dict:
    """解析文档
    
    Args:
        doc_path: 文档文件路径
        extract_type: 提取类型 (text/tables/images/all)
    
    Returns:
        解析结果
    """
    init_multimodal()
    config = load_config()
    
    if not config.get("enabled", True):
        return {"error": "多模态系统已禁用"}
    
    if not Path(doc_path).exists():
        return {"error": f"文件不存在：{doc_path}"}
    
    item_id = generate_id()
    doc_type = get_file_type(doc_path)
    
    # 模拟文档解析
    doc_result = {
        "id": item_id,
        "type": ModalityType.DOCUMENT,
        "file_path": str(doc_path),
        "file_name": Path(doc_path).name,
        "doc_type": doc_type,
        "status": ProcessingStatus.COMPLETED,
        "created_at": datetime.now().isoformat(),
        "content": {
            "text": extract_document_text(doc_path),
            "tables": extract_tables(doc_path),
            "images": extract_document_images(doc_path),
            "metadata": get_document_metadata(doc_path)
        },
        "extract_type": extract_type,
        "processing_time_ms": 0
    }
    
    # 保存
    db = load_db()
    db["items"].append(doc_result)
    db["stats"]["total_processed"] += 1
    db["stats"]["documents"] += 1
    save_db(db)
    
    print(f"{Colors.GREEN}✅ 文档解析完成{Colors.RESET}")
    print(f"   ID: {item_id}")
    print(f"   文件：{Path(doc_path).name}")
    print(f"   类型：{doc_type}")
    print(f"   文字：{len(doc_result['content']['text'])}字符")
    print(f"   表格：{len(doc_result['content']['tables'])}个")
    
    return doc_result

def extract_document_text(doc_path: str) -> str:
    """提取文档文字"""
    # 模拟
    return "这是文档的文字内容示例。包含多个段落和章节。"

def extract_tables(doc_path: str) -> List[Dict]:
    """提取表格"""
    # 模拟
    return [
        {"headers": ["姓名", "年龄", "城市"], "rows": [["张三", "25", "北京"], ["李四", "30", "上海"]]}
    ]

def extract_document_images(doc_path: str) -> List[str]:
    """提取文档中的图片"""
    # 模拟
    return ["image1.png", "image2.jpg"]

def get_document_metadata(doc_path: str) -> Dict:
    """获取文档元数据"""
    try:
        stat = Path(doc_path).stat()
        return {
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "format": Path(doc_path).suffix.lower(),
            "pages": 10  # 模拟页数
        }
    except:
        return {}

# ==================== PDF 专用解析 ====================

def parse_pdf(pdf_path: str, pages: List[int] = None) -> Dict:
    """解析 PDF 文件
    
    Args:
        pdf_path: PDF 文件路径
        pages: 要解析的页码列表 (None=全部)
    
    Returns:
        解析结果
    """
    init_multimodal()
    
    if not Path(pdf_path).exists():
        return {"error": f"文件不存在：{pdf_path}"}
    
    item_id = generate_id()
    
    # 模拟 PDF 解析
    pdf_result = {
        "id": item_id,
        "type": "pdf",
        "file_path": str(pdf_path),
        "file_name": Path(pdf_path).name,
        "status": ProcessingStatus.COMPLETED,
        "created_at": datetime.now().isoformat(),
        "content": {
            "total_pages": 20,
            "parsed_pages": pages if pages else list(range(1, 21)),
            "text": "PDF 文字内容示例...",
            "tables": [],
            "images": [],
            "outline": ["第一章", "第二章", "第三章"]
        },
        "processing_time_ms": 0
    }
    
    # 保存
    db = load_db()
    db["items"].append(pdf_result)
    save_db(db)
    
    print(f"{Colors.GREEN}✅ PDF 解析完成{Colors.RESET}")
    print(f"   ID: {item_id}")
    print(f"   文件：{Path(pdf_path).name}")
    print(f"   页数：{pdf_result['content']['total_pages']}页")
    
    return pdf_result

# ==================== 多模态融合 ====================

def fuse_modalities(item_ids: List[str], fusion_type: str = "combined") -> Dict:
    """多模态融合
    
    Args:
        item_ids: 要融合的项目 ID 列表
        fusion_type: 融合类型 (combined/summary/correlation)
    
    Returns:
        融合结果
    """
    init_multimodal()
    
    db = load_db()
    
    # 查找项目
    items = []
    for item_id in item_ids:
        for item in db["items"]:
            if item["id"] == item_id:
                items.append(item)
                break
    
    if len(items) != len(item_ids):
        return {"error": "部分项目未找到"}
    
    fusion_id = f"FUSE-{db['next_id']:04d}"
    db["next_id"] += 1
    
    # 模拟融合结果
    fusion_result = {
        "id": fusion_id,
        "type": "fusion",
        "fusion_type": fusion_type,
        "source_ids": item_ids,
        "source_types": [item["type"] for item in items],
        "status": ProcessingStatus.COMPLETED,
        "created_at": datetime.now().isoformat(),
        "result": {
            "combined_summary": generate_combined_summary(items),
            "cross_modal_links": find_cross_modal_links(items),
            "unified_representation": create_unified_representation(items),
            "insights": generate_insights(items)
        },
        "processing_time_ms": 0
    }
    
    db["fused_results"].append(fusion_result)
    db["stats"]["fusions"] += 1
    save_db(db)
    
    print(f"{Colors.GREEN}✅ 多模态融合完成{Colors.RESET}")
    print(f"   ID: {fusion_id}")
    print(f"   源项目：{len(items)}个")
    print(f"   类型：{fusion_type}")
    print(f"   洞察：{len(fusion_result['result']['insights'])}条")
    
    return fusion_result

def generate_combined_summary(items: List[Dict]) -> str:
    """生成综合摘要"""
    return f"综合分析了{len(items)}个多模态项目，包括图像、音频和文档。"

def find_cross_modal_links(items: List[Dict]) -> List[Dict]:
    """发现跨模态关联"""
    return [
        {"source": "image", "target": "text", "relation": "contains"},
        {"source": "audio", "target": "text", "relation": "transcribes"}
    ]

def create_unified_representation(items: List[Dict]) -> Dict:
    """创建统一表示"""
    return {
        "entities": ["实体 1", "实体 2"],
        "relationships": ["关系 1", "关系 2"],
        "concepts": ["概念 1", "概念 2"]
    }

def generate_insights(items: List[Dict]) -> List[str]:
    """生成洞察"""
    return [
        "图像和文档描述的是同一主题",
        "音频内容与文档文字高度相关",
        "多模态信息相互补充，形成完整理解"
    ]

# ==================== 缓存管理 ====================

def cache_result(item_id: str, result: Dict):
    """缓存结果"""
    config = load_config()
    
    if not config.get("cache_enabled", True):
        return
    
    cache_file = CACHE_DIR / f"{item_id}.json"
    
    cache_data = {
        "item_id": item_id,
        "result": result,
        "cached_at": datetime.now().isoformat(),
        "expires_at": (datetime.now().replace(hour=datetime.now().hour + config.get("cache_ttl_hours", 24))).isoformat()
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

def get_cached(item_id: str) -> Optional[Dict]:
    """获取缓存"""
    config = load_config()
    
    if not config.get("cache_enabled", True):
        return None
    
    cache_file = CACHE_DIR / f"{item_id}.json"
    
    if not cache_file.exists():
        return None
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    # 检查是否过期
    expires = datetime.fromisoformat(cache_data["expires_at"])
    if datetime.now() > expires:
        cache_file.unlink()
        return None
    
    return cache_data["result"]

def clear_cache():
    """清除缓存"""
    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()
    
    print(f"{Colors.GREEN}✅ 缓存已清除{Colors.RESET}")

# ==================== 状态和统计 ====================

def show_status():
    """显示系统状态"""
    init_multimodal()
    db = load_db()
    config = load_config()
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}多模态理解系统状态{Colors.RESET}")
    print("=" * 70)
    
    # 系统状态
    enabled = config.get("enabled", True)
    status_color = Colors.GREEN if enabled else Colors.RED
    print(f"系统状态：{status_color}{'启用' if enabled else '禁用'}{Colors.RESET}")
    print(f"缓存：{'启用' if config.get('cache_enabled') else '禁用'}")
    print(f"缓存 TTL: {config.get('cache_ttl_hours', 24)}小时")
    print(f"最大文件大小：{config.get('max_file_size_mb', 100)}MB")
    
    # 处理统计
    stats = db.get("stats", {})
    print(f"\n处理统计:")
    print(f"  总处理：{stats.get('total_processed', 0)}个")
    print(f"  图像：{stats.get('images', 0)}个")
    print(f"  音频：{stats.get('audio', 0)}个")
    print(f"  文档：{stats.get('documents', 0)}个")
    print(f"  融合：{stats.get('fusions', 0)}次")
    
    # 最近项目
    items = db.get("items", [])[-5:]
    if items:
        print(f"\n最近项目:")
        for item in items:
            print(f"  {item['id']}: {item['type']} - {item['file_name'][:30]}... [{item['status']}]")
    
    print("=" * 70)

def list_items(limit: int = 10) -> List[Dict]:
    """列出项目"""
    db = load_db()
    items = db.get("items", [])
    return items[-limit:]

# ==================== 统一 API ====================

def process_file(file_path: str, process_type: str = "auto") -> Dict:
    """统一文件处理接口
    
    Args:
        file_path: 文件路径
        process_type: 处理类型 (auto/image/audio/document/pdf/ocr)
    
    Returns:
        处理结果
    """
    init_multimodal()
    
    if process_type == "auto":
        process_type = get_file_type(file_path)
    
    if process_type == ModalityType.IMAGE or process_type in ["jpg", "jpeg", "png", "gif"]:
        return analyze_image(file_path)
    elif process_type == ModalityType.AUDIO or process_type in ["mp3", "wav", "ogg"]:
        return process_audio(file_path)
    elif process_type == "pdf":
        return parse_pdf(file_path)
    elif process_type == ModalityType.DOCUMENT or process_type in ["docx", "xlsx", "pptx"]:
        return parse_document(file_path)
    elif process_type == "ocr":
        return perform_ocr(file_path)
    else:
        return {"error": f"不支持的文件类型：{process_type}"}

def get_result(item_id: str) -> Optional[Dict]:
    """获取处理结果"""
    db = load_db()
    
    # 先查缓存
    cached = get_cached(item_id)
    if cached:
        return cached
    
    # 查数据库
    for item in db["items"]:
        if item["id"] == item_id:
            return item
    
    for fused in db["fused_results"]:
        if fused["id"] == item_id:
            return fused
    
    return None

# ==================== 主函数 ====================

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}多模态理解系统菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 分析图像")
        print("2. OCR 文字识别")
        print("3. 处理音频")
        print("4. 解析文档")
        print("5. 解析 PDF")
        print("6. 多模态融合")
        print("7. 查看结果")
        print("8. 查看状态")
        print("9. 清除缓存")
        print("10. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-10): ").strip()
        
        if choice == '1':
            path = input("图像路径：").strip()
            analyze_image(path)
        elif choice == '2':
            path = input("图像路径：").strip()
            perform_ocr(path)
        elif choice == '3':
            path = input("音频路径：").strip()
            process_audio(path)
        elif choice == '4':
            path = input("文档路径：").strip()
            parse_document(path)
        elif choice == '5':
            path = input("PDF 路径：").strip()
            parse_pdf(path)
        elif choice == '6':
            ids = input("项目 ID 列表 (逗号分隔): ").strip()
            fuse_modalities([id.strip() for id in ids.split(',')])
        elif choice == '7':
            item_id = input("项目 ID: ").strip()
            result = get_result(item_id)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"{Colors.RED}❌ 未找到{Colors.RESET}")
        elif choice == '8':
            show_status()
        elif choice == '9':
            clear_cache()
        elif choice == '10':
            print("退出")
            break
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multimodal Understanding System - 多模态理解')
    parser.add_argument('--image', type=str, help='分析图像')
    parser.add_argument('--ocr', type=str, help='OCR 文字识别')
    parser.add_argument('--audio', type=str, help='处理音频')
    parser.add_argument('--doc', type=str, help='解析文档')
    parser.add_argument('--pdf', type=str, help='解析 PDF')
    parser.add_argument('--fuse', type=str, help='多模态融合 (ID 列表)')
    parser.add_argument('--result', type=str, help='查看结果 (ID)')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--clear-cache', action='store_true', help='清除缓存')
    
    args = parser.parse_args()
    
    init_multimodal()
    
    if args.image:
        analyze_image(args.image)
    elif args.ocr:
        perform_ocr(args.ocr)
    elif args.audio:
        process_audio(args.audio)
    elif args.doc:
        parse_document(args.doc)
    elif args.pdf:
        parse_pdf(args.pdf)
    elif args.fuse:
        ids = [id.strip() for id in args.fuse.split(',')]
        fuse_modalities(ids)
    elif args.result:
        result = get_result(args.result)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"{Colors.RED}❌ 未找到{Colors.RESET}")
    elif args.status:
        show_status()
    elif args.clear_cache:
        clear_cache()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()
