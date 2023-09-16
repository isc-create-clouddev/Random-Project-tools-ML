import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import json
import cv2

class LabelingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Label jobs")

        self.label_text = tk.StringVar(value="No label")
        self.mode = tk.StringVar(value="Fast")

        self.setup_UI()

        self.image_index = 0
        self.output_dir = ""
        self.label = ""
        self.annotations = []

    def setup_UI(self):
        self.choose_dir_button = tk.Button(self.master, text="Choose image directory", command=self.load_images)
        self.choose_dir_button.pack(pady=10)

        self.output_dir_button = tk.Button(self.master, text="Labeled image output", command=self.choose_output_dir)
        self.output_dir_button.pack(pady=10)

        self.output_dir_label = tk.Label(self.master, text="Labeled images will be saved here: ")
        self.output_dir_label.pack(pady=10)

        self.label_input_button = tk.Button(self.master, text="Provide a text label to be applied", command=self.input_label)
        self.label_input_button.pack(pady=10)

        self.label_display_label = tk.Label(self.master, textvariable=self.label_text)
        self.label_display_label.pack(pady=10)

        self.mode_label = tk.Label(self.master, textvariable=self.mode)
        self.mode_label.pack(pady=10)

        self.mode_button = tk.Button(self.master, text="Change Mode", command=self.change_mode)
        self.mode_button.pack(pady=10)

        self.clear_button = tk.Button(self.master, text="Clear", command=self.clear_canvas)
        self.clear_button.pack(pady=10)
        self.clear_button.pack_forget()

        self.jsonl_button = tk.Button(self.master, text="Apply JSONL format", command=self.save_as_jsonl)
        self.jsonl_button.pack(pady=10)

        self.image_canvas = tk.Canvas(self.master)
        self.image_canvas.pack()

    def load_images(self):
        self.image_dir = filedialog.askdirectory()
        self.image_paths = [os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir) if f.endswith((".jpg", ".jpeg"))]
        self.load_image()

    def load_image(self):
        if self.image_index < len(self.image_paths):
            self.image = Image.open(self.image_paths[self.image_index])
            self.image.thumbnail((800, 600))
            self.image_width, self.image_height = self.image.size
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.image_canvas.config(width=self.image_width, height=self.image_height)
            self.image_canvas.create_image(self.image_width//2, self.image_height//2, anchor="center", image=self.image_tk)
            self.image_canvas.bind("<ButtonPress-1>", self.on_click)
            self.image_canvas.bind("<B1-Motion>", self.on_drag)
            self.image_canvas.bind("<ButtonRelease-1>", self.on_release)
            self.master.bind("<Return>", self.save_labeled_image)
        else:
            messagebox.showinfo("Information", "All images have been labeled")

    def choose_output_dir(self):
        self.output_dir = filedialog.askdirectory()
        self.output_dir_label.config(text="Labeled images will be saved here: " + self.output_dir)

    def input_label(self):
        self.label = simpledialog.askstring("Input", "Please enter a label:")
        self.label_text.set("Current label: " + self.label)

    def change_mode(self):
        if self.mode.get() == "Fast":
            self.mode.set("Manual")
            self.clear_button.pack()
        else:
            self.mode.set("Fast")
            self.clear_button.pack_forget()

    def on_click(self, event):
        self.start_x = self.image_canvas.canvasx(event.x)
        self.start_y = self.image_canvas.canvasy(event.y)
        if self.mode.get() == "Manual":
            if hasattr(self, 'rect'):
                self.image_canvas.delete(self.rect)
            self.rect = self.image_canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="lime", width=2)

    def on_drag(self, event):
        if self.mode.get() == "Fast":
            if hasattr(self, 'rect'):
                self.image_canvas.delete(self.rect)
            self.end_x = self.image_canvas.canvasx(event.x)
            self.end_y = self.image_canvas.canvasy(event.y)
            self.rect = self.image_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="lime", width=2)
        elif self.mode.get() == "Manual":
            self.end_x = self.image_canvas.canvasx(event.x)
            self.end_y = self.image_canvas.canvasy(event.y)
            self.update_canvas()

    def on_release(self, event):
        if self.mode.get() == "Fast":
            if hasattr(self, 'rect'):
                self.image_canvas.delete(self.rect)
            self.end_x = self.image_canvas.canvasx(event.x)
            self.end_y = self.image_canvas.canvasy(event.y)
            self.save_labeled_image(event)
        elif self.mode.get() == "Manual":
            self.end_x = self.image_canvas.canvasx(event.x)
            self.end_y = self.image_canvas.canvasy(event.y)
            if hasattr(self, 'rect'):
                self.image_canvas.delete(self.rect)
            self.rect = self.image_canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="lime", width=2)

    def update_canvas(self):
        if hasattr(self, 'rect'):
            self.image_canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def save_labeled_image(self, event=None):
        if not self.label:
            messagebox.showwarning("No Label", "Please provide a label before saving.")
            return

        x0, y0, x1, y1 = self.start_x, self.start_y, self.end_x, self.end_y
        coords = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        
        if coords[2] <= coords[0] or coords[3] <= coords[1]:  # Ensure valid coordinates to avoid the error
            messagebox.showwarning("Invalid Coordinates", "Please select a valid area.")
            return

        image_name = os.path.basename(self.image_paths[self.image_index])
        label_data = {
            "imageGcsUri": f"gs://gpulunar/{image_name}",
            "boundingBoxAnnotations": [
                {
                    "displayName": "GPU",
                    "xMin": coords[0] / self.image_width,
                    "yMin": coords[1] / self.image_height,
                    "xMax": coords[2] / self.image_width,
                    "yMax": coords[3] / self.image_height,
                }
            ]
        }
        self.annotations.append(label_data)

        draw = ImageDraw.Draw(self.image)
        draw.rectangle(coords, outline="lime", width=2)
        draw.text((coords[0], coords[1] - 10), self.label, fill="lime")
        self.image.save(os.path.join(self.output_dir, image_name))
        self.image_index += 1
        self.load_image()

    def clear_canvas(self):
        if hasattr(self, 'rect'):
            self.image_canvas.delete(self.rect)

    def save_as_jsonl(self):
        jsonl_path = filedialog.asksaveasfilename(defaultextension=".jsonl", filetypes=[("JSONL files", "*.jsonl")])
        with open(jsonl_path, 'w') as f:
            for annotation in self.annotations:
                json.dump(annotation, f)
                f.write('\n')


if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()
