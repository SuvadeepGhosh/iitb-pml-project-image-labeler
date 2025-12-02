import pandas as pd
import numpy as np
import cv2
import os
from PIL import Image
from skimage.feature import hog
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Configuration
IMG_WIDTH = 800
IMG_HEIGHT = 600
GRID_ROWS = 8
GRID_COLS = 8
LABELS_CSV = "labels.csv"
OUTPUT_CSV = "features.csv"
RAW_IMAGES_DIR = "raw_images"

def extract_features():
    if not os.path.exists(LABELS_CSV):
        print(f"Error: {LABELS_CSV} not found.")
        return

    print("Loading labels...")
    df_labels = pd.read_csv(LABELS_CSV)
    
    all_features = []
    
    # Define Kernels for Convolution Features
    kernel_edge = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    kernel_sharpen = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    kernel_blur = np.ones((5, 5), np.float32) / 25

    total_images = len(df_labels)
    print(f"Found {total_images} labeled images. Starting extraction...")

    for idx, row in df_labels.iterrows():
        filename = row['ImageFileName']
        filepath = os.path.join(RAW_IMAGES_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"Warning: Image {filename} not found in {RAW_IMAGES_DIR}. Skipping.")
            continue
            
        print(f"Processing {idx+1}/{total_images}: {filename}")
        
        try:
            # Load and Resize
            pil_img = Image.open(filepath)
            pil_img = pil_img.resize((IMG_WIDTH, IMG_HEIGHT), Image.Resampling.LANCZOS)
            img_rgb = np.array(pil_img.convert("RGB"))
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            
            cell_w = int(IMG_WIDTH / GRID_COLS)
            cell_h = int(IMG_HEIGHT / GRID_ROWS)
            
            for i in range(64):
                # Get Label
                label = row[f"c{i+1:02d}"]
                
                # Calculate coordinates
                r = i // GRID_COLS
                c = i % GRID_COLS
                x1 = c * cell_w
                y1 = r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h
                
                # Extract Cell
                cell_rgb = img_rgb[y1:y2, x1:x2]
                cell_gray = img_gray[y1:y2, x1:x2]
                
                # --- 1. HOG Features ---
                # Using fewer pixels per cell to get a reasonable vector size
                # 8x8 pixels per cell, 2x2 cells per block, 9 orientations
                # Cell size is 100x75. 
                # 100/8 = 12, 75/8 = 9. Blocks approx (11, 8). Vector size ~ 11*8*2*2*9 = 3168 (large!)
                # Let's increase pixels_per_cell to reduce vector size for this CSV
                # 16x16 pixels -> 6x4 blocks. Vector ~ 5*3*4*9 = 540. More manageable.
                fd_hog = hog(cell_gray, orientations=9, pixels_per_cell=(16, 16),
                             cells_per_block=(2, 2), visualize=False, channel_axis=None)
                
                # --- 2. Color Histogram Features ---
                # 8 bins per channel -> 24 features
                hist_r, _ = np.histogram(cell_rgb[:, :, 0], bins=8, range=(0, 256), density=True)
                hist_g, _ = np.histogram(cell_rgb[:, :, 1], bins=8, range=(0, 256), density=True)
                hist_b, _ = np.histogram(cell_rgb[:, :, 2], bins=8, range=(0, 256), density=True)
                color_feats = np.concatenate([hist_r, hist_g, hist_b])
                
                # --- 3. Convolution Features ---
                # Apply kernels and take Mean and Variance
                conv_edge = cv2.filter2D(cell_gray, -1, kernel_edge)
                conv_sharpen = cv2.filter2D(cell_gray, -1, kernel_sharpen)
                conv_blur = cv2.filter2D(cell_gray, -1, kernel_blur)
                
                conv_feats = [
                    np.mean(conv_edge), np.var(conv_edge),
                    np.mean(conv_sharpen), np.var(conv_sharpen),
                    np.mean(conv_blur), np.var(conv_blur)
                ]
                
                # --- 4. Shape Features ---
                # Canny
                edges = cv2.Canny(cell_gray, 50, 150)
                
                # Hough Lines
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=20, maxLineGap=10)
                num_lines = len(lines) if lines is not None else 0
                
                # Hough Circles
                circles = cv2.HoughCircles(cell_gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                           param1=50, param2=30, minRadius=5, maxRadius=50)
                num_circles = circles.shape[1] if circles is not None else 0
                
                shape_feats = [num_lines, num_circles]
                
                # --- Combine All ---
                # Create a dictionary for the row
                feature_row = {
                    "ImageName": filename,
                    "CellIndex": i,
                    "Label": label
                }
                
                # Add HOG
                for j, val in enumerate(fd_hog):
                    feature_row[f"HOG_{j}"] = val
                    
                # Add Color
                for j, val in enumerate(color_feats):
                    feature_row[f"Color_{j}"] = val
                    
                # Add Conv
                feature_row["Conv_Edge_Mean"] = conv_feats[0]
                feature_row["Conv_Edge_Var"] = conv_feats[1]
                feature_row["Conv_Sharpen_Mean"] = conv_feats[2]
                feature_row["Conv_Sharpen_Var"] = conv_feats[3]
                feature_row["Conv_Blur_Mean"] = conv_feats[4]
                feature_row["Conv_Blur_Var"] = conv_feats[5]
                
                # Add Shape
                feature_row["Shape_Lines"] = shape_feats[0]
                feature_row["Shape_Circles"] = shape_feats[1]
                
                all_features.append(feature_row)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Create DataFrame
    print("Creating DataFrame...")
    df_features = pd.DataFrame(all_features)
    
    # Save to CSV
    print(f"Saving to {OUTPUT_CSV}...")
    df_features.to_csv(OUTPUT_CSV, index=False)
    print("Done!")

if __name__ == "__main__":
    extract_features()
