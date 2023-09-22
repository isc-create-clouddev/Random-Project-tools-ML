This Python script provides a simple GUI to annotate images with bounding boxes and text labels and deploy it as a usable .jsonl file for dataset deployment in Vertex AI. It is built using the tkinter and PIL libraries, with additional features from the os, json, and cv2 libraries.

Getting Started

Before you run the script, make sure to install the necessary Python modules. You can do this by running the following command in your terminal:
pip install pillow opencv-python-headless


How to Use application:

1. Run the Script

Run the script by executing it in a Python environment. The GUI will appear, and you can start labeling your images.

To execute the script, navigate to the directory where the script is located in your terminal and run the following command:

python Label.py

2. Choose Image Directory

Click this button to select the directory containing the images you want to annotate with bounding boxes and Labels.

3. Labeled Image Output

Click this button to select the directory where labeled images will be saved.

4. Provide a Text Label to be Applied

Click this button to input a text label that will be applied to the bounding box.

5. Change Mode

Toggle between "Fast" and "Manual" modes for drawing bounding boxes.
Fast Mode: Draw a bounding box by clicking to start, dragging, and releasing to finish.
Manual Mode: Draw a bounding box by clicking to start, dragging, and pressing "Enter" when finished. The "Clear" button becomes visible in this mode to clear the bounding box if needed.

6. Apply JSONL Format

Click this button to save the annotated data in JSONL format. You will be prompted to specify the file name and location. Note that script needs to be modified to point to correct bucket URI. Currently the .jsonl file is default and needs to be updated before the script is ran if needed.

I hope this helps! Let me know if there's anything else you'd like to add or modify. Currently working on a multi label mode where multiple annotations can be added to a single image. Implementing feature that saves the images coordinates in 4 rotations of image to create more complex datasets.
