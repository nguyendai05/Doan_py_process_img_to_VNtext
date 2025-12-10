import re
import unicodedata
from typing import Dict, List, Pattern, Tuple, Optional


# Lưu ý: Thư viện `spellchecker` không hỗ trợ tốt tiếng Việt.
# Tôi sẽ giả định rằng bạn đã có một cơ chế hoặc từ điển tiếng Việt
# nếu muốn thực hiện kiểm tra chính tả nâng cao.
# Trong ví dụ này, tôi tập trung vào việc làm sạch ký tự.

class TextProcessor:
    """
    Xử lý text thô từ đầu ra OCR.
    - Chuẩn hóa Unicode.
    - Loại bỏ/Thay thế ký tự lỗi do OCR (dựa trên quy tắc).
    - Loại bỏ ký tự lạ, ký tự toán học, và ký tự không hợp lệ cho tiếng Việt.
    """

    # 🇻🇳 Bảng chữ cái tiếng Việt và các ký tự hợp lệ cơ bản
    # Bao gồm chữ cái (thường, hoa, có dấu), số, dấu cách, và dấu câu cơ bản.
    VIETNAMESE_CHARS = r"a-zàáạảãăằắặẳẵâầấậẩẫèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđA-ZÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"

    # Cần loại bỏ hoặc thay thế nếu không phải là phần của văn bản thông thường.
    # Ví dụ: toán tử, ký hiệu tiền tệ, các ký tự không in được, v.v.
    # Lưu ý: Cẩn thận không xóa các dấu câu hợp lệ.
    MATH_AND_JUNK_CHARS = re.compile(
        r"[^\w\s" + VIETNAMESE_CHARS + r".,;:!?()\"\'\-\/—\$%\&\*\+=<>@#^`~\[\]{}|\\_]"  # Các ký tự còn lại
    )

    #Sửa lỗi thay thế ký tự phổ biến của OCR (thường là lẫn giữa chữ và số)
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
    def normalize_unicode(text: str) -> str:
        """Chuẩn hóa Unicode (NFC: Composition Form)"""
        # Đảm bảo các ký tự có dấu được hợp nhất (ví dụ: 'o' + '́' -> 'ó')
        text = unicodedata.normalize('NFC', text)
        return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Chuẩn hóa khoảng trắng và ngắt dòng"""
        # Thay thế nhiều khoảng trắng/tab bằng một khoảng trắng
        text = re.sub(r'[ \t]+', ' ', text)
        # Chuẩn hóa ngắt dòng (đảm bảo chỉ dùng \n)
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        # Loại bỏ ngắt dòng dư thừa (chỉ giữ tối đa 2 ngắt dòng liên tiếp)
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Xóa khoảng trắng ở đầu/cuối mỗi dòng
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        return text.strip()

    def apply_ocr_rules(self, text: str) -> str:
        """Áp dụng các quy tắc sửa lỗi OCR"""

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

    def process(self, text: str) -> str:
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



if __name__ == '__main__':
    # Đầu vào giả định từ OCR
    ocr_text_input = """
    Kink Te 8ol Kgoai
BỔ SUNG HÌNH ẢNH ĐÍNH KÈM
CẬP NHẬT HỒ SƠ ĐĂNG KÝ XÉT TUYỂN
THÔNG TIN THÍ SINH ĐÃ ĐĂNG KÝ
Mã hồ sơ: 24oo7s8s
Họ tên thí sinh: Nguyễn Thị Kim Thoa
CMND: 027306oo6793
Ngày sinh: o8/ll/2oo6
Giới tính: Nữ
Email: nguyenkimthoa2lol@gmail.com
Điện thoại: 096848o8s7
Địa chỉ nhận giấy báo: Bưu điện xã Tân Đông, huyện Tân Châu; tinh Tây Ninh
Tỉnh /Thành phố lớp l2: Tinh
Ninh
Quận/Huyện lớp l2:
Trường Iớp l2: THPT Tân
Năm tốt nghiệp: 2o24
Khu vực:
Đối tượng ưu tiên:
Số báo danh: 46oo3773
Mã code:
THÔNG TIN XÉT TUYỂN
30oo387 số nôi bô 1lo
Tây
Đông
    """

    processor = TextProcessor()

    print("--- 📄 Text Gốc ---")
    print(ocr_text_input)

    # Xử lý text
    processed_text = processor.process(ocr_text_input)

    print("\n--- 🌟 Text Đã Xử Lý (Loại bỏ lỗi OCR, Toán học, Ký tự lạ) ---")
    print(processed_text)