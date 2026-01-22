import easyocr
import cv2
import numpy as np
from PIL import Image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg


_ocr_reader = None
_vietocr_predictor = None


def init_ocr_reader(languages):
    """
    Initialize OCR readers once at app startup
    """
    global _ocr_reader, _vietocr_predictor
    GPU = True # or False
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(languages, gpu=GPU)

    if _vietocr_predictor is None:
        config = Cfg.load_config_from_name("vgg_transformer")
        config["device"] = "cuda" if GPU else "cpu"
        _vietocr_predictor = Predictor(config)

    return _ocr_reader


def get_ocr_reader():
    """Get EasyOCR singleton"""
    return _ocr_reader


def get_vietocr_predictor():
    """Get VietOCR singleton"""
    return _vietocr_predictor


class OCRService:
    """Service for OCR processing"""

    @staticmethod
    def preprocess_image(image_bytes):
        """
        Preprocess image for better OCR accuracy
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Cannot decode image")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)

        h, w = denoised.shape
        if w < 300:
            scale = 300 / w
            denoised = cv2.resize(
                denoised,
                (int(w * scale), int(h * scale)),
                interpolation=cv2.INTER_CUBIC
            )

        return denoised

    @staticmethod
    def extract_text(image_bytes, preprocess=True, use_vietocr=True):
        """
        Extract text from image
        - EasyOCR: detect bbox
        - VietOCR: recognize text (optional)
        """
        reader = get_ocr_reader()
        vietocr = get_vietocr_predictor()

        if reader is None:
            raise RuntimeError("OCR reader not initialized")

        nparr = np.frombuffer(image_bytes, np.uint8)
        original_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if preprocess:
            processed_img = OCRService.preprocess_image(image_bytes)
        else:
            processed_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

        results = reader.readtext(processed_img)

        segments = []

        for bbox, easy_text, confidence in results:
            x = [int(p[0]) for p in bbox]
            y = [int(p[1]) for p in bbox]

            crop = original_img[min(y):max(y), min(x):max(x)]
            if crop.size == 0:
                continue

            final_text = easy_text

            if use_vietocr and vietocr is not None:
                pil_img = Image.fromarray(
                    cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                )
                try:
                    final_text = vietocr.predict(pil_img)
                except Exception:
                    final_text = easy_text  # fallback

            segments.append({
                "text": final_text,
                "confidence": float(confidence),
                "bbox": [[int(c) for c in point] for point in bbox]
            })

        return segments

    @staticmethod
    def segments_to_text(segments):
        """Convert OCR segments to plain text"""
        return "  ".join(seg["text"] for seg in segments)
