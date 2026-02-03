from ultralytics import YOLO
import cv2

class PCBDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def predict(self, image_path, conf=0.5):
        results = self.model(image_path, conf=conf)[0]
        img = cv2.imread(image_path)

        label_map = {
            "missing_hole": "Missing Hole",
            "mouse_bite": "Mouse Bite",
            "open_circuit": "Open Circuit",
            "short": "Short Circuit",
            "spur": "Spur",
            "spurious_copper": "Spurious Copper"
        }

        counts = {v: 0 for v in label_map.values()}

        for box in results.boxes:
            cls = int(box.cls[0])
            raw_name = results.names[cls]
            ui_name = label_map.get(raw_name, raw_name)

            if ui_name in counts:
                counts[ui_name] += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, ui_name, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return img, counts
