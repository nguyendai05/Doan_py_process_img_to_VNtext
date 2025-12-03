# Python OCR Web Application

Ứng dụng web chuyển hình ảnh thành văn bản sử dụng EasyOCR với xử lý văn bản offline.

## Tính năng chính

- **OCR Engine**: EasyOCR hỗ trợ tiếng Anh và tiếng Việt
- **Xử lý văn bản offline**: Normalize, rule-based fix, spell-check (không dùng GenAI)
- **2 chế độ xử lý**:
  - Single Image: Xử lý nhanh 1 ảnh
  - Multi Image: Xử lý tối đa 5 ảnh với khung văn bản có thể kéo thả, gộp
- **Quản lý người dùng**: Đăng ký, đăng nhập với MySQL
- **Work History**: Lưu trữ và quản lý lịch sử OCR
- **Công cụ nâng cao**: TTS, Dịch thuật, Research

## Cấu trúc dự án

```
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── work.py
│   │   └── text_block.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── ocr.py
│   │   ├── work.py
│   │   └── tools.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py
│   │   ├── text_processing.py
│   │   ├── tts_service.py
│   │   ├── translate_service.py
│   │   └── research_service.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── auth/
│       └── work/
├── uploads/
├── requirements.txt
├── run.py
└── .env.example
```

## Cài đặt

```bash
# Clone repository
git clone <repo-url>
cd python-ocr

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình database
cp .env.example .env
# Chỉnh sửa .env với thông tin MySQL của bạn

# Chạy ứng dụng
python run.py
```

## Yêu cầu hệ thống

- Python 3.9+
- MySQL 8.0+
- RAM: Tối thiểu 4GB (EasyOCR cần bộ nhớ)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất

### OCR
- `POST /api/ocr/single` - OCR 1 ảnh
- `POST /api/ocr/multi` - OCR nhiều ảnh (tối đa 5)

### Work
- `GET /api/works` - Danh sách works
- `POST /api/works` - Tạo work mới
- `GET /api/works/<id>` - Chi tiết work
- `PUT /api/works/<id>` - Cập nhật work
- `DELETE /api/works/<id>` - Xóa work

### Tools
- `POST /api/tools/tts` - Text-to-Speech
- `POST /api/tools/translate` - Dịch văn bản
- `POST /api/tools/research` - Phân tích/tóm tắt

## License

MIT
