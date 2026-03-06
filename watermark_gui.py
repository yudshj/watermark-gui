#!/usr/bin/env python3
"""水印 GUI 工具 - 基于 tkinter 的图片水印添加工具"""

import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
from PIL import Image, ImageTk

from add_watermark import apply_watermark

PREVIEW_MAX = 800  # 预览区域最大尺寸


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片水印工具")
        self.root.geometry("1100x750")
        self.root.minsize(800, 500)

        self.original_img = None  # 原图 PIL Image
        self.preview_img = None   # 缩小后用于预览的 PIL Image
        self.photo_image = None   # 保持 PhotoImage 引用防止 GC
        self.debounce_id = None
        self.color = (128, 128, 128)

        self._build_menu()
        self._build_ui()
        self._build_statusbar()

    # ── 菜单栏 ──────────────────────────────────────────────

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开图片…", command=self.open_image, accelerator="⌘O")
        file_menu.add_command(label="保存…", command=self.save_image, accelerator="⌘S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)

        self.root.bind("<Command-o>", lambda e: self.open_image())
        self.root.bind("<Command-s>", lambda e: self.save_image())

    # ── 主界面 ──────────────────────────────────────────────

    def _build_ui(self):
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        # 左侧预览
        preview_frame = ttk.Frame(main)
        main.add(preview_frame, weight=3)

        self.canvas = tk.Canvas(preview_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._schedule_preview())

        # 右侧控制面板
        ctrl_frame = ttk.Frame(main, padding=10)
        main.add(ctrl_frame, weight=0)

        # 水印文字
        ttk.Label(ctrl_frame, text="水印文字").pack(anchor="w")
        self.text_var = tk.StringVar(value="仅供 XX 使用")
        entry = ttk.Entry(ctrl_frame, textvariable=self.text_var, width=20)
        entry.pack(fill="x", pady=(0, 10))
        self.text_var.trace_add("write", lambda *_: self._schedule_preview())

        # 字体大小
        self.font_size_var = tk.IntVar(value=50)
        self._add_slider(ctrl_frame, "字体大小", self.font_size_var, 10, 200)

        # 透明度
        self.opacity_var = tk.IntVar(value=150)
        self._add_slider(ctrl_frame, "透明度", self.opacity_var, 0, 255)

        # 间距
        self.spacing_var = tk.IntVar(value=100)
        self._add_slider(ctrl_frame, "间距", self.spacing_var, 20, 500)

        # 角度
        self.angle_var = tk.IntVar(value=35)
        self._add_slider(ctrl_frame, "角度", self.angle_var, 0, 90)

        # 颜色选择
        color_frame = ttk.Frame(ctrl_frame)
        color_frame.pack(fill="x", pady=(5, 10))
        ttk.Label(color_frame, text="颜色").pack(side="left")
        self.color_btn = tk.Button(
            color_frame, width=4, bg=self._color_hex(),
            relief="solid", command=self.pick_color,
        )
        self.color_btn.pack(side="right")

        # 按钮
        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.pack(fill="x", pady=(15, 0))
        ttk.Button(btn_frame, text="预览", command=self._update_preview).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(btn_frame, text="保存", command=self.save_image).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _add_slider(self, parent, label, var, from_, to):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=(0, 8))
        ttk.Label(frame, text=label).pack(side="left")
        val_label = ttk.Label(frame, text=str(var.get()), width=4)
        val_label.pack(side="right")
        slider = ttk.Scale(
            parent, from_=from_, to=to, variable=var, orient="horizontal",
            command=lambda v, lbl=val_label, variable=var: (
                lbl.config(text=str(variable.get())),
                self._schedule_preview(),
            ),
        )
        slider.pack(fill="x", pady=(0, 5))

    # ── 状态栏 ──────────────────────────────────────────────

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="就绪 — 请打开一张图片")
        bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", padding=(8, 2))
        bar.pack(side="bottom", fill="x")

    # ── 颜色 ────────────────────────────────────────────────

    def _color_hex(self):
        return "#%02x%02x%02x" % self.color

    def pick_color(self):
        result = colorchooser.askcolor(color=self._color_hex(), title="选择水印颜色")
        if result[0]:
            self.color = tuple(int(c) for c in result[0])
            self.color_btn.config(bg=self._color_hex())
            self._schedule_preview()

    # ── 打开 / 保存 ────────────────────────────────────────

    def open_image(self):
        path = filedialog.askopenfilename(
            title="打开图片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("所有文件", "*.*"),
            ],
        )
        if not path:
            return
        self.original_img = Image.open(path)
        w, h = self.original_img.size
        self.status_var.set(f"已打开: {path}  ({w}×{h})")
        self._update_preview()

    def save_image(self):
        if self.original_img is None:
            self.status_var.set("请先打开一张图片")
            return
        text = self.text_var.get().strip()
        if not text:
            self.status_var.set("请输入水印文字")
            return
        path = filedialog.asksaveasfilename(
            title="保存图片",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
            ],
        )
        if not path:
            return
        result = apply_watermark(
            self.original_img, text,
            font_size=self.font_size_var.get(),
            opacity=self.opacity_var.get(),
            color=self.color,
            spacing=self.spacing_var.get(),
            angle=self.angle_var.get(),
        )
        if path.lower().endswith((".jpg", ".jpeg")):
            result = result.convert("RGB")
        result.save(path)
        self.status_var.set(f"已保存: {path}")

    # ── 预览 ────────────────────────────────────────────────

    def _schedule_preview(self):
        if self.debounce_id is not None:
            self.root.after_cancel(self.debounce_id)
        self.debounce_id = self.root.after(300, self._update_preview)

    def _update_preview(self):
        self.debounce_id = None
        if self.original_img is None:
            return
        text = self.text_var.get().strip()
        if not text:
            self._show_plain_preview()
            return

        # 缩小原图以加速预览
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 2 or ch < 2:
            return
        img = self.original_img.copy()
        img.thumbnail((cw, ch), Image.LANCZOS)

        # 按缩放比例调整 font_size 和 spacing
        scale = img.size[0] / self.original_img.size[0]
        preview_font = max(8, int(self.font_size_var.get() * scale))
        preview_spacing = max(5, int(self.spacing_var.get() * scale))

        result = apply_watermark(
            img, text,
            font_size=preview_font,
            opacity=self.opacity_var.get(),
            color=self.color,
            spacing=preview_spacing,
            angle=self.angle_var.get(),
        )
        self._display(result)

    def _show_plain_preview(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 2 or ch < 2:
            return
        img = self.original_img.copy()
        img.thumbnail((cw, ch), Image.LANCZOS)
        self._display(img.convert("RGBA"))

    def _display(self, pil_img):
        self.photo_image = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        self.canvas.create_image(cw // 2, ch // 2, image=self.photo_image)


def main():
    root = tk.Tk()
    WatermarkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
