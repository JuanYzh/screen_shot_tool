# -*- coding: utf-8 -*-
# Copyright (c) 2023 by WenHuan Yang-Zhang.
# Date: 2023-03.01
# Ich und google :)
import io
import tkinter as tk
from tkinter import ttk
import win32clipboard as clipboard
from tkinter import Toplevel, Menu, colorchooser
from PIL import Image, ImageTk, ImageGrab, ImageDraw


cversion = "ScreenShot tool - v1.0.0"


class ScreenShotImage():
    def __init__(self, root, screenshot_image):
        self.root = root
        self.screenshot_image = screenshot_image
        self.screenshot_image_copy = screenshot_image.copy()

    def show_screenshot(self):
        screenshot = self.screenshot_image
        self.screenshot_window = Toplevel(self.root)
        self.screenshot_window.title("Screenshot")

        self.screenshot_tk_image = ImageTk.PhotoImage(screenshot)
        self.label = ttk.Label(self.screenshot_window, image=self.screenshot_tk_image)
        self.label.pack(fill=tk.BOTH, expand=True)

        self.setup_tools(self.screenshot_window)

        width, height = screenshot.size
        self.screenshot_window.geometry(f"{width}x{height + 50}")
        self.screenshot_window.overrideredirect(True)  # 去掉窗口边框
        self.screenshot_window.attributes('-topmost', True)  # 窗口置顶

        self.initial_width = int(self.screenshot_tk_image.width())
        self.initial_height = int(self.screenshot_tk_image.height())

        def on_right_click(event):
            menu = Menu(self.screenshot_window, tearoff=0)
            menu.add_command(label="Copy", command=self.copy_image)
            menu.add_command(label="Close", command=self.screenshot_window.destroy)
            menu.post(event.x_root, event.y_root)

        self.label.bind("<Button-1>", self.on_draw_press)
        self.label.bind("<B1-Motion>", self.on_draw_drag)
        self.label.bind("<ButtonRelease-1>", self.on_draw_release)
        self.label.bind("<Button-3>", on_right_click)
        self.screenshot_window.bind("<MouseWheel>", self.on_mouse_wheel)
        self.screenshot_window.resizable(True, True)

    def start_move(self, event):
        self.screenshot_window._x = event.x
        self.screenshot_window._y = event.y

    # 允许拖动窗口
    def do_move(self, event):
        x = event.x_root - self.screenshot_window._x
        y = event.y_root - self.screenshot_window._y
        self.screenshot_window.geometry(f"+{x}+{y}")

    def on_mouse_wheel(self, event):
        current_width = self.screenshot_window.winfo_width()
        current_height = self.screenshot_window.winfo_height()

        if event.delta > 0:  # 向上滚动，放大
            new_width = int(current_width * 1.1)
            new_height = int(current_height * 1.1)
        else:  # 向下滚动，缩小
            new_width = int(current_width * 0.9)
            new_height = int(current_height * 0.9)

        self.screenshot_window.geometry(f"{new_width}x{new_height}")
        self.update_image_size(new_width, new_height - 50)

    def update_image_size(self, width, height):
        resized_image = self.screenshot_image.resize((width, height), Image.Resampling.LANCZOS)
        self.screenshot_tk_image = ImageTk.PhotoImage(resized_image)
        self.label.config(image=self.screenshot_tk_image)
        self.label.image = self.screenshot_tk_image

    def setup_tools(self, window):
        self.current_tool = None
        self.current_color = 'red'
        self.draw = ImageDraw.Draw(self.screenshot_image)

        toolbar = ttk.Frame(window)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tool_var = tk.StringVar(value="None")
        tools = ["None", "Rectangle", "Brush", "Text"]
        for tool in tools:
            b = tk.Radiobutton(toolbar, text=tool, variable=self.tool_var, value=tool, indicatoron=False)
            b.pack(side=tk.LEFT)

        colors = ["red", "white", "black", "blue", "green", "yellow"]
        for color in colors:
            b = tk.Button(toolbar, bg=color, width=2, command=lambda c=color: self.set_color(c))
            b.pack(side=tk.LEFT)

        clear_button = ttk.Button(toolbar, text="Clear", command=self.clear_drawings)
        clear_button.pack(side=tk.LEFT)

        copy_button = ttk.Button(toolbar, text="Copy", command=self.copy_image)
        copy_button.pack(side=tk.LEFT)

        destroy_button = ttk.Button(toolbar, text="Destroy", command=self.screenshot_window.destroy)
        destroy_button.pack(side=tk.LEFT)

    def set_color(self, color):
        self.current_color = color

    def clear_drawings(self):
        self.screenshot_image.paste(self.screenshot_image_copy)
        self.update_image()

    def copy_image(self):
        # 将图像保存到内存中的字节流
        output = io.BytesIO()
        self.screenshot_image.save(output, format='BMP')  # 保存为 BMP 格式
        data = output.getvalue()[14:]
        output.close()
        clipboard.OpenClipboard()
        clipboard.EmptyClipboard()
        clipboard.SetClipboardData(clipboard.CF_DIB, data)
        clipboard.CloseClipboard()

    def update_image(self):
        self.update_win_size()
        # self.screenshot_tk_image = ImageTk.PhotoImage(self.screenshot_image)
        # self.label.config(image=self.screenshot_tk_image)
        # self.label.image = self.screenshot_tk_image
        # self.update_win_size()

    def on_draw_press(self, event):
        if self.tool_var.get() == "None":
            self.start_move(event)
            self.is_drawing = False
        else:
            self.is_drawing = True
            self.update_win_size()
            zoom_factor_x = self.get_zoom_factor_x()
            zoom_factor_y = self.get_zoom_factor_y()
            self.draw_start_x = event.x / zoom_factor_x
            self.draw_start_y = event.y / zoom_factor_y
            # print("点击", self.draw_start_x, self.draw_start_y)

    def on_draw_drag(self, event):
        if self.is_drawing:
            self.update_win_size()
            if self.tool_var.get() == "Brush":
                zoom_factor_x = self.get_zoom_factor_x()
                zoom_factor_y = self.get_zoom_factor_y()
                self.draw.line([(self.draw_start_x, self.draw_start_y),
                                (event.x / zoom_factor_x, event.y / zoom_factor_y)],
                               fill=self.current_color,
                               width=3)
                self.draw_start_x, self.draw_start_y = event.x / zoom_factor_x, event.y / zoom_factor_y
                # print("拖拽", self.draw_start_x, self.draw_start_y)
            self.update_image()
        else:
            self.do_move(event)

    def on_draw_release(self, event):
        if self.is_drawing:
            self.update_image()
            zoom_factor_x = self.get_zoom_factor_x()
            zoom_factor_y = self.get_zoom_factor_y()
            if self.tool_var.get() == "Rectangle":
                self.draw.rectangle([(self.draw_start_x, self.draw_start_y),
                                     (event.x / zoom_factor_x, event.y / zoom_factor_y)],
                                    outline=self.current_color)
            elif self.tool_var.get() == "Text":
                self.draw_text(event.x / zoom_factor_x, event.y / zoom_factor_y)
            self.is_drawing = False
            self.update_image()

    def draw_text(self, x, y):
        def show_input_dialog():
            def on_ok():
                text = text_entry.get()
                fontsize = fontsize_entry.get()
                if str(fontsize).isdigit():
                    fontsize = int(fontsize)
                else:
                    fontsize = 10
                self.draw.text((x, y), text, fill=self.current_color, font_size=fontsize)
                input_window.destroy()

            def on_cancel():
                input_window.destroy()

            input_window = tk.Toplevel(self.screenshot_window)
            input_window.attributes('-topmost', True)
            input_window.title("Input")

            input_window.geometry("300x150")
            input_window.transient(self.screenshot_window)
            input_window.grab_set()

            input_window.grid_rowconfigure(0, weight=1)
            input_window.grid_rowconfigure(1, weight=1)
            input_window.grid_rowconfigure(2, weight=1)
            input_window.grid_columnconfigure(0, weight=1)

            input_frame = tk.Frame(input_window)
            input_frame.grid(row=0, column=0, sticky="ew")
            input_frame.columnconfigure(0, weight=1)

            enter_label = ttk.Label(input_frame, text="Enter text:")
            enter_label.grid(row=0, column=0, sticky="ew")

            text_entry = ttk.Entry(input_frame)
            text_entry.grid(row=1, column=0, sticky="ew")

            fontsize_label = ttk.Label(input_frame, text="Font size:")
            fontsize_label.grid(row=2, column=0, sticky="ew")

            fontsize_entry = ttk.Entry(input_frame, )
            fontsize_entry.insert(0, 10)
            fontsize_entry.grid(row=3, column=0, sticky="ew")

            input_frame.grid_columnconfigure(0, weight=1)
            input_frame.grid_rowconfigure(0, weight=1)
            input_frame.grid_rowconfigure(1, weight=1)

            button_frame = tk.Frame(input_window)
            button_frame.grid(row=1, column=0, sticky="ew")

            ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
            ok_button.grid(row=0, column=0, sticky="ew")

            cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
            cancel_button.grid(row=0, column=1, sticky="ew")

            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            button_frame.grid_rowconfigure(0, weight=1)

            self.screenshot_window.wait_window(input_window)

        show_input_dialog()

    def update_win_size(self):
        new_width = self.screenshot_window.winfo_width()
        new_height = self.screenshot_window.winfo_height()
        self.screenshot_window.geometry(f"{new_width}x{new_height}")
        self.update_image_size(new_width, new_height - 50)

    def get_zoom_factor_x(self):
        current_width = int(self.screenshot_tk_image.width())
        zoom_factor_x = current_width / self.initial_width
        return zoom_factor_x

    def get_zoom_factor_y(self):
        current_height = int(self.screenshot_tk_image.height())
        zoom_factor_y = current_height / self.initial_height
        return zoom_factor_y


class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title(cversion)
        self.root.geometry("200x100")

        self.screenshot_button = ttk.Button(self.root, text="Screenshot", command=self.start_selection)
        self.screenshot_button.pack(pady=10)

        self.quit_button = ttk.Button(self.root, text="Quit", command=self.root.quit)
        self.quit_button.pack(pady=10)

        self.is_drawing = False  # 初始化绘图状态
        self.initial_width = None  # 初始化初始宽度
        self.initial_height = None  # 初始化初始高度

    def start_selection(self):
        self.selection_window = Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.3)
        self.selection_window.configure(background='black')
        self.canvas = tk.Canvas(self.selection_window, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.start_x = None
        self.start_y = None

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.selection_window.destroy()

        # 确保坐标顺序正确
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        self.take_screenshot(x1, y1, x2, y2)

    def take_screenshot(self, x1, y1, x2, y2):
        self.root.withdraw()  # 隐藏主窗口
        self.screenshot_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        self.screenshot_image_copy = self.screenshot_image.copy()
        self.root.deiconify()  # 截图完成后显示主窗口
        self.show_screenshot(self.screenshot_image)

    def show_screenshot(self, screenshot_image):
        draw_win = ScreenShotImage(self.root, screenshot_image)
        draw_win.show_screenshot()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
