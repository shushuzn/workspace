#!/usr/bin/env python3
# figure_enhancer.py - 图表增强器 (质量过滤 + 超分辨率)
# 用法：py figure_enhancer.py <image_file> [--output <output_file>]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
from pathlib import Path
from datetime import datetime
import json

from quality_filter import QualityFilter
from super_resolution import SuperResolution

class FigureEnhancer:
    """图表增强器 - 质量过滤 + 超分辨率"""

    def __init__(self, config=None):
        self.quality_filter = QualityFilter(config)
        self.sr = None  # 延迟初始化

    def process(self, image_path, output_path=None, auto_enhance=True):
        """处理单个图像"""
        image_path = Path(image_path)

        print(f"📊 处理：{image_path.name}")
        print(f"   路径：{image_path}")

        # 步骤 1: 质量评估
        print("\n🔍 步骤 1/2: 质量评估")
        quality_result = self.quality_filter.evaluate(image_path)

        print(f"   结果：{'✅ 通过' if quality_result['pass'] else '❌ 失败'}")
        print(f"   原因：{quality_result['reason']}")

        if quality_result['metrics']:
            for key, value in quality_result['metrics'].items():
                print(f"   - {key}: {value}")

        # 如果质量达标且不需要自动增强，直接返回
        if quality_result['pass'] and not auto_enhance:
            print("\n✅ 质量达标，无需增强")
            return {
                'success': True,
                'enhanced': False,
                'quality': quality_result,
                'output': str(image_path)
            }

        # 步骤 2: 超分辨率增强
        print("\n🔍 步骤 2/2: 超分辨率增强")

        if self.sr is None:
            self.sr = SuperResolution(scale=4)

        if not output_path:
            output_path = image_path.parent / f"{image_path.stem}_enhanced.png"

        enhanced_image = self.sr.enhance(image_path, output_path)

        if enhanced_image is None:
            return {
                'success': False,
                'error': '超分辨率处理失败',
                'quality': quality_result
            }

        # 再次评估增强后的质量
        print("\n🔍 增强后质量评估:")
        enhanced_quality = self.quality_filter.evaluate(output_path)
        print(f"   结果：{'✅ 通过' if enhanced_quality['pass'] else '❌ 失败'}")

        return {
            'success': True,
            'enhanced': True,
            'quality_before': quality_result,
            'quality_after': enhanced_quality,
            'output': str(output_path)
        }

    def batch_process(self, image_dir, output_dir=None, auto_enhance=True):
        """批量处理目录中的图像"""
        image_dir = Path(image_dir)

        if output_dir is None:
            output_dir = image_dir.parent / f"{image_dir.name}_enhanced"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        image_files = list(image_dir.glob('*.png')) + list(image_dir.glob('*.jpg'))

        print(f"📊 批量处理：{len(image_files)} 个图像")
        print(f"   输入：{image_dir}")
        print(f"   输出：{output_dir}")

        results = []
        enhanced_count = 0
        skipped_count = 0

        for i, img_file in enumerate(image_files):
            print(f"\n[{i +1}/{len(image_files)}] {img_file.name}")

            output_file = output_dir / img_file.name
            result = self.process(img_file, output_file, auto_enhance)
            results.append(result)

            if result.get('enhanced'):
                enhanced_count += 1
            elif result.get('success') and not result.get('enhanced'):
                skipped_count += 1

        # 保存处理报告
        report_file = output_dir / "processing_report.json"
        report = {
            'timestamp': datetime.now().isoformat(),
            'input_dir': str(image_dir),
            'output_dir': str(output_dir),
            'total': len(image_files),
            'enhanced': enhanced_count,
            'skipped': skipped_count,
            'failed': len(image_files) - enhanced_count - skipped_count,
            'results': results
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n{'=' *60}")
        print(f"✅ 批量处理完成")
        print(f"   总数：{len(image_files)}")
        print(f"   增强：{enhanced_count}")
        print(f"   跳过：{skipped_count}")
        print(f"   失败：{len(image_files) - enhanced_count - skipped_count}")
        print(f"📁 报告：{report_file}")

        return results


def main():
    parser = argparse.ArgumentParser(description="图表增强器 (质量过滤 + 超分辨率)")
    parser.add_argument("image_file", type=str, nargs='?', help="图像文件路径")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径")
    parser.add_argument("--batch", "-b", type=str, help="批量处理目录")
    parser.add_argument("--output-dir", type=str, help="批量处理输出目录")
    parser.add_argument("--no-auto-enhance", action="store_true", help="禁用自动增强 (仅评估)")
    parser.add_argument("--config", "-c", type=str, help="配置文件 (JSON)")

    args = parser.parse_args()

    # 加载配置
    config = None
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding='utf-8'))

    enhancer = FigureEnhancer(config)

    if args.batch:
        # 批量模式
        enhancer.batch_process(args.batch, args.output_dir, not args.no_auto_enhance)
    elif args.image_file:
        # 单文件模式
        image_path = Path(args.image_file)
        if not image_path.exists():
            print(f"❌ 文件不存在：{image_path}")
            sys.exit(1)

        result = enhancer.process(image_path, args.output, not args.no_auto_enhance)

        print(f"\n{'=' *60}")
        if result['success']:
            if result.get('enhanced'):
                print(f"✅ 增强完成")
                print(f"📁 输出：{result['output']}")
            else:
                print(f"✅ 质量达标")
        else:
            print(f"❌ 处理失败：{result.get('error', '未知错误')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
