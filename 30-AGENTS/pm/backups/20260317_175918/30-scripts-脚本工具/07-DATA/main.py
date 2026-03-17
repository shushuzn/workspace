#!/usr/bin/env python3
# main.py - OpenClaw API Server (FastAPI)
# 用法：uvicorn main:app --reload --host 0.0.0.0 --port 8000

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import time

# 创建应用
app = FastAPI(
    title="OpenClaw API",
    description="OpenClaw 研究工具 API - PDF 提取/图表增强/图谱渲染/每日简报",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============

class PDFExtractRequest(BaseModel):
    file_path: str = Field(..., description="PDF 文件路径")
    max_pages: int = Field(default=0, description="最大处理页数 (0=全部)")
    output_format: str = Field(default="markdown", description="输出格式 (markdown/json)")

class PDFExtractResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    processing_time: float

class FigureEnhanceRequest(BaseModel):
    image_path: str = Field(..., description="图像文件路径")
    output_path: Optional[str] = Field(default=None, description="输出路径")
    scale: int = Field(default=4, description="放大倍数 (2 或 4)")
    auto_enhance: bool = Field(default=True, description="自动增强")

class FigureEnhanceResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    processing_time: float

class BriefGenerateRequest(BaseModel):
    date: Optional[str] = Field(default=None, description="日期 (YYYY-MM-DD), 默认昨天")
    send: bool = Field(default=False, description="是否发送到 Feishu")

class BriefGenerateResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# ============ 健康检查 ============

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

# ============ PDF 提取 ============

@app.post("/api/v1/pdf/extract", response_model=PDFExtractResponse, tags=["PDF"])
async def extract_pdf(request: PDFExtractRequest):
    """
    提取 PDF 内容为 Markdown
    
    - **file_path**: PDF 文件路径
    - **max_pages**: 最大处理页数 (0=全部)
    - **output_format**: 输出格式 (markdown/json)
    """
    start_time = time.time()
    
    try:
        from pathlib import Path
        pdf_path = Path(request.file_path)
        
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在：{request.file_path}")
        
        # 调用 PDF 提取器
        import subprocess
        extractor_path = Path(__file__).parent.parent / "pdf-extractor" / "simple_pdf_extractor.py"
        
        cmd = [
            "py", str(extractor_path),
            str(pdf_path),
            "-m", str(request.max_pages) if request.max_pages > 0 else "0"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        processing_time = time.time() - start_time
        
        return PDFExtractResponse(
            success=True,
            data={
                "output": result.stdout[:10000] if result.stdout else "",  # 限制返回长度
                "pages_processed": request.max_pages if request.max_pages > 0 else "all"
            },
            message=f"PDF 提取完成 ({processing_time:.2f}s)",
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return PDFExtractResponse(
            success=False,
            message=f"提取失败：{str(e)}",
            processing_time=time.time() - start_time
        )

# ============ 图表增强 ============

@app.post("/api/v1/figure/enhance", response_model=FigureEnhanceResponse, tags=["Figure"])
async def enhance_figure(request: FigureEnhanceRequest):
    """
    增强图表质量 (质量过滤 + 超分辨率)
    
    - **image_path**: 图像文件路径
    - **output_path**: 输出路径 (可选)
    - **scale**: 放大倍数 (2 或 4)
    - **auto_enhance**: 自动增强
    """
    start_time = time.time()
    
    try:
        from pathlib import Path
        image_path = Path(request.image_path)
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在：{request.image_path}")
        
        # 调用质量过滤器
        import subprocess
        enhancer_path = Path(__file__).parent.parent / "figure-enhancer" / "quality_filter.py"
        
        cmd = ["py", str(enhancer_path), str(image_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        processing_time = time.time() - start_time
        
        stdout_text = result.stdout or ""
        return FigureEnhanceResponse(
            success=True,
            data={
                "quality_report": stdout_text,
                "recommendation": "建议增强" if "模糊" in stdout_text or "对比度低" in stdout_text else "质量良好"
            },
            message=f"质量评估完成 ({processing_time:.2f}s)",
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return FigureEnhanceResponse(
            success=False,
            message=f"评估失败：{str(e)}",
            processing_time=time.time() - start_time
        )

# ============ 每日简报 ============

@app.post("/api/v1/brief/generate", response_model=BriefGenerateResponse, tags=["Brief"])
async def generate_brief(request: BriefGenerateRequest):
    """
    生成每日简报
    
    - **date**: 日期 (YYYY-MM-DD), 默认昨天
    - **send**: 是否发送到 Feishu
    """
    start_time = time.time()
    
    try:
        import subprocess
        brief_path = Path(__file__).parent.parent / "daily-brief.py"
        
        cmd = ["py", str(brief_path)]
        
        if request.date:
            cmd.extend(["--date", request.date])
        
        if request.send:
            cmd.append("--send")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        processing_time = time.time() - start_time
        
        return BriefGenerateResponse(
            success=True,
            data={
                "log": result.stdout,
                "brief_date": request.date or "yesterday"
            },
            message=f"简报生成完成 ({processing_time:.2f}s)",
            processing_time=processing_time
        )
        
    except Exception as e:
        return BriefGenerateResponse(
            success=False,
            message=f"生成失败：{str(e)}",
            processing_time=time.time() - start_time
        )

# ============ 根路径 ============

@app.get("/", tags=["Root"])
async def root():
    """API 根路径 - 重定向到文档"""
    return {
        "message": "欢迎使用 OpenClaw API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# ============ 启动应用 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
