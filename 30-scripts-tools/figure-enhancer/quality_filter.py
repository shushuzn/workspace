#!/usr/bin/env python3
# quality_filter.py - 图表质量过滤器
# 用法：py quality_filter.py <image_file> [--output <output_dir>]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
import cv2
import numpy as np
from pathlib import Path
import json

class QualityFilter:
    """图表质量过滤器"""

    def __init__(self, config=None):
        self.config = config or {
            'min_width': 200,
            'min_height': 200,
            'min_blur_score': 100,
            'min_contrast': 0.3,
            'max_compression_ratio': 0.1
        }

    def evaluate(self, image_path):
        """评估图像质量"""
        image = cv2.imread(str(image_path))
        if image is None:
            return {
                'pass': False,
                'reason': '无法读取图像',
                'metrics': {}
            }

        h, w = image.shape[:2]

        # 分辨率检查
        if w < self.config['min_width']:
            return {
                'pass': False,
                'reason': f'宽度不足',
                'metrics': {
                    'width': w,
                    'min_width': self.config['min_width']
                }
            }
        if h < self.config['min_height']:
            return {
                'pass': False,
                'reason': f'高度不足',
                'metrics': {
                    'height': h,
                    'min_height': self.config['min_height']
                }
            }

        # 模糊度检查 (Laplacian 方差)
        blur_score = self._calculate_blur(image)
        min_blur = self.config.get('min_blur_score', 100)
        if blur_score < min_blur:
            return {
                'pass': False,
                'reason': f'图像模糊',
                'metrics': {
                    'blur_score': blur_score,
                    'min_blur_score': min_blur
                }
            }

        # 对比度检查 (RMS)
        contrast = self._calculate_contrast(image)
        min_contrast = self.config.get('min_contrast', 0.3)
        if contrast < min_contrast:
            return {
                'pass': False,
                'reason': f'对比度低',
                'metrics': {
                    'contrast': contrast,
                    'min_contrast': min_contrast
                }
            }

        # 全部通过
        return {
            'pass': True,
            'reason': '质量达标',
            'metrics': {
                'resolution': f'{w}x{h}',
                'blur_score': f'{blur_score:.1f}',
                'contrast': f'{contrast:.3f}',
                'file_size': Path(image_path).stat().st_size / 1024  # KB
            }
        }

    def _calculate_blur(self, image):
        """计算模糊度 (Laplacian 方差)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def _calculate_contrast(self, image):
        """计算对比度 (RMS 对比度)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = np.sqrt(np.mean((gray - gray.mean())**2))
        return contrast / 255.0  # 归一化到 0-1

    def batch_evaluate(self, image_dir, output_file=None):
        """批量评估目录中的图像"""
        image_dir = Path(image_dir)
        results = []

        image_files = list(image_dir.glob('*.png')) + list(image_dir.glob('*.jpg'))

        print(f"📊 批量评估：{len(image_files)} 个图像")

        for i, img_file in enumerate(image_files):
            print(f"   [{i +1}/{len(image_files)}] {img_file.name}...", end="\r")
            result = self.evaluate(img_file)
            result['file'] = str(img_file)
            results.append(result)

        print(f"\n✅ 评估完成")

        # 统计
        passed = sum(1 for r in results if r['pass'])
        failed = len(results) - passed

        print(f"   通过：{passed} ({passed /len(results) *100:.1f}%)")
        print(f"   失败：{failed} ({failed /len(results) *100:.1f}%)")

        # 保存结果
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"📁 结果已保存：{output_path}")

        return results


def main():
    parser = argparse.ArgumentParser(description="图表质量过滤器")
    parser.add_argument("image_file", type=str, nargs='?', help="图像文件路径")
    parser.add_argument("--batch", "-b", type=str, help="批量评估目录")
    parser.add_argument("--output", "-o", type=str, help="输出文件 (批量模式)")
    parser.add_argument("--config", "-c", type=str, help="配置文件 (JSON)")

    args = parser.parse_args()

    # 加载配置
    config = None
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding='utf-8'))

    filter = QualityFilter(config)

    if args.batch:
        # 批量模式
        filter.batch_evaluate(args.batch, args.output)
    elif args.image_file:
        # 单文件模式
        image_path = Path(args.image_file)
        if not image_path.exists():
            print(f"❌ 文件不存在：{image_path}")
            sys.exit(1)

        result = filter.evaluate(image_path)

        print(f"📊 质量评估：{image_path.name}")
        print(f"   结果：{'✅ 通过' if result['pass'] else '❌ 失败'}")
        print(f"   原因：{result['reason']}")

        if result['metrics']:
            print(f"   指标:")
            for key, value in result['metrics'].items():
                print(f"     - {key}: {value}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
