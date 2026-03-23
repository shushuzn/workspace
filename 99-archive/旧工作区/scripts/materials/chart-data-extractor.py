#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Data Extractor - 图表数据提取器

功能：
1. 从论文 PDF 中提取图表区域
2. 使用 OCR 提取坐标轴标签和数值
3. 解析曲线数据点
4. 支持常见图表类型 (折线图、柱状图、散点图)

作者：Claw (AI Research OS)
创建时间：2026-03-05 22:15
"""

import re
import json
import base64
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


# ============================================================================
# 1. 数据结构定义
# ============================================================================

@dataclass
class ChartDataPoint:
    """图表数据点"""
    x: float
    y: float
    series: Optional[str] = None  # 系列名称 (如多条曲线)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ChartMetadata:
    """图表元数据"""
    chart_type: str  # line/bar/scatter
    title: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    x_axis_unit: Optional[str] = None
    y_axis_unit: Optional[str] = None
    x_range: Optional[Tuple[float, float]] = None
    y_range: Optional[Tuple[float, float]] = None
    num_series: int = 1
    series_names: Optional[List[str]] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ExtractedChartData:
    """提取的图表数据"""
    figure_id: str  # 图编号 (如 "Figure 1")
    page_number: int
    metadata: ChartMetadata
    data_points: List[List[ChartDataPoint]]  # 多个系列
    source_image: Optional[str] = None  # Base64 编码的图表图片
    confidence: float = 0.0  # 提取置信度

    def to_dict(self) -> Dict:
        return {
            'figure_id': self.figure_id,
            'page_number': self.page_number,
            'metadata': self.metadata.to_dict(),
            'data_points': [[dp.to_dict() for dp in series] for series in self.data_points],
            'confidence': self.confidence
        }


# ============================================================================
# 2. 图表检测器
# ============================================================================

class ChartDetector:
    """图表检测器 - 识别论文中的图表"""

    # 图表标题模式
    FIGURE_PATTERNS = [
        r'[Ff]igure\s*(\d+[A-Za-z]?)[:\.\s]+(.+?)(?=\n|$)',
        r'[Ff]ig\.\s*(\d+[A-Za-z]?)[:\.\s]+(.+?)(?=\n|$)',
        r'[图图]\s*(\d+[A-Za-z]?)[：:\.\s]+(.+?)(?=\n|$)',
    ]

    # 图表类型关键词
    CHART_TYPE_KEYWORDS = {
        'line': ['plot', 'curve', 'trend', 'vs', 'dependence', 'relationship'],
        'bar': ['bar', 'histogram', 'distribution', 'comparison'],
        'scatter': ['scatter', 'correlation', 'data points'],
        'pie': ['pie', 'percentage', 'composition'],
    }

    def detect_chart_type(self, caption: str) -> str:
        """从标题检测图表类型"""
        caption_lower = caption.lower()

        for chart_type, keywords in self.CHART_TYPE_KEYWORDS.items():
            if any(kw in caption_lower for kw in keywords):
                return chart_type

        # 默认返回折线图
        return 'line'

    def extract_figure_captions(self, text: str) -> List[Tuple[str, str, int]]:
        """从文本中提取图表标题"""
        figures = []

        for pattern in self.FIGURE_PATTERNS:
            for match in re.finditer(pattern, text, re.MULTILINE):
                figure_id = match.group(1)
                caption = match.group(2).strip()

                # 估算页码 (每 500 行约 1 页)
                line_num = text[:match.start()].count('\n')
                page_num = (line_num // 500) + 1

                figures.append((figure_id, caption, page_num))

        return figures


# ============================================================================
# 3. 坐标轴解析器
# ============================================================================

class AxisParser:
    """坐标轴解析器 - 提取坐标轴信息"""

    # 轴标签模式
    AXIS_LABEL_PATTERNS = [
        r'([A-Za-z\s]+)\s*\(\s*([A-Za-z0-9/·]+)\s*\)',  # "Wavelength (nm)"
        r'([A-Za-z\s]+)\s*[/\s]\s*([A-Za-z0-9]+)',  # "Energy / eV"
        r'([A-Za-z\s]+)\s*:',  # "Temperature:"
    ]

    # 数值范围模式
    RANGE_PATTERNS = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)',  # "100-200"
        r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)',  # "100 to 200"
    ]

    def parse_axis_label(self, label: str) -> Tuple[Optional[str], Optional[str]]:
        """解析轴标签，返回 (名称，单位)"""
        for pattern in self.AXIS_LABEL_PATTERNS:
            match = re.search(pattern, label)
            if match:
                name = match.group(1).strip()
                unit = match.group(2).strip() if len(match.groups()) > 1 else None
                return name, unit

        return label.strip(), None

    def parse_tick_labels(self, text: str) -> List[float]:
        """从 OCR 文本中提取刻度标签"""
        numbers = []

        # 匹配数字 (包括科学计数法)
        pattern = r'(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'

        for match in re.finditer(pattern, text):
            try:
                num = float(match.group(1))
                numbers.append(num)
            except ValueError:
                continue

        return sorted(set(numbers))

    def infer_scale(self, tick_labels: List[float]) -> str:
        """推断坐标轴刻度类型"""
        if len(tick_labels) < 2:
            return 'unknown'

        # 检查是否等间距
        diffs = [tick_labels[i +1] - tick_labels[i] for i in range(len(tick_labels) -1)]
        avg_diff = sum(diffs) / len(diffs)

        if all(abs(d - avg_diff) / avg_diff < 0.1 for d in diffs if avg_diff > 0):
            return 'linear'

        # 检查是否对数刻度
        ratios = [tick_labels[i +1] / tick_labels[i] for i in range(len(tick_labels) -1) if tick_labels[i] > 0]
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            if all(abs(r / avg_ratio - 1) < 0.1 for r in ratios if avg_ratio > 0):
                return 'logarithmic'

        return 'unknown'


# ============================================================================
# 4. 曲线数据提取器
# ============================================================================

class CurveExtractor:
    """曲线数据提取器 - 从图表中提取数据点"""

    def __init__(self):
        self.axis_parser = AxisParser()

    def extract_from_coordinates(
        self,
        pixel_coordinates: List[Tuple[int, int]],
        x_range: Tuple[float, float],
        y_range: Tuple[float, float],
        image_width: int,
        image_height: int,
        plot_area: Tuple[int, int, int, int]  # (x_min, y_min, x_max, y_max) 像素
    ) -> List[ChartDataPoint]:
        """
        从像素坐标转换为数据坐标
        
        Args:
            pixel_coordinates: 像素坐标列表 [(x, y), ...]
            x_range: X 轴数据范围 (min, max)
            y_range: Y 轴数据范围 (min, max)
            image_width: 图像宽度 (像素)
            image_height: 图像高度 (像素)
            plot_area: 绘图区域 (左，下，右，上) 像素坐标
        
        Returns:
            数据点列表
        """
        data_points = []

        x_min_px, y_min_px, x_max_px, y_max_px = plot_area

        # 计算像素到数据的映射
        x_scale = (x_range[1] - x_range[0]) / (x_max_px - x_min_px)
        y_scale = (y_range[1] - y_range[0]) / (y_max_px - y_min_px)

        for px_x, px_y in pixel_coordinates:
            # 检查点是否在绘图区域内
            if not (x_min_px <= px_x <= x_max_px and y_min_px <= px_y <= y_max_px):
                continue

            # 转换为数据坐标
            data_x = x_range[0] + (px_x - x_min_px) * x_scale
            data_y = y_range[0] + (y_max_px - px_y) * y_scale  # Y 轴翻转

            data_points.append(ChartDataPoint(
                x=round(data_x, 4),
                y=round(data_y, 4)
            ))

        return data_points

    def detect_curves_by_color(
        self,
        image_data: bytes,
        num_curves: int = 1
    ) -> List[List[Tuple[int, int]]]:
        """
        按颜色检测曲线 (需要图像处理库)
        
        TODO: 集成 OpenCV/PIL 实现颜色分割和曲线追踪
        当前返回空列表，需要实际图像处理实现
        """
        # 这是一个占位实现
        # 实际使用需要：
        # 1. 使用 PIL/OpenCV 加载图像
        # 2. 转换为 HSV 色彩空间
        # 3. 颜色分割提取不同曲线
        # 4. 骨架化获取曲线像素坐标

        print("  [提示] 曲线颜色检测需要安装 OpenCV/PIL")
        print("  安装：pip install opencv-python pillow")

        return []


# ============================================================================
# 5. 图表数据提取器 (主类)
# ============================================================================

class ChartDataExtractor:
    """图表数据提取器 - 整合所有功能"""

    def __init__(self):
        self.detector = ChartDetector()
        self.axis_parser = AxisParser()
        self.curve_extractor = CurveExtractor()

    def extract_from_pdf(
        self,
        pdf_path: str,
        figure_ids: Optional[List[str]] = None
    ) -> List[ExtractedChartData]:
        """
        从 PDF 中提取图表数据
        
        Args:
            pdf_path: PDF 文件路径
            figure_ids: 要提取的图编号列表 (如 ["1", "2a"])，None 表示全部
        
        Returns:
            提取的图表数据列表
        """
        print(f"\n[图表提取] 处理 PDF: {pdf_path}")

        # TODO: 实现完整的 PDF 处理流程
        # 1. 使用 PyMuPDF/pdfplumber 提取文本和图片
        # 2. 检测图表位置和标题
        # 3. 提取图表区域
        # 4. OCR 识别坐标轴
        # 5. 曲线追踪和数据点提取

        print("  [提示] 完整 PDF 图表提取需要安装:")
        print("  - PyMuPDF (fitz): pip install pymupdf")
        print("  - pdfplumber: pip install pdfplumber")
        print("  - pytesseract: pip install pytesseract")
        print("  - Tesseract OCR: https://github.com/tesseract-ocr/tesseract")

        return []

    def extract_from_coordinates(
        self,
        figure_id: str,
        page_number: int,
        pixel_data: List[Tuple[int, int]],
        x_range: Tuple[float, float],
        y_range: Tuple[float, float],
        x_label: str = "",
        y_label: str = "",
        image_dimensions: Tuple[int, int] = (800, 600),
        plot_area: Tuple[int, int, int, int] = (100, 50, 700, 500)
    ) -> ExtractedChartData:
        """
        从已知的像素坐标提取数据
        
        适用于：
        1. 手动标注的图表
        2. 其他工具提取的像素坐标
        """
        # 解析轴标签
        x_name, x_unit = self.axis_parser.parse_axis_label(x_label)
        y_name, y_unit = self.axis_parser.parse_axis_label(y_label)

        # 提取数据点
        data_points = self.curve_extractor.extract_from_coordinates(
            pixel_coordinates=pixel_data,
            x_range=x_range,
            y_range=y_range,
            image_width=image_dimensions[0],
            image_height=image_dimensions[1],
            plot_area=plot_area
        )

        # 创建元数据
        metadata = ChartMetadata(
            chart_type='line',
            x_axis_label=x_name,
            y_axis_label=y_name,
            x_axis_unit=x_unit,
            y_axis_unit=y_unit,
            x_range=x_range,
            y_range=y_range,
            num_series=1
        )

        return ExtractedChartData(
            figure_id=figure_id,
            page_number=page_number,
            metadata=metadata,
            data_points=[data_points],  # 单系列
            confidence=0.85  # 假设置信度
        )

    def manual_digitize(self, figure_id: str) -> Dict:
        """
        生成交互式数字化模板
        
        用户可以手动点击图表上的数据点
        """
        template = {
            'figure_id': figure_id,
            'instructions': [
                '1. 打开图表图片',
                '2. 标注坐标轴范围 (x_min, x_max, y_min, y_max)',
                '3. 点击曲线上的数据点',
                '4. 保存为 JSON'
            ],
            'data_points': []
        }

        return template


# ============================================================================
# 6. Web 图表提取 (Plotly/Chart.js)
# ============================================================================

class WebChartExtractor:
    """Web 图表数据提取器"""

    @staticmethod
    def extract_plotly_data(json_data: Dict) -> List[ChartDataPoint]:
        """从 Plotly JSON 中提取数据"""
        data_points = []

        for trace in json_data.get('data', []):
            x_values = trace.get('x', [])
            y_values = trace.get('y', [])

            for x, y in zip(x_values, y_values):
                data_points.append(ChartDataPoint(x=float(x), y=float(y)))

        return data_points

    @staticmethod
    def extract_chartjs_data(json_data: Dict) -> List[ChartDataPoint]:
        """从 Chart.js JSON 中提取数据"""
        data_points = []

        for dataset in json_data.get('datasets', []):
            data = dataset.get('data', [])
            labels = json_data.get('labels', [])

            for i, value in enumerate(data):
                x = labels[i] if i < len(labels) else i
                data_points.append(ChartDataPoint(x=float(i), y=float(value)))

        return data_points


# ============================================================================
# 7. 主函数
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Chart Data Extractor - 图表数据提取器")
    print("=" * 60)

    # 1. 创建提取器
    print("\n[1/4] 初始化提取器...")
    extractor = ChartDataExtractor()

    # 2. 测试坐标转换
    print("\n[2/4] 测试像素坐标转换...")

    # 模拟像素坐标 (一条直线)
    pixel_coords = [(200, 400), (300, 350), (400, 300), (500, 250), (600, 200)]

    chart_data = extractor.extract_from_coordinates(
        figure_id="Figure 1",
        page_number=3,
        pixel_data=pixel_coords,
        x_range=(0, 100),
        y_range=(0, 1000),
        x_label="Temperature (K)",
        y_label="Conductivity (S/m)",
        image_dimensions=(800, 600),
        plot_area=(100, 50, 700, 500)
    )

    print(f"  图表 ID: {chart_data.figure_id}")
    print(f"  X 轴：{chart_data.metadata.x_axis_label} ({chart_data.metadata.x_axis_unit})")
    print(f"  Y 轴：{chart_data.metadata.y_axis_label} ({chart_data.metadata.y_axis_unit})")
    print(f"  数据点：{len(chart_data.data_points[0])} 个")

    for i, point in enumerate(chart_data.data_points[0][:3]):
        print(f"    点{i +1}: ({point.x}, {point.y})")

    # 3. 测试图表检测
    print("\n[3/4] 测试图表标题检测...")

    sample_text = """
    Figure 1: Temperature dependence of electrical conductivity.
    The conductivity increases with temperature.
    
    Fig. 2: XRD patterns of the synthesized materials.
    
    图 3：不同掺杂浓度下的带隙变化。
    """

    detector = ChartDetector()
    figures = detector.extract_figure_captions(sample_text)

    for fig_id, caption, page in figures:
        chart_type = detector.detect_chart_type(caption)
        print(f"  Figure {fig_id} (第{page}页): {caption[:40]}... [{chart_type}]")

    # 4. 保存示例数据
    print("\n[4/4] 保存示例数据...")

    output_data = chart_data.to_dict()
    output_path = Path("data/chart-data-example.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  保存到：{output_path}")

    print("\n" + "=" * 60)
    print("图表数据提取器准备完成！")
    print("=" * 60)

    print("\n📌 下一步:")
    print("  1. 安装依赖：pip install pymupdf pdfplumber pytesseract opencv-python")
    print("  2. 安装 Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    print("  3. 实现 PDF 图表自动提取")
    print("  4. 或使用手动数字化工具提取数据点")


if __name__ == '__main__':
    main()
