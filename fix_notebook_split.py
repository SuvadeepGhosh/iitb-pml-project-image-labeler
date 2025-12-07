import json
import os

notebook_path = 'cricket_classification.ipynb'

with open(notebook_path, 'r') as f:
    nb = json.load(f)

# Update train_test_split cell
found = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'train_test_split' in ''.join(cell['source']):
        new_source = []
        for line in cell['source']:
            if 'train_test_split(X, y' in line:
                # Replace the line with the correct one including meta
                new_source.append("X_train, X_test, y_train, y_test, meta_train, meta_test = train_test_split(X, y, meta, test_size=0.2, random_state=42)\n")
                found = True
            else:
                new_source.append(line)
        cell['source'] = new_source
        if found:
            break

if found:
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=1)
    print("Notebook updated successfully: Fixed train_test_split.")
else:
    print("Error: Could not find train_test_split cell to update.")
