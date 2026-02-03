from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import cv2
from detector import PCBDetector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../models/best.pt")
INIT_IMG = os.path.join(BASE_DIR, "../assets/whitebg.jpg")

detector = PCBDetector(MODEL_PATH)

current_image_path = None
original_pil = None
predicted_pil = None
score_thresh = 0.5


# ---------- Viewer Window (Zoom + Pan) ----------

def open_viewer(pil_image, title):
    if pil_image is None:
        return

    win = Toplevel(root)
    win.title(title)
    win.geometry("900x700")

    canvas = Canvas(win, bg="black")
    canvas.pack(fill=BOTH, expand=True)

    img = pil_image.copy()
    zoom = 1.0

    def redraw():
        nonlocal img, zoom
        w, h = img.size
        resized = img.resize((int(w * zoom), int(h * zoom)))
        tk = ImageTk.PhotoImage(resized)
        canvas.image = tk
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=tk)
        canvas.config(scrollregion=canvas.bbox(ALL))

    def on_mousewheel(event):
        nonlocal zoom
        if event.delta > 0:
            zoom *= 1.1
        else:   
            zoom /= 1.1
        redraw()

    def start_pan(event):
        canvas.scan_mark(event.x, event.y)

    def do_pan(event):
        canvas.scan_dragto(event.x, event.y, gain=1)

    canvas.bind("<MouseWheel>", on_mousewheel)
    canvas.bind("<ButtonPress-1>", start_pan)
    canvas.bind("<B1-Motion>", do_pan)

    redraw()


# ---------- Main Logic ----------

def add_image():
    global current_image_path, original_pil, predicted_pil

    file = filedialog.askopenfilename(
        title="Select PCB Image",
        filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
    )
    if not file:
        return

    current_image_path = file
    original_pil = Image.open(file)
    predicted_pil = None

    show_preview(original_pil, panel_original)
    panel_pred.configure(image=placeholder_tk)
    panel_pred.image = placeholder_tk


def run_detection():
    global predicted_pil

    if not current_image_path:
        return

    img, counts = detector.predict(current_image_path, conf=score_thresh)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    predicted_pil = Image.fromarray(img)

    show_preview(predicted_pil, panel_pred)

    textvariable1.set(str(counts.get("Missing Hole", 0)))
    textvariable2.set(str(counts.get("Mouse Bite", 0)))
    textvariable3.set(str(counts.get("Open Circuit", 0)))
    textvariable4.set(str(counts.get("Short Circuit", 0)))
    textvariable5.set(str(counts.get("Spur", 0)))
    textvariable6.set(str(counts.get("Spurious Copper", 0)))


def show_preview(pil_img, panel):
    img = pil_img.copy()
    img.thumbnail((300, 300))
    tk = ImageTk.PhotoImage(img)
    panel.configure(image=tk)
    panel.image = tk


def change_score():
    global score_thresh
    score_thresh = float(score_valuechange.get())
    score_value.set(str(score_thresh))


# ---------- UI ----------

root = Tk()
root.title("PCB Inspection System")
root.geometry("1100x650")

placeholder = Image.open(INIT_IMG)
placeholder.thumbnail((300, 300))
placeholder_tk = ImageTk.PhotoImage(placeholder)

panel_original = Label(root, image=placeholder_tk, bd=2, relief="groove")
panel_pred = Label(root, image=placeholder_tk, bd=2, relief="groove")

panel_original.grid(row=0, column=0, padx=10, pady=10)
panel_pred.grid(row=0, column=1, padx=10, pady=10)

panel_original.bind("<Button-1>", lambda e: open_viewer(original_pil, "Original Image"))
panel_pred.bind("<Button-1>", lambda e: open_viewer(predicted_pil, "Prediction Image"))

control = ttk.Frame(root, padding=10, relief="groove")
control.grid(row=0, column=2, sticky="nsew", padx=10)

textvariable1 = StringVar(value="0")
textvariable2 = StringVar(value="0")
textvariable3 = StringVar(value="0")
textvariable4 = StringVar(value="0")
textvariable5 = StringVar(value="0")
textvariable6 = StringVar(value="0")

labels = ["Missing Hole", "Mouse Bite", "Open Circuit", "Short Circuit", "Spur", "Spurious Copper"]
vars = [textvariable1, textvariable2, textvariable3, textvariable4, textvariable5, textvariable6]

ttk.Label(control, text="Defects", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

for i, (l, v) in enumerate(zip(labels, vars), start=1):
    ttk.Label(control, text=l).grid(row=i, column=0, sticky="w")
    ttk.Label(control, textvariable=v, width=5, relief="sunken").grid(row=i, column=1)

row_base = len(labels) + 2

score_value = StringVar(value="0.5")
score_valuechange = StringVar()

ttk.Label(control, text="Threshold").grid(row=row_base, column=0, pady=10)
ttk.Label(control, textvariable=score_value).grid(row=row_base, column=1)

ttk.Entry(control, textvariable=score_valuechange).grid(row=row_base + 1, column=1)
ttk.Button(control, text="Change Score", command=change_score).grid(row=row_base + 2, columnspan=2, pady=5)

ttk.Button(control, text="Add Image", command=add_image).grid(row=row_base + 3, columnspan=2, pady=5)
ttk.Button(control, text="Run Detection", command=run_detection).grid(row=row_base + 4, columnspan=2, pady=5)

root.mainloop()
