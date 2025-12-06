# Cricket Image Labeler & Feature Extraction Suite

A comprehensive toolkit for labeling cricket images, visualizing computer vision features, and extracting datasets for machine learning.

## Setup

1.  **Images**: Place your raw cricket images (jpg, png, etc.) in the `raw_images` folder.
2.  **Dependencies**: Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: `tkinter` is required for the GUI tools. It is usually included with Python, but on some systems like Mac, you might need `brew install python-tk`)*.

## Tools Overview

### 1. Image Labeler (`labeler.py`)
The primary tool for manually labeling images.
*   **Usage**: `python3 labeler.py`
*   **Features**:
    *   Loads images from `raw_images`.
    *   Displays an 8x8 grid (configurable).
    *   **Click to Label**: Red (Ball), Blue (Bat), Green (Stump).
    *   **Skip**: Skip images without saving.
    *   **Save & Next**: Saves labels to `labels.csv`, clean images to `processed_images/`, and overlaid images to `labeled_images/`.
    *   **Resume**: Automatically loads existing labels if an image was previously processed.

### 2. Auto Labeler (`auto-labeler.py`)
Uses YOLO-World to automatically detect objects and generate labels.
*   **Usage**: `python3 auto-labeler.py`
*   **Output**: Generates `auto_labels.csv` and visualized images.

### 3. Image Scraper (`scraper.py`)
A Selenium-based scraper to download cricket images from the web.
*   **Usage**: `python3 scraper.py`
*   **Note**: Requires Chrome/Chromium.

### 4. Feature Visualizers
A suite of tools to inspect computer vision features for individual grid cells. All tools support folder navigation.

*   **HOG Visualizer** (`hog_visualizer.py`):
    *   Visualizes Histogram of Oriented Gradients (HOG) for texture/shape analysis.
*   **Color Visualizer** (`color_visualizer.py`):
    *   Displays RGB histograms to analyze color distribution.
*   **Convolution Visualizer** (`convolution_visualizer.py`):
    *   Shows the effect of Edge Detection, Sharpening, and Box Blur kernels.
*   **Shape Visualizer** (`shape_visualizer.py`):
    *   Visualizes Canny Edges, Hough Lines (for bats/stumps), and Hough Circles (for balls).
*   **Feature Comparison** (`feature_comparison_visualizer.py`):
    *   **All-in-one tool**: Side-by-side comparison of HOG and Color features across Original, Edge, Sharpen, and Blur versions of a cell.

### 5. Feature Extractor (`feature_extractor.py`)
Generates the final dataset for machine learning.
*   **Usage**: `python3 feature_extractor.py`
*   **Input**: Reads `labels.csv` and processed images.
*   **Output**: Saves `features.csv` containing high-dimensional feature vectors for every cell.
    *   **Features**: HOG (8x8 cells), Color Histograms (32 bins), Convolution Histograms (16 bins), Shape Counts.
    *   **Dimensions**: ~3,314 features per cell.

## Output Files

*   **`labels.csv` / `auto_labels.csv`**: Ground truth labels.
*   **`features.csv`**: The feature matrix for training ML models.
*   **`processed_images/`**: Clean, resized (800x600) images used for training.
*   **`labeled_images/`**: Images with grid overlays, cell numbers, and labels for visual verification.
