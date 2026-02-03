from ultralytics import YOLO

model = YOLO("models/best.pt")

metrics = model.val(data="data.yaml")

print("mAP@0.5:0.95:", metrics.box.map)
print("mAP@0.5:", metrics.box.map50)
print("Precision:", metrics.box.precision)
print("Recall:", metrics.box.recall)
