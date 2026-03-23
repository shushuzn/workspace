#!/usr/bin/env python3
# super_resolution.py - 图像超分辨率增强器
# 用法：py super_resolution.py <image_file> [--output <output_file>] [--scale 4]

import argparse
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    # 尝试导入 Real-ESRGAN
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    REAL_ESRGAN_AVAILABLE = True
except ImportError:
    REAL_ESRGAN_AVAILABLE = False

class SuperResolution:
    """图像超分辨率增强器"""

    def __init__(self, scale=4, use_realesrgan=True):
        self.scale = scale
        self.use_realesrgan = use_realesrgan and REAL_ESRGAN_AVAILABLE

        if self.use_realesrgan:
            print("🔧 初始化 Real-ESRGAN...")
            self._init_realesrgan()
            print("✅ Real-ESRGAN 就绪")
        else:
            print("⚠️ 使用 OpenCV 备用方案 (BICUBIC 插值)")

    def _init_realesrgan(self):
        """初始化 Real-ESRGAN 模型"""
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=self.scale
        )

        self.upsampler = RealESRGANer(
            scale=self.scale,
            model_path='experiments/pretrained_models/RealESRGAN_x4plus.pth',
            model=model,
            tile=0,  # 0 = 不分割，完整处理
            tile_pad=10,
            pre_pad=0,
            half=True  # 使用半精度加速
        )

    def enhance(self, image_path, output_path=None):
        """增强图像分辨率"""
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ 无法读取图像：{image_path}")
            return None

        h, w = image.shape[:2]
        print(f"📊 原始尺寸：{w}x{h}")

        if self.use_realesrgan:
            print("🚀 Real-ESRGAN 处理中...")
            output, _ = self.upsampler.enhance(image, outscale=self.scale)
        else:
            print("🚀 OpenCV BICUBIC 插值中...")
            output = cv2.resize(image, (w *self.scale, h *self.scale), interpolation=cv2.INTER_CUBIC)

        new_h, new_w = output.shape[:2]
        print(f"✅ 增强完成：{new_w}x{new_h} (放大{self.scale}倍)")

        if output_path:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), output)
            print(f"📁 已保存：{output_path}")

        return output

    def batch_enhance(self, image_dir, output_dir, scale=4):
        """批量增强目录中的图像"""
        image_dir = Path(image_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        image_files = list(image_dir.glob('*.png')) + list(image_dir.glob('*.jpg'))

        print(f"📊 批量处理：{len(image_files)} 个图像")

        for i, img_file in enumerate(image_files):
            output_file = output_dir / img_file.name
            print(f"   [{i +1}/{len(image_files)}] {img_file.name}")
            self.enhance(img_file, output_file)

        print(f"\n✅ 批量处理完成")
        print(f"📁 输出目录：{output_dir}")


def main():
    parser = argparse.ArgumentParser(description="图像超分辨率增强器")
    parser.add_argument("image_file", type=str, nargs='?', help="图像文件路径")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径")
    parser.add_argument("--scale", "-s", type=int, default=4, choices=[2, 4], help="放大倍数 (2 或 4)")
    parser.add_argument("--batch", "-b", type=str, help="批量处理目录")
    parser.add_argument("--output-dir", type=str, help="批量处理输出目录")

    args = parser.parse_args()

    if args.batch:
        # 批量模式
        if not args.output_dir:
            args.output_dir = args.batch + "_enhanced"

        sr = SuperResolution(scale=args.scale)
        sr.batch_enhance(args.batch, args.output_dir, scale=args.scale)
    elif args.image_file:
        # 单文件模式
        image_path = Path(args.image_file)
        if not image_path.exists():
            print(f"❌ 文件不存在：{image_path}")
            sys.exit(1)

        if not args.output:
            args.output = str(image_path.parent / f"{image_path.stem}_enhanced.png")

        sr = SuperResolution(scale=args.scale)
        sr.enhance(image_path, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
