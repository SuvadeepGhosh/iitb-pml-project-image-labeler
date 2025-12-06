import os
import cv2
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw

# Configuration
PREDICTIONS_FILE = "predicted_labels.csv"
PROCESSED_DIR = "processed_images"
OUTPUT_DIR = "predicted_images"
GRID_ROWS = 8
GRID_COLS = 8
IMG_WIDTH = 800
IMG_HEIGHT = 600

# Color mapping (Same as labeler.py)
COLORS = {
    1: (255, 0, 0),   # Red (Ball)
    2: (0, 0, 255),   # Blue (Bat)
    3: (0, 255, 0)    # Green (Stump)
}
ALPHA = 70

def create_overlay_image(width, height, color, alpha):
    return Image.new("RGBA", (width, height), color + (alpha,))

def visualize_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        print(f"Error: {PREDICTIONS_FILE} not found. Please run the notebook to generate predictions first.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.read_csv(PREDICTIONS_FILE)
    print(f"Found predictions for {len(df)} images.")
    
    cell_w = int(IMG_WIDTH / GRID_COLS)
    cell_h = int(IMG_HEIGHT / GRID_ROWS)
    
    # Pre-create overlays
    overlays = {k: create_overlay_image(cell_w, cell_h, v, ALPHA) for k, v in COLORS.items()}

    for _, row in df.iterrows():
        img_name = row['ImageFileName']
        img_path = os.path.join(PROCESSED_DIR, img_name)
        
        if not os.path.exists(img_path):
            print(f"Warning: Image {img_name} not found in {PROCESSED_DIR}")
            continue
            
        # Load image using PIL to handle transparency easily
        try:
            base_img = Image.open(img_path).convert("RGBA")
            # Ensure it's the right size (it should be if from processed_images)
            base_img = base_img.resize((IMG_WIDTH, IMG_HEIGHT))
            
            # Create a drawing context for lines/text
            draw = ImageDraw.Draw(base_img)
            
            # Draw overlays based on predictions
            for i in range(64):
                col_name = f"c{i+1:02d}"
                label = row.get(col_name, 0)
                
                if label in overlays:
                    r = i // GRID_COLS
                    c = i % GRID_COLS
                    x = c * cell_w
                    y = r * cell_h
                    
                    # Paste overlay
                    base_img.paste(overlays[label], (x, y), overlays[label])
            
            # Draw Grid Lines (Yellow)
            for i in range(1, GRID_COLS):
                x = i * cell_w
                draw.line([(x, 0), (x, IMG_HEIGHT)], fill="yellow", width=1)
            for i in range(1, GRID_ROWS):
                y = i * cell_h
                draw.line([(0, y), (IMG_WIDTH, y)], fill="yellow", width=1)
                
            # Draw Cell Numbers (White)
            for i in range(64):
                r = i // GRID_COLS
                c = i % GRID_COLS
                x = c * cell_w + 2
                y = r * cell_h + 2
                draw.text((x, y), str(i+1), fill="white")
                
            # Save
            out_path = os.path.join(OUTPUT_DIR, img_name)
            base_img.convert("RGB").save(out_path)
            # print(f"Saved {out_path}")
            
        except Exception as e:
            print(f"Error processing {img_name}: {e}")

    print(f"Done! Visualizations saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    visualize_predictions()
