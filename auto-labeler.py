from ultralytics import YOLOWorld
import cv2
import pandas as pd
import os
import glob
import numpy as np
from PIL import Image

# --- CONFIGURATION ---
IMAGE_FOLDER = "raw_images"
OUTPUT_CSV = "auto_labels.csv"
PROCESSED_DIR = "processed_images"
CONFIDENCE_THRESHOLD = 0.15
IOU_THRESHOLD = 0.15

# Project Logic: 800x600 image, 8x8 grid
IMG_W, IMG_H = 800, 600
ROWS, COLS = 8, 8
CELL_W = int(IMG_W / COLS)
CELL_H = int(IMG_H / ROWS)

# Class Mapping
CLASS_MAP = {
    0: 1,  # Ball
    1: 2,  # Bat
    2: 3   # Stump
}

# Colors for visualization (BGR)
COLORS = {
    1: (0, 0, 255),   # Red (Ball)
    2: (255, 0, 0),   # Blue (Bat)
    3: (0, 255, 0)    # Green (Stump)
}

def get_intersection_area(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    if xB > xA and yB > yA:
        return (xB - xA) * (yB - yA)
    return 0

def process_images():
    # Ensure processed directory exists
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    # 1. Load YOLO-World
    print("Loading YOLO-World model...")
    model = YOLOWorld("yolov8s-world.pt")
    model.set_classes(["cricket ball", "cricket bat", "cricket stump"])

    # 2. Prepare Data List
    csv_data = []
    
    all_files = glob.glob(os.path.join(IMAGE_FOLDER, "*"))
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    image_files = [f for f in all_files if os.path.splitext(f)[1].lower() in valid_extensions]
    
    print(f"Found {len(image_files)} valid images.")

    if len(image_files) == 0:
        print("ERROR: No images found! Check your 'raw_images' folder.")
        return

    for img_path in image_files:
        filename = os.path.basename(img_path)
        
        try:
            pil_img = Image.open(img_path)
            pil_img = pil_img.convert("RGB") 
            img = np.array(pil_img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"WARNING: Corrupt file {filename}. Error: {e}")
            continue
            
        # Resize
        img = cv2.resize(img, (IMG_W, IMG_H))
        
        # Run Inference
        results = model.predict(img, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        grid_labels = [0] * 64
        
        # Process Detections
        for box in results[0].boxes.data.tolist():
            x1, y1, x2, y2, conf, cls_idx = box
            project_label = CLASS_MAP.get(int(cls_idx), 0)
            detected_box = [x1, y1, x2, y2]
            
            for i in range(64):
                row = i // COLS
                col = i % COLS
                cell_x1 = col * CELL_W
                cell_y1 = row * CELL_H
                cell_x2 = cell_x1 + CELL_W
                cell_y2 = cell_y1 + CELL_H
                cell_box = [cell_x1, cell_y1, cell_x2, cell_y2]
                
                intersection = get_intersection_area(detected_box, cell_box)
                cell_area = CELL_W * CELL_H
                
                if (intersection / cell_area) > IOU_THRESHOLD:
                    if grid_labels[i] == 0:
                        grid_labels[i] = project_label

        # --- VISUALIZATION ---
        overlay = img.copy()
        alpha = 0.27 # Approx 70/255
        
        for i, label in enumerate(grid_labels):
            if label != 0:
                row = i // COLS
                col = i % COLS
                x1 = col * CELL_W
                y1 = row * CELL_H
                x2 = x1 + CELL_W
                y2 = y1 + CELL_H
                
                color = COLORS.get(label, (255, 255, 255))
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1) # -1 fills the rectangle
                
        # Blend overlay with original image
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # Save processed image
        save_path = os.path.join(PROCESSED_DIR, filename)
        cv2.imwrite(save_path, img)

        # Save Row
        row_dict = {
            "ImageFileName": filename,
            "TrainOrTest": "Train",
        }
        for i in range(64):
            row_dict[f"c{i+1:02d}"] = grid_labels[i]
            
        csv_data.append(row_dict)
        print(f"Processed: {filename}")

    # 3. Save to CSV
    if not csv_data:
        print("ERROR: No data generated.")
        return

    df = pd.DataFrame(csv_data)
    cols = ["ImageFileName", "TrainOrTest"] + [f"c{i+1:02d}" for i in range(64)]
    df = df[cols]
    
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Done! Labels saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    process_images()