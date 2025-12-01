import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuration
IMG_WIDTH = 800
IMG_HEIGHT = 600
GRID_ROWS = 8
GRID_COLS = 8

class ColorVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Histogram Visualizer")
        
        # State
        self.current_pil_img = None
        self.current_image_name = ""
        self.image_list = []
        self.current_img_index = 0
        
        # Layout
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel: Image
        self.left_panel = tk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.left_panel, width=IMG_WIDTH, height=IMG_HEIGHT, bg="grey")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Controls
        ctrl_frame = tk.Frame(self.left_panel)
        ctrl_frame.pack(pady=10)
        
        btn_load = tk.Button(ctrl_frame, text="Load Folder", command=self.load_folder)
        btn_load.pack(side=tk.TOP, pady=5)
        
        nav_frame = tk.Frame(ctrl_frame)
        nav_frame.pack(side=tk.TOP)
        
        tk.Button(nav_frame, text="<< Prev", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next >>", command=self.next_image).pack(side=tk.LEFT, padx=5)
        
        self.lbl_status = tk.Label(self.left_panel, text="Load a folder to start")
        self.lbl_status.pack()

        # Right Panel: Plots
        self.right_panel = tk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Matplotlib Figure
        self.fig, self.axs = plt.subplots(2, 1, figsize=(5, 8))
        self.fig.tight_layout(pad=3.0)
        
        self.axs[0].set_title("Selected Cell")
        self.axs[0].axis('off')
        
        self.axs[1].set_title("RGB Color Histograms")
        self.axs[1].set_xlabel("Pixel Value")
        self.axs[1].set_ylabel("Frequency")
        
        self.chart = FigureCanvasTkAgg(self.fig, self.right_panel)
        self.chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def load_folder(self):
        initial_dir = os.path.join(os.getcwd(), "raw_images")
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
            
        folder_path = filedialog.askdirectory(initialdir=initial_dir)
        if not folder_path:
            return
            
        # Get all images
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        self.image_list = [
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path) 
            if os.path.splitext(f)[1].lower() in valid_exts
        ]
        
        if not self.image_list:
            messagebox.showerror("Error", "No images found in folder!")
            return
            
        self.current_img_index = 0
        self.load_current_image()

    def load_current_image(self):
        if not self.image_list:
            return
            
        filepath = self.image_list[self.current_img_index]
        
        try:
            pil_img = Image.open(filepath)
            
            # Check dimensions (optional, but good for consistency)
            w, h = pil_img.size
            if w < IMG_WIDTH or h < IMG_HEIGHT:
                print(f"Warning: {os.path.basename(filepath)} is small ({w}x{h})")

            pil_img = pil_img.resize((IMG_WIDTH, IMG_HEIGHT), Image.Resampling.LANCZOS)
            self.current_pil_img = pil_img.convert("RGB")
            self.current_image_name = os.path.basename(filepath)
            
            self.tk_img = ImageTk.PhotoImage(self.current_pil_img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
            
            self.draw_grid()
            self.lbl_status.config(text=f"Image {self.current_img_index + 1}/{len(self.image_list)}: {self.current_image_name}")
            
            # Clear plots
            for ax in self.axs:
                ax.clear()
            self.axs[0].set_title("Selected Cell")
            self.axs[1].set_title("RGB Color Histograms")
            self.axs[0].axis('off')
            self.chart.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def next_image(self):
        if self.current_img_index < len(self.image_list) - 1:
            self.current_img_index += 1
            self.load_current_image()

    def prev_image(self):
        if self.current_img_index > 0:
            self.current_img_index -= 1
            self.load_current_image()

    def draw_grid(self):
        self.canvas.delete("grid_line")
        cell_w = IMG_WIDTH / GRID_COLS
        cell_h = IMG_HEIGHT / GRID_ROWS
        
        for i in range(1, GRID_COLS):
            x = i * cell_w
            self.canvas.create_line(x, 0, x, IMG_HEIGHT, fill="yellow", tags="grid_line")
            
        for i in range(1, GRID_ROWS):
            y = i * cell_h
            self.canvas.create_line(0, y, IMG_WIDTH, y, fill="yellow", tags="grid_line")

    def on_canvas_click(self, event):
        if not self.current_pil_img:
            return
            
        cell_w = IMG_WIDTH / GRID_COLS
        cell_h = IMG_HEIGHT / GRID_ROWS
        
        col = int(event.x // cell_w)
        row = int(event.y // cell_h)
        
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            self.visualize_cell(row, col)

    def visualize_cell(self, row, col):
        cell_w = int(IMG_WIDTH / GRID_COLS)
        cell_h = int(IMG_HEIGHT / GRID_ROWS)
        
        x1 = col * cell_w
        y1 = row * cell_h
        x2 = x1 + cell_w
        y2 = y1 + cell_h
        
        # Extract cell image
        cell_img = self.current_pil_img.crop((x1, y1, x2, y2))
        cell_array = np.array(cell_img)
        
        # Update Plots
        self.axs[0].clear()
        self.axs[0].imshow(cell_array)
        self.axs[0].set_title(f"Cell ({row+1}, {col+1})")
        self.axs[0].axis('off')
        
        self.axs[1].clear()
        self.axs[1].set_title("RGB Color Histograms")
        self.axs[1].set_xlabel("Pixel Value")
        self.axs[1].set_ylabel("Frequency")
        
        # Plot Histograms
        colors = ('red', 'green', 'blue')
        for i, color in enumerate(colors):
            hist, bins = np.histogram(cell_array[:, :, i], bins=256, range=(0, 256))
            self.axs[1].plot(bins[:-1], hist, color=color, alpha=0.7, label=color.upper())
            
        self.axs[1].legend()
        self.axs[1].set_xlim(0, 255)
        
        self.chart.draw()
        
        # Highlight cell on canvas
        self.canvas.delete("highlight")
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3, tags="highlight")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1400x700")
    app = ColorVisualizer(root)
    root.mainloop()
