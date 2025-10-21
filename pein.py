import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import time

try:
    from PIL import Image, ImageGrab, ImageOps, ImageChops, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("рисовалка")
        self.root.geometry("800x600")

        self.color = "black"
        self.brush_size = 3

        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=500)
        self.canvas.pack(pady=10)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

        self.last_x, self.last_y = None, None

        self.create_toolbar()

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack()

        btn_color = tk.Button(toolbar, text="Цвет", command=self.choose_color)
        btn_color.pack(side=tk.LEFT, padx=5)

        btn_clear = tk.Button(toolbar, text="Очистить", command=self.clear_canvas)
        btn_clear.pack(side=tk.LEFT, padx=5)

        btn_save = tk.Button(toolbar, text="Сохранить", command=self.save_image)
        btn_save.pack(side=tk.LEFT, padx=5)

        size_label = tk.Label(toolbar, text="Размер кисти:")
        size_label.pack(side=tk.LEFT)

        self.size_entry = tk.Entry(toolbar, width=3)
        self.size_entry.insert(0, str(self.brush_size))
        self.size_entry.pack(side=tk.LEFT)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def paint(self, event):
        if self.last_x and self.last_y:
            try:
                self.brush_size = int(self.size_entry.get())
            except ValueError:
                self.brush_size = 3
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    fill=self.color, width=self.brush_size,
                                    capstyle=tk.ROUND, smooth=True)

        self.last_x = event.x
        self.last_y = event.y

    def reset(self, event):
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        self.canvas.delete("all")

    def save_image(self):
        if not PIL_AVAILABLE:
            messagebox.showerror("Ошибка", "Библиотека Pillow не установлена.")
            return

        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG файлы", "*.png")])
        if file_path:
            try:
                ImageGrab.grab().crop((x, y, x1, y1)).save(file_path)
                messagebox.showinfo("Сохранено", f"Изображение сохранено в:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ой", f"Не удалось сохранить изображение:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()
