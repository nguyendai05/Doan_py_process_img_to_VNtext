import easyocr
import cv2
import numpy as np
from PIL import Image
import io

# Global OCR reader instance (singleton)
_ocr_reader = None


def init_ocr_reader(languages):
    """Initialize OCR reader once at app startup"""
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(languages, gpu=False)
    return _ocr_reader


def get_ocr_reader():
    """Get the singleton OCR reader"""
    global _ocr_reader
    return _ocr_reader


class OCRService:
    """Service for OCR processing"""

    @staticmethod
    def preprocess_image(image_bytes):
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply CLAHE for contrast enhancement
        - Denoise
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Cannot decode image")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)

        # Resize if too small (min 300px width)
        height, width = denoised.shape
        if width < 300:
            scale = 300 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            denoised = cv2.resize(denoised, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        return denoised

    @staticmethod
    def extract_text(image_bytes, preprocess=True):
        """
        Extract text from image using EasyOCR
        Returns list of text segments with confidence scores
        """
        reader = get_ocr_reader()
        if reader is None:
            raise RuntimeError("OCR reader not initialized")

        if preprocess:
            processed_img = OCRService.preprocess_image(image_bytes)
        else:
            nparr = np.frombuffer(image_bytes, np.uint8)
            processed_img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Run OCR
        results = reader.readtext(processed_img)

        # Extract text segments
        segments = []
        for (bbox, text, confidence) in results:
            segments.append({
                'text': text,
                'confidence': confidence,
                'bbox': bbox
            })

        return segments

    @staticmethod
    def segments_to_text(segments):
        """Convert OCR segments to plain text"""
        return '\n'.join([seg['text'] for seg in segments])
