import os
import cv2
import pandas as pd
import numpy as np

# Configuration
PREDICTIONS_FILE = "predicted_labels.csv"
PROCESSED_DIR = "processed_images"
OUTPUT_DIR = "prediction_visualizations"
GRID_ROWS = 8
GRID_COLS = 8
CELL_W = 128
CELL_H = 128
LABELS = {1: 'Bat', 2: 'Ball', 3: 'Stump'}

def visualize_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        print(f"Error: {PREDICTIONS_FILE} not found. Please run the notebook to generate predictions first.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = pd.read_csv(PREDICTIONS_FILE)
    
    # Group predictions by image
    grouped = df.groupby('ImageFileName')
    
    print(f"Found predictions for {len(grouped)} images.")
    
    for img_name, group in grouped:
        img_path = os.path.join(PROCESSED_DIR, img_name)
        if not os.path.exists(img_path):
            print(f"Warning: Image {img_name} not found in {PROCESSED_DIR}")
            continue
            
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        # Draw predictions
        for _, row in group.iterrows():
            cell_idx = int(row['CellIndex'])
            true_lbl = int(row['TrueLabel'])
            pred_lbl = int(row['PredictedLabel'])
            
            # Calculate cell coordinates
            r = cell_idx // GRID_COLS
            c = cell_idx % GRID_COLS
            
            x1 = c * CELL_W
            y1 = r * CELL_H
            x2 = x1 + CELL_W
            y2 = y1 + CELL_H
            
            # Determine color (Green for correct, Red for incorrect)
            if true_lbl == pred_lbl:
                color = (0, 255, 0) # Green
                thickness = 2
            else:
                color = (0, 0, 255) # Red
                thickness = 3
                
            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
            
            # Add label text
            # T: True, P: Pred
            label_text = f"T:{LABELS.get(true_lbl, str(true_lbl))} P:{LABELS.get(pred_lbl, str(pred_lbl))}"
            
            # Text background for readability
            (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x1, y1), (x1 + w, y1 + h + 5), color, -1)
            
            # Text color (Black for contrast)
            cv2.putText(img, label_text, (x1, y1 + h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
        # Save annotated image
        out_path = os.path.join(OUTPUT_DIR, f"pred_{img_name}")
        cv2.imwrite(out_path, img)
        print(f"Saved visualization to {out_path}")

if __name__ == "__main__":
    visualize_predictions()
