import tkinter as tk
from pynput import mouse

class MergingPointsSelector:
    def __init__(self, point_num):
        self.point_num = point_num
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-alpha", 0.3)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Print info on canvas
        info_text = f"Please click {self.point_num} center points of space for merging points on the screen."
        self.canvas.create_text(self.root.winfo_screenwidth() // 2, 50, text=info_text, font=("Arial", 24), fill="black")

        self.points = []
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        self.root.mainloop()

    def on_click(self, x, y, button, pressed):
        if pressed and len(self.points) < self.point_num:
            self.points.append((x, y))
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
            if len(self.points) == self.point_num:
                self.listener.stop()
                self.root.quit()

    def get_points(self):
        self.root.destroy()
        return self.points
