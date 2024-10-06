import tkinter as tk
from pynput import mouse

class ScreenAreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.3)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)

        # Print info on canvas
        info_text = "Drag to select the area of your Farm Merge Valley game"
        self.canvas.create_text(self.root.winfo_screenwidth() // 2, 50, text=info_text, font=("Arial", 24), fill="black")

        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move)
        self.listener.start()

        self.root.mainloop()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.start_x = x
            self.start_y = y
            self.rect = self.canvas.create_rectangle(x, y, x, y, outline="blue", fill="blue")
        else:
            self.end_x, self.end_y = x, y
            self.canvas.delete(self.rect)
            self.listener.stop()
            self.root.quit()

    def on_move(self, x, y):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, x, y)

    def get_coordinates(self):
        if self.start_x > self.end_x:
            self.start_x, self.end_x = self.end_x, self.start_x
        if self.start_y > self.end_y:
            self.start_y, self.end_y = self.end_y, self.start_y
        self.root.destroy()
        return self.start_x, self.start_y, self.end_x, self.end_y

    # def close(self):
    #     self.listener.stop()
    #     self.root.quit()
    #     self.root.destroy()