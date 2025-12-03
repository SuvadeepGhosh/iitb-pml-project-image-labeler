import pandas as pd
import numpy as np
import cv2
import os
import csv  # Added for efficient writing
from PIL import Image
from skimage.feature import hog
import warnings

warnings.filterwarnings("ignore")

# Configuration
IMG_WIDTH = 800
IMG_HEIGHT = 600
GRID_ROWS = 8
GRID_COLS = 8
LABELS_CSV = "labels.csv"
OUTPUT_CSV = "features1.csv"
RAW_IMAGES_DIR = "processed_images"

def extract_features():
    if not os.path.exists(LABELS_CSV):
        print(f"Error: {LABELS_CSV} not found.")
        return

    df_labels = pd.read_csv(LABELS_CSV)
    
    # Define Kernels
    kernel_edge = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    kernel_sharpen = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    kernel_blur = np.ones((5, 5), np.float32) / 25

    # --- PREPARE CSV HEADER ONCE ---
    # We calculate the header mathematically to avoid doing it inside the loop
    header = ["ImageName", "CellIndex", "Label"]
    header += [f"HOG_{i}" for i in range(3168)]
    header += [f"Color_{i}" for i in range(96)]
    header += [f"Conv_{i}" for i in range(48)]
    header += ["Shape_Lines", "Shape_Circles"]

    # Open CSV in write mode and write header
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        total_images = len(df_labels)
        print(f"Found {total_images} images. Writing to {OUTPUT_CSV} incrementally...")

        for idx, row in df_labels.iterrows():
            filename = row['ImageFileName']
            filepath = os.path.join(RAW_IMAGES_DIR, filename)
            
            if not os.path.exists(filepath):
                continue
                
            if idx % 10 == 0:
                print(f"Processing {idx}/{total_images}...")
            
            try:
                # Load and Resize
                pil_img = Image.open(filepath)
                pil_img = pil_img.resize((IMG_WIDTH, IMG_HEIGHT), Image.Resampling.LANCZOS)
                img_rgb = np.array(pil_img.convert("RGB"))
                img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
                
                cell_w = int(IMG_WIDTH / GRID_COLS)
                cell_h = int(IMG_HEIGHT / GRID_ROWS)
                
                for i in range(64):
                    # Data Row Container
                    data_row = [filename, i, row[f"c{i+1:02d}"]]

                    # Coords
                    r, c = divmod(i, GRID_COLS)
                    x1, y1 = c * cell_w, r * cell_h
                    x2, y2 = x1 + cell_w, y1 + cell_h
                    
                    cell_rgb = img_rgb[y1:y2, x1:x2]
                    cell_gray = img_gray[y1:y2, x1:x2]
                    
                    # 1. HOG (Returns flat array by default)
                    fd_hog = hog(cell_gray, orientations=9, pixels_per_cell=(8, 8),
                                 cells_per_block=(2, 2), visualize=False, feature_vector=True)
                    data_row.extend(fd_hog) # Efficient extension
                    
                    # 2. Color
                    hist_r, _ = np.histogram(cell_rgb[:, :, 0], bins=32, range=(0, 256), density=True)
                    hist_g, _ = np.histogram(cell_rgb[:, :, 1], bins=32, range=(0, 256), density=True)
                    hist_b, _ = np.histogram(cell_rgb[:, :, 2], bins=32, range=(0, 256), density=True)
                    data_row.extend(hist_r)
                    data_row.extend(hist_g)
                    data_row.extend(hist_b)
                    
                    # 3. Convolution (Fixed for negative values)
                    # Use CV_32F to capture negative edges, then Abs, then convert to 8-bit
                    conv_edge = cv2.filter2D(cell_gray, cv2.CV_32F, kernel_edge)
                    conv_edge = cv2.convertScaleAbs(conv_edge) 
                    
                    conv_sharpen = cv2.filter2D(cell_gray, cv2.CV_32F, kernel_sharpen)
                    conv_sharpen = cv2.convertScaleAbs(conv_sharpen)

                    conv_blur = cv2.filter2D(cell_gray, -1, kernel_blur) # Blur is always positive
                    
                    hist_edge, _ = np.histogram(conv_edge, bins=16, range=(0, 256), density=True)
                    hist_sharpen, _ = np.histogram(conv_sharpen, bins=16, range=(0, 256), density=True)
                    hist_blur, _ = np.histogram(conv_blur, bins=16, range=(0, 256), density=True)
                    
                    data_row.extend(hist_edge)
                    data_row.extend(hist_sharpen)
                    data_row.extend(hist_blur)
                    
                    # 4. Shape
                    edges = cv2.Canny(cell_gray, 50, 150)
                    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=20, maxLineGap=10)
                    num_lines = len(lines) if lines is not None else 0
                    
                    circles = cv2.HoughCircles(cell_gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                               param1=50, param2=30, minRadius=5, maxRadius=50)
                    num_circles = circles.shape[1] if circles is not None else 0
                    
                    data_row.append(num_lines)
                    data_row.append(num_circles)
                    
                    # Write row immediately
                    writer.writerow(data_row)
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("Done!")

if __name__ == "__main__":
    extract_features()
