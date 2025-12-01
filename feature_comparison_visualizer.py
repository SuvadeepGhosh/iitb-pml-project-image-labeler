import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
from skimage.feature import hog
from skimage import exposure

# Configuration
IMG_WIDTH = 800
IMG_HEIGHT = 600
GRID_ROWS = 8
GRID_COLS = 8

class FeatureComparisonVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Feature Comparison Visualizer")
        
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
        
        # Matplotlib Figure (4x3 grid)
        # Rows: Original, Edge, Sharpen, Blur
        # Cols: Image, HOG, Color Hist
        self.fig, self.axs = plt.subplots(4, 3, figsize=(12, 10))
        self.fig.tight_layout(pad=2.0)
        
        self.row_labels = ["Original", "Edge Detection", "Sharpen", "Box Blur"]
        self.col_labels = ["Cell Image", "HOG Features", "Color Histogram"]
        
        # Set initial titles
        for i in range(4):
            for j in range(3):
                self.axs[i, j].axis('off')
                if i == 0:
                    self.axs[i, j].set_title(self.col_labels[j])
                if j == 0:
                    self.axs[i, j].set_ylabel(self.row_labels[i])
                    # We need to turn axis on to see ylabel, but remove ticks
                    self.axs[i, j].axis('on')
                    self.axs[i, j].set_xticks([])
                    self.axs[i, j].set_yticks([])
                    self.axs[i, j].spines['top'].set_visible(False)
                    self.axs[i, j].spines['right'].set_visible(False)
                    self.axs[i, j].spines['bottom'].set_visible(False)
                    self.axs[i, j].spines['left'].set_visible(False)

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
            
            # Check dimensions
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
            
            # Clear plots but keep structure
            for i in range(4):
                for j in range(3):
                    self.axs[i, j].clear()
                    self.axs[i, j].axis('off')
                    if i == 0:
                        self.axs[i, j].set_title(self.col_labels[j])
                    if j == 0:
                        self.axs[i, j].set_ylabel(self.row_labels[i])
                        self.axs[i, j].axis('on')
                        self.axs[i, j].set_xticks([])
                        self.axs[i, j].set_yticks([])
                        self.axs[i, j].spines['top'].set_visible(False)
                        self.axs[i, j].spines['right'].set_visible(False)
                        self.axs[i, j].spines['bottom'].set_visible(False)
                        self.axs[i, j].spines['left'].set_visible(False)
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
        
        # Define Kernels
        kernel_edge = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        kernel_sharpen = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        kernel_blur = np.ones((5, 5), np.float32) / 25
        
        # Apply Convolutions
        img_edge = cv2.filter2D(cell_array, -1, kernel_edge)
        img_sharpen = cv2.filter2D(cell_array, -1, kernel_sharpen)
        img_blur = cv2.filter2D(cell_array, -1, kernel_blur)
        
        images = [cell_array, img_edge, img_sharpen, img_blur]
        
        # Update Plots
        for i, img in enumerate(images):
            # 1. Image
            self.axs[i, 0].clear()
            self.axs[i, 0].imshow(img)
            self.axs[i, 0].set_ylabel(self.row_labels[i])
            self.axs[i, 0].axis('on')
            self.axs[i, 0].set_xticks([])
            self.axs[i, 0].set_yticks([])
            self.axs[i, 0].spines['top'].set_visible(False)
            self.axs[i, 0].spines['right'].set_visible(False)
            self.axs[i, 0].spines['bottom'].set_visible(False)
            self.axs[i, 0].spines['left'].set_visible(False)
            if i == 0: self.axs[i, 0].set_title(self.col_labels[0])

            # 2. HOG
            fd, hog_image = hog(img, orientations=9, pixels_per_cell=(8, 8),
                                cells_per_block=(2, 2), visualize=True, channel_axis=-1)
            hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))
            
            self.axs[i, 1].clear()
            self.axs[i, 1].imshow(hog_image_rescaled, cmap=plt.cm.gray)
            self.axs[i, 1].axis('off')
            if i == 0: self.axs[i, 1].set_title(self.col_labels[1])
            
            # 3. Color Histogram
            self.axs[i, 2].clear()
            colors = ('red', 'green', 'blue')
            for c_idx, color in enumerate(colors):
                hist, bins = np.histogram(img[:, :, c_idx], bins=256, range=(0, 256))
                self.axs[i, 2].plot(bins[:-1], hist, color=color, alpha=0.7)
            self.axs[i, 2].set_xlim(0, 255)
            # Remove ticks for cleaner look
            self.axs[i, 2].set_xticks([])
            self.axs[i, 2].set_yticks([])
            if i == 0: self.axs[i, 2].set_title(self.col_labels[2])

        self.chart.draw()
        
        # Highlight cell on canvas
        self.canvas.delete("highlight")
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3, tags="highlight")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1600x900")
    app = FeatureComparisonVisualizer(root)
    root.mainloop()
