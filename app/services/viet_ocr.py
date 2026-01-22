import easyocr
import cv2
import numpy as np
from PIL import Image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

# =========================
# INIT MODELS
# =========================

import torch

# Auto-detect GPU availability
GPU_AVAILABLE = torch.cuda.is_available()
print(f"[INFO] GPU Available: {GPU_AVAILABLE}")

print("[INFO] Loading EasyOCR...")
easy_reader = easyocr.Reader(['vi', 'en'], gpu=GPU_AVAILABLE)

print("[INFO] Loading VietOCR...")
config = Cfg.load_config_from_name("vgg_transformer")
config['device'] = 'cuda' if GPU_AVAILABLE else 'cpu'
vietocr = Predictor(config)

print("[INFO] Models loaded successfully.")

# =========================
# OCR FUNCTION
# =========================

def ocr_image(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Cannot read image")

    results = easy_reader.readtext(image)

    texts = []

    for box, _, conf in results:
        # Lấy bounding box
        x = [int(p[0]) for p in box]
        y = [int(p[1]) for p in box]

        crop = image[min(y):max(y), min(x):max(x)]
        if crop.size == 0:
            continue

        # Convert sang PIL
        pil_img = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

        # VietOCR recognize
        text = vietocr.predict(pil_img)

        texts.append({
            "text": text,
            "confidence": round(conf, 3),
            "box": box
        })

    return texts




if __name__ == "__main__":
    IMAGE_PATH = r"C:\Users\HINH\Downloads\test_image.png"

    results = ocr_image(IMAGE_PATH)
    text =[]
    print("\n===== OCR RESULT =====")
    for r in results:
        text.append(r["text"])
        print(f"{r['text']}  (conf={r['confidence']})")
    print("\n===== OCR RESULT =====")
    print(" ".join(text))