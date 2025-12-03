import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import pandas as pd
import os

# --- CONFIGURATION (Based on Project Specs) ---
GRID_ROWS = 8
GRID_COLS = 8
IMG_WIDTH = 800
IMG_HEIGHT = 600
OUTPUT_CSV = "labels.csv"
OUTPUT_CSV = "labels1.csv"
CLEAN_DIR = "Processed_image"
REFERENCE_DIR = "Reference_Images"

# Color mapping for visual feedback
# 0: None, 1: Ball, 2: Bat, 3: Stump
COLORS = {
    0: "",          # Transparent/None
    1: "#FF0000",   # Red (Ball)
    2: "#0000FF",   # Blue (Bat)
    3: "#00FF00"    # Green (Stump)
}

NAMES = {0: "None", 1: "Ball", 2: "Bat", 3: "Stump"}

class CricketLabeler:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Grid Labeler (8x8)")
        
        # State
        self.image_list = []
        self.current_img_index = 0
        self.grid_data = [0] * 64 # Flat list for c01 to c64
        self.current_image_name = ""
        
        # Ensure processed directory exists
        # Ensure processed directories exist
        if not os.path.exists(CLEAN_DIR):
            os.makedirs(CLEAN_DIR)
        if not os.path.exists(REFERENCE_DIR):
            os.makedirs(REFERENCE_DIR)

        # UI Setup
        self.setup_ui()
        self.create_overlay_images()
        
    def create_overlay_images(self):
        self.overlay_images = {}
        cell_w = int(IMG_WIDTH / GRID_COLS)
        cell_h = int(IMG_HEIGHT / GRID_ROWS)
        alpha = 70 # Reduced opacity (0-255)
        
        # Map IDs to RGB
        rgb_map = {
            1: (255, 0, 0),   # Red
            2: (0, 0, 255),   # Blue
            3: (0, 255, 0)    # Green
        }
        
        for key, rgb in rgb_map.items():
            # Create PIL Image for saving later
            pil_overlay = Image.new("RGBA", (cell_w, cell_h), rgb + (alpha,))
            self.overlay_images_pil = self.overlay_images_pil if hasattr(self, 'overlay_images_pil') else {}
            self.overlay_images_pil[key] = pil_overlay
            
            # Create PhotoImage for UI
            self.overlay_images[key] = ImageTk.PhotoImage(pil_overlay)

        
    def setup_ui(self):
        # Create a main container with scrollbar
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Canvas for scrolling
        self.main_scroll_canvas = tk.Canvas(main_container)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=self.main_scroll_canvas.yview)
        
        # Frame inside canvas
        self.scrollable_frame = tk.Frame(self.main_scroll_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_scroll_canvas.configure(
                scrollregion=self.main_scroll_canvas.bbox("all")
            )
        )

        self.main_scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_scroll_canvas.configure(yscrollcommand=scrollbar.set)

        self.main_scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- UI Elements inside scrollable_frame ---
        
        # Top Control Panel
        control_frame = tk.Frame(self.scrollable_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        btn_load = tk.Button(control_frame, text="Load Images Folder", command=self.load_folder)
        btn_load.pack(side=tk.LEFT)
        
        self.lbl_status = tk.Label(control_frame, text="No images loaded")
        self.lbl_status.pack(side=tk.LEFT, padx=10)
        
        # Main Canvas for Image
        self.canvas = tk.Canvas(self.scrollable_frame, width=IMG_WIDTH, height=IMG_HEIGHT, bg="grey")
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Bottom Control Panel
        bottom_frame = tk.Frame(self.scrollable_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        btn_prev = tk.Button(bottom_frame, text="<< Previous", command=self.prev_image)
        btn_prev.pack(side=tk.LEFT)
        
        btn_save = tk.Button(bottom_frame, text="Save & Next >>", command=self.save_and_next, bg="lightblue")
        btn_save.pack(side=tk.RIGHT)
        
        btn_skip = tk.Button(bottom_frame, text="Skip >>", command=self.skip_image)
        btn_skip.pack(side=tk.RIGHT, padx=5)

        # Instructions
        lbl_instr = tk.Label(bottom_frame, text="Click grid cells to toggle: Ball(1) -> Bat(2) -> Stump(3)")
        lbl_instr.pack(side=tk.TOP)
        
        # Bind mousewheel
        self.main_scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.main_scroll_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_folder(self):
        initial_dir = os.path.join(os.getcwd(), "raw_images")
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
            
        folder_path = filedialog.askdirectory(initialdir=initial_dir)
        if not folder_path:
            return
            
        # Get all images
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".jfif", ".pjpeg", ".pjp"}
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
        self.current_image_name = os.path.basename(filepath)
        
        # Load and Resize Image
        try:
            pil_img = Image.open(filepath)
            
            # Check dimensions
            w, h = pil_img.size
            if w < IMG_WIDTH or h < IMG_HEIGHT:
                self.canvas.delete("all")
                self.canvas.create_text(IMG_WIDTH/2, IMG_HEIGHT/2, text=f"REJECTED: Image too small ({w}x{h})\nMin required: {IMG_WIDTH}x{IMG_HEIGHT}", fill="red", font=("Arial", 24), anchor=tk.CENTER)
                self.lbl_status.config(text=f"Image {self.current_img_index + 1}/{len(self.image_list)}: {self.current_image_name} [REJECTED]")
                self.grid_data = [0] * 64 
                self.current_pil_img = None 
                return

            pil_img = pil_img.resize((IMG_WIDTH, IMG_HEIGHT), Image.Resampling.LANCZOS)
            self.current_pil_img = pil_img.convert("RGBA") # Keep reference for saving
            
            self.tk_img = ImageTk.PhotoImage(pil_img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
            
            # Reset grid data for new image
            self.grid_data = [0] * 64 
            
            # Load existing labels if available
            if os.path.exists(OUTPUT_CSV):
                try:
                    df = pd.read_csv(OUTPUT_CSV)
                    if self.current_image_name in df["ImageFileName"].values:
                        row = df[df["ImageFileName"] == self.current_image_name].iloc[0]
                        # Columns are c01, c02... c64
                        self.grid_data = [row[f"c{i+1:02d}"] for i in range(64)]
                        print(f"Loaded existing labels for {self.current_image_name}")
                except Exception as e:
                    print(f"Error loading existing labels: {e}") 
            
            self.draw_grid()
            self.lbl_status.config(text=f"Image {self.current_img_index + 1}/{len(self.image_list)}: {self.current_image_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def draw_grid(self):
        # Clear existing rectangles/lines (keep image which is item 1)
        self.canvas.delete("grid_line")
        self.canvas.delete("grid_rect")
        
        cell_w = IMG_WIDTH / GRID_COLS
        cell_h = IMG_HEIGHT / GRID_ROWS
        
        # Draw active cells
        for idx, val in enumerate(self.grid_data):
            if val != 0:
                row = idx // GRID_COLS
                col = idx % GRID_COLS
                x1 = col * cell_w
                y1 = row * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                
                # Use pre-created transparent image
                if val in self.overlay_images:
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.overlay_images[val], tags="grid_rect")
                
                # Draw text label
                self.canvas.create_text(x1+10, y1+10, text=str(val), fill="white", tags="grid_rect")

        # Draw Grid Lines
        for i in range(1, GRID_COLS):
            x = i * cell_w
            self.canvas.create_line(x, 0, x, IMG_HEIGHT, fill="yellow", tags="grid_line")
            
        for i in range(1, GRID_ROWS):
            y = i * cell_h
            self.canvas.create_line(0, y, IMG_WIDTH, y, fill="yellow", tags="grid_line")

    def on_canvas_click(self, event):
        if not self.image_list:
            return
            
        # Determine cell
        cell_w = IMG_WIDTH / GRID_COLS
        cell_h = IMG_HEIGHT / GRID_ROWS
        
        col = int(event.x // cell_w)
        row = int(event.y // cell_h)
        
        # Calculate flat index (0-63)
        index = row * GRID_COLS + col
        
        if 0 <= index < 64:
            # Toggle class: 0 -> 1 -> 2 -> 3 -> 0
            self.grid_data[index] = (self.grid_data[index] + 1) % 4
            self.draw_grid()

    def save_and_next(self):
        if not self.image_list:
            return
            
        # Skip saving if image was rejected
        if getattr(self, 'current_pil_img', None) is None:
            print(f"Skipping rejected image: {self.current_image_name}")
            # Move to next
            if self.current_img_index < len(self.image_list) - 1:
                self.current_img_index += 1
                self.load_current_image()
            else:
                messagebox.showinfo("Done", "All images processed!")
            return

        # Prepare Data Row
        row_dict = {
            "ImageFileName": self.current_image_name,
            "TrainOrTest": "Train" 
        }
        
        for i in range(64):
            # Formats column name as c01, c02... c64
            col_name = f"c{i+1:02d}"
            row_dict[col_name] = self.grid_data[i]
            
        df_new = pd.DataFrame([row_dict])
        
        # --- SAVE VISUALIZED IMAGE ---
        try:
            # Create a copy of the base image to draw on
            save_img = self.current_pil_img.copy()
            
            cell_w = int(IMG_WIDTH / GRID_COLS)
            cell_h = int(IMG_HEIGHT / GRID_ROWS)
            
            for idx, val in enumerate(self.grid_data):
                if val != 0 and val in self.overlay_images_pil:
                    row = idx // GRID_COLS
                    col = idx % GRID_COLS
                    x = col * cell_w
                    y = row * cell_h
                    
                    # Paste the overlay
                    save_img.paste(self.overlay_images_pil[val], (x, y), self.overlay_images_pil[val])
            
            # Draw Grid Lines
            draw = ImageDraw.Draw(save_img)
            # Vertical
            for i in range(1, GRID_COLS):
                x = i * cell_w
                draw.line([(x, 0), (x, IMG_HEIGHT)], fill="yellow", width=1)
            # Horizontal
            for i in range(1, GRID_ROWS):
                y = i * cell_h
                draw.line([(0, y), (IMG_WIDTH, y)], fill="yellow", width=1)

            # Draw Cell Numbers
            for i in range(64):
                row = i // GRID_COLS
                col = i % GRID_COLS
                x = col * cell_w + 2
                y = row * cell_h + 2
                draw.text((x, y), str(i+1), fill="white")

            # Save to processed_images (convert back to RGB to remove alpha channel if saving as jpg)
            # Save CLEAN image (resized, no overlay) to Processed_image
            clean_save_path = os.path.join(CLEAN_DIR, self.current_image_name)
            self.current_pil_img.convert("RGB").save(clean_save_path)

            # Save REFERENCE image (with overlay) to Reference_Images
            ref_save_path = os.path.join(REFERENCE_DIR, self.current_image_name)
            save_img.convert("RGB").save(ref_save_path)
            
        except Exception as e:
            print(f"Error saving visualized image: {e}")

        # Append to CSV
        
        # Update or Append to CSV
        if os.path.exists(OUTPUT_CSV):
            try:
                df = pd.read_csv(OUTPUT_CSV)
                
                # Check if image already exists
                if self.current_image_name in df["ImageFileName"].values:
                    print(f"Updating existing entry for {self.current_image_name}")
                    # Update existing row
                    # We need to ensure we update all columns
                    for col, val in row_dict.items():
                        df.loc[df["ImageFileName"] == self.current_image_name, col] = val
                else:
                    # Append new row
                    df_new = pd.DataFrame([row_dict])
                    df = pd.concat([df, df_new], ignore_index=True)
                
                df.to_csv(OUTPUT_CSV, index=False)
                
            except Exception as e:
                print(f"Error reading/writing CSV: {e}")
                # Fallback to append if read fails (e.g. empty file)
                df_new = pd.DataFrame([row_dict])
                df_new.to_csv(OUTPUT_CSV, mode='a', header=False, index=False)
        else:
            # Create new file
            df_new = pd.DataFrame([row_dict])
            df_new.to_csv(OUTPUT_CSV, index=False)
            
        print(f"Saved {self.current_image_name}")
        
        # Move to next
        if self.current_img_index < len(self.image_list) - 1:
            self.current_img_index += 1
            self.load_current_image()
        else:
            messagebox.showinfo("Done", "All images processed!")

    def prev_image(self):
        if self.current_img_index > 0:
            self.current_img_index -= 1
            self.load_current_image()

    def skip_image(self):
        if self.current_img_index < len(self.image_list) - 1:
            self.current_img_index += 1
            self.load_current_image()
        else:
            messagebox.showinfo("Done", "All images processed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CricketLabeler(root)
    root.mainloop()
