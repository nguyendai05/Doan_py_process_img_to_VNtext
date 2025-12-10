import re
from typing import Dict, List, Pattern, Tuple, Optional
import unicodedata
from spellchecker import SpellChecker


class TextProcessor:
    """
     text processing for OCR output
    - Unicode normalization
    - OCR error correction (rule-based)
    - Spell checking
    """

    VIETNAMESE_CHARS = r"a-zàáạảãăằắặẳẵâầấậẩẫèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđA-ZÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"

    MATH_AND_JUNK_CHARS = re.compile(
        r"[^\w\s" + VIETNAMESE_CHARS + r".,;:!?()\"\'\-\/—\$%\&\*\+=<>@#^`~\[\]{}|\\_]"  # Các ký tự còn lại
    )

    # Sửa lỗi thay thế ký tự phổ biến của OCR (thường là lẫn giữa chữ và số)
    OCR_CORRECTIONS: Dict[str, str] = {
        '0': 'o', 'O': '0', 'o': '0',  # '0' có thể thành 'o', 'O' có thể thành '0'
        '1': 'l', 'l': '1', 'I': '1',  # 1, l, I lẫn lộn
        '5': 's', 'S': '5',
        '8': 'B', 'B': '8',
        '|': 'l',  # Dấu gạch đứng (|) thành 'l'
        'm': 'rn', 'rn': 'm',  # Lỗi 'rn' thành 'm' và ngược lại (ít phổ biến hơn)
        'vv': 'w',  # Tiếng Việt không có 'w' (thay bằng 'v' hoặc xóa nếu sai)
        'cl': 'd',
        'é': 'e',  # Lỗi nhận dạng dấu có thể gây ra ký tự lạ
        'è': 'e',
        'ç': 'c',
        # Thêm các ký tự lỗi toán học thường gặp bị nhận dạng sai thành chữ:
        '°': 'o',  # Ký hiệu độ có thể thành 'o'
        '£': 'E',  # Ký hiệu bảng Anh có thể thành 'E'
        # Thêm các lỗi OCR Tiếng Việt cụ thể:
        'đ': 'a',  # Đôi khi 'đ' bị nhận dạng sai thành 'a' hoặc 'd'
        'd': 'đ',  # Sửa chữa ngược lại (cần cẩn thận với từ có 'd')
    }

    # Context-aware patterns for correction
    CONTEXT_PATTERNS: List[Tuple[Pattern, str]] = [
        (re.compile(r'\b(\w*)0(\w+)\b', re.IGNORECASE), r'\1o\2'),
        (re.compile(r'\b(\w+)0(\w*)\b', re.IGNORECASE), r'\1o\2'),
        (re.compile(r'\b(\w*)1(\w+)\b', re.IGNORECASE), r'\1l\2'),
        (re.compile(r'\b(\w+)1(\w*)\b', re.IGNORECASE), r'\1l\2'),
        (re.compile(r'\b(\w*)5(\w+)\b', re.IGNORECASE), r'\1s\2'),
        (re.compile(r'\b(\w+)5(\w*)\b', re.IGNORECASE), r'\1s\2'),
        (re.compile(r'cl', re.IGNORECASE), r'd'),
    ]

    def __init__(self, language: str = 'vi'):
        self.language = language

    @staticmethod
    def normalize_unicode(text):
        """Normalize Unicode characters"""
        # NFC normalization
        text = unicodedata.normalize('NFC', text)
        return text

    @staticmethod
    def normalize_whitespace(text):
        """Normalize whitespace and line breaks"""
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        # Remove excessive line breaks (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        return text.strip()

    def apply_ocr_rules(self, text):
        # 1. Áp dụng các mẫu sửa lỗi theo ngữ cảnh (ví dụ: số trong từ)
        for pattern, replacement in self.CONTEXT_PATTERNS:
            text = pattern.sub(replacement, text)

        # 2. Sửa lỗi thay thế ký tự phổ biến (thường là lẫn giữa chữ và số)
        # Sẽ sửa từng ký tự/cụm ký tự một.
        for old, new in self.OCR_CORRECTIONS.items():
            text = text.replace(old, new)

        return text

    def clean_math_and_junk_chars(self, text: str) -> str:
        """Loại bỏ các ký tự lạ, ký tự toán học, hoặc không hợp lệ"""

        # Loại bỏ các ký tự không nằm trong danh sách VIETNAMESE_CHARS, số,
        # khoảng trắng, và các dấu câu cơ bản.
        text = self.MATH_AND_JUNK_CHARS.sub('', text)

        return text

    def process(self, text):
        # 1. Chuẩn hóa Unicode
        text = self.normalize_unicode(text)

        # 2. Chuẩn hóa khoảng trắng
        text = self.normalize_whitespace(text)

        # 3. Áp dụng quy tắc sửa lỗi OCR
        text = self.apply_ocr_rules(text)

        # 4. Loại bỏ ký tự lạ, toán học và không hợp lệ
        text = self.clean_math_and_junk_chars(text)

        # Chuẩn hóa khoảng trắng lần cuối
        text = self.normalize_whitespace(text)

        return text
