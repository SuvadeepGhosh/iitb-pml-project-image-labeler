# Cricket Image Labeler

A simple tool to label cricket images with an 8x8 grid overlay.

## Setup

1.  **Images**: Place your raw cricket images (jpg, png, etc.) in the `raw_images` folder.
2.  **Dependencies**: Ensure you have Python installed along with the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: `tkinter` is usually included with Python, but if you get an error, you may need to install it separately, e.g., `brew install python-tk` on Mac).

## Usage

1.  Run the tool:
    ```bash
    python3 labeler.py
    ```
2.  Click **"Load Images Folder"**. It defaults to `raw_images`.
3.  **Labeling**:
    *   Click on grid cells to toggle the label:
        *   **Red**: Ball
        *   **Blue**: Bat
        *   **Green**: Stump
        *   (Click again to clear)
4.  **Navigation**:
    *   Click **"Save & Next >>"** to save the labels to `labels.csv` and move to the next image.
    *   The tool automatically resizes images to 800x600 and saves a copy in `processed_images`.

## Output

*   **`labels.csv`**: Contains the labels for each image.
    *   Format: `ImageFileName, TrainOrTest, c01, c02, ..., c64`
    *   Values: 0 (None), 1 (Ball), 2 (Bat), 3 (Stump)
*   **`processed_images/`**: Contains the resized (800x600) images corresponding to the labels.
