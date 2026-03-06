# 图片水印工具

给照片添加倾斜平铺文字水印，支持命令行和 GUI 两种使用方式。

## 依赖

```bash
pip install Pillow
```

tkinter 随 Python 自带（macOS 需确认已安装 `python-tk`）。

## 使用方式

### GUI

```bash
python3 watermark_gui.py
```

- 打开图片 → 调整参数 → 实时预览 → 保存
- 支持快捷键：⌘O 打开、⌘S 保存
- 可调参数：水印文字、字体大小、透明度、间距、角度、颜色

### 命令行

```bash
python3 add_watermark.py -i input.jpg -o output.jpg -t "仅供XX使用"
```

可选参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--font-size` | 字体大小 | 50 |
| `--opacity` | 透明度 (0-255) | 150 |
| `--spacing` | 水印间距（像素） | 100 |
| `--angle` | 倾斜角度 | 35 |

## 项目结构

```
add_watermark.py   # 核心水印逻辑 + CLI 入口
watermark_gui.py   # tkinter GUI
```

`apply_watermark(img, text, ...)` 是核心函数，接收 PIL Image 返回合成后的 RGBA Image，供 CLI 和 GUI 共用。
