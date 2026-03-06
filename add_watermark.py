#!/usr/bin/env python3
"""给照片添加倾斜平铺水印"""

import argparse
import math
from PIL import Image, ImageDraw, ImageFont


def apply_watermark(img, text, font_size=40, opacity=50, color=(128, 128, 128), spacing=100, angle=35):
    """
    给 PIL Image 添加倾斜平铺水印，返回合成后的 RGBA Image。

    Args:
        img: PIL Image 对象
        text: 水印文字
        font_size: 字体大小
        opacity: 透明度 (0-255)
        color: 水印颜色 RGB
        spacing: 水印间距（像素）
        angle: 倾斜角度
    Returns:
        合成水印后的 PIL Image (RGBA)
    """
    img = img.convert("RGBA")
    w, h = img.size

    # 创建足够大的透明图层，旋转后能覆盖原图
    diag = int(math.sqrt(w ** 2 + h ** 2))
    watermark_layer = Image.new("RGBA", (diag * 2, diag * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", font_size)
    except OSError:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
        except OSError:
            font = ImageFont.load_default()

    # 计算单个水印文字的尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 平铺水印
    step_x = text_w + spacing
    step_y = text_h + spacing
    fill = (*color, opacity)

    y = 0
    row = 0
    while y < diag * 2:
        x = -(step_x // 2) if row % 2 else 0  # 奇偶行错开
        while x < diag * 2:
            draw.text((x, y), text, font=font, fill=fill)
            x += step_x
        y += step_y
        row += 1

    # 旋转水印图层
    watermark_layer = watermark_layer.rotate(angle, resample=Image.BICUBIC)

    # 裁剪到原图中心区域
    cx, cy = watermark_layer.size[0] // 2, watermark_layer.size[1] // 2
    crop_box = (cx - w // 2, cy - h // 2, cx - w // 2 + w, cy - h // 2 + h)
    watermark_layer = watermark_layer.crop(crop_box)

    return Image.alpha_composite(img, watermark_layer)


def add_watermark(input_path, output_path, text, font_size=40, opacity=50, color=(128, 128, 128), spacing=100, angle=35):
    """
    给图片添加倾斜平铺水印并保存。

    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        text: 水印文字
        font_size: 字体大小
        opacity: 透明度 (0-255)
        color: 水印颜色 RGB
        spacing: 水印间距（像素）
        angle: 倾斜角度
    """
    img = Image.open(input_path)
    result = apply_watermark(img, text, font_size=font_size, opacity=opacity,
                             color=color, spacing=spacing, angle=angle)

    if output_path.lower().endswith((".jpg", ".jpeg")):
        result = result.convert("RGB")
    result.save(output_path)
    print(f"水印已添加: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="给照片添加倾斜平铺水印")
    parser.add_argument("-i", "--input", required=True, help="输入图片路径")
    parser.add_argument("-o", "--output", required=True, help="输出图片路径")
    parser.add_argument("-t", "--text", required=True, help="水印文字")
    parser.add_argument("--font-size", type=int, default=50, help="字体大小 (默认: 50)")
    parser.add_argument("--opacity", type=int, default=150, help="透明度 0-255 (默认: 150)")
    parser.add_argument("--spacing", type=int, default=100, help="水印间距像素 (默认: 100)")
    parser.add_argument("--angle", type=int, default=35, help="倾斜角度 (默认: 35)")
    args = parser.parse_args()

    add_watermark(
        input_path=args.input,
        output_path=args.output,
        text=args.text,
        font_size=args.font_size,
        opacity=args.opacity,
        spacing=args.spacing,
        angle=args.angle,
    )


if __name__ == "__main__":
    main()
