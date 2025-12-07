import os
import cv2
import numpy as np
import pandas as pd
from skimage.feature import hog
from skimage.feature import local_binary_pattern

# Configuration
IMG_WIDTH = 800
IMG_HEIGHT = 600
GRID_ROWS = 8
GRID_COLS = 8
CELL_W = IMG_WIDTH // GRID_COLS
CELL_H = IMG_HEIGHT // GRID_ROWS
PROCESSED_DIR = "processed_images"
LABELS_FILE = "labels.csv"

def extract_features(df):
    features_list = []
    labels_list = []
    meta_list = []

    print("Starting feature extraction...")

    for idx, row in df.iterrows():
        img_name = row['ImageFileName']
        img_path = os.path.join(PROCESSED_DIR, img_name)

        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue

        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to read image: {img_path}")
            continue
            
        # FIX 1: Resize image to ensure consistent dimensions
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        for i in range(64):
            label = row[f"c{i+1:02d}"]
            
            r = i // GRID_COLS
            c = i % GRID_COLS

            x1 = c * CELL_W
            y1 = r * CELL_H
            x2 = x1 + CELL_W
            y2 = y1 + CELL_H

            cell = img[y1:y2, x1:x2]

            # --- Feature 1: HOG ---
            fd = hog(cell, orientations=9, pixels_per_cell=(8, 8),
                     cells_per_block=(2, 2), visualize=False, channel_axis=-1)

            # --- Feature 2: Color Histogram ---
            hist_features = []
            for ch in range(3):
                hist = cv2.calcHist([cell], [ch], None, [32], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                hist_features.extend(hist)

            # --- Feature 3: Shape Counts ---
            gray = cv2.cvtColor(cell, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, minLineLength=20, maxLineGap=10)
            num_lines = len(lines) if lines is not None else 0

            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                       param1=50, param2=30, minRadius=5, maxRadius=50)
            # Check if circles is None before accessing index
            num_circles = len(circles[0, :]) if circles is not None else 0

            # --- Feature 4: LBP (Texture) ---
            # P=8, R=1. Method='uniform' gives 10 bins for P=8
            lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
            
            # FIX 2: Fixed n_bins to 10 for P=8 uniform LBP
            n_bins = 10
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)

            # Combine
            combined = np.concatenate([fd, hist_features, [num_lines, num_circles], lbp_hist])

            features_list.append(combined)
            labels_list.append(label)
            meta_list.append((img_name, i))

    return np.array(features_list), np.array(labels_list), meta_list

if __name__ == "__main__":
    if os.path.exists(LABELS_FILE):
        df = pd.read_csv(LABELS_FILE)
        # Test on a small subset
        df_subset = df.head(3) 
        try:
            X, y, meta = extract_features(df_subset)
            print("Feature extraction successful!")
            print(f"Feature matrix shape: {X.shape}")
        except Exception as e:
            print(f"Error during feature extraction: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Labels file not found: {LABELS_FILE}")
