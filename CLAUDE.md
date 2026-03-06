# Project: watermark-gui

图片水印工具，支持 CLI 和 tkinter GUI。

## Architecture

- `add_watermark.py` — 核心水印逻辑 + CLI 入口
  - `apply_watermark(img, text, ...)`: 核心函数，接收 PIL Image，返回 RGBA Image
  - `add_watermark(input_path, output_path, text, ...)`: CLI 包装，打开文件 → apply_watermark → 保存
- `watermark_gui.py` — tkinter GUI，import `apply_watermark` 实现预览和保存

## Key Details

- 字体回退链: STHeiti Medium → PingFang → default（macOS 优先）
- GUI 预览使用缩小图 + 等比缩放参数（font_size, spacing），300ms debounce
- 保存时用原图全分辨率生成
- 支持格式: jpg/jpeg/png/bmp/webp

## Dependencies

- Python 3
- Pillow
- tkinter (stdlib)
