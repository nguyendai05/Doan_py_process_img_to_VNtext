# Python OCR Web Application

Ứng dụng web nhận diện văn bản từ hình ảnh (OCR) sử dụng EasyOCR, tích hợp các công cụ xử lý văn bản như dịch thuật, text-to-speech và phân tích nội dung.

## Tính năng chính

- **OCR (Optical Character Recognition)**: Nhận diện văn bản từ ảnh sử dụng EasyOCR, hỗ trợ tiếng Anh và tiếng Việt
- **Xử lý văn bản**: Chuẩn hóa Unicode, sửa lỗi OCR theo rule-based, kiểm tra chính tả (spell-check)
- **Text-to-Speech (TTS)**: Chuyển văn bản thành giọng nói sử dụng gTTS
- **Dịch thuật**: Dịch văn bản sang nhiều ngôn ngữ qua Google Translate
- **Research/Phân tích**: Tóm tắt, trích xuất từ khóa, tạo câu hỏi (hỗ trợ OpenAI API hoặc phân tích cơ bản)
- **Quản lý Work**: Lưu trữ và quản lý lịch sử OCR theo từng work với các text block

## Tech Stack

- **Backend**: Flask 3.0, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite (development) / MySQL (production)
- **OCR Engine**: EasyOCR với OpenCV preprocessing
- **TTS**: gTTS (Google Text-to-Speech)
- **Translation**: googletrans
- **Text Processing**: pyspellchecker

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

# Cấu hình environment
cp .env.example .env
# Chỉnh sửa .env theo nhu cầu

# Chạy ứng dụng
python run.py
```

Ứng dụng sẽ chạy tại: http://127.0.0.1:5000

## Cấu hình (.env)

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `SECRET_KEY` | Flask secret key | dev-secret-key |
| `USE_SQLITE` | Sử dụng SQLite thay vì MySQL | true |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Cấu hình MySQL | localhost:3306 |
| `MAX_CONTENT_LENGTH` | Kích thước file tối đa (bytes) | 5242880 (5MB) |
| `ALLOWED_EXTENSIONS` | Định dạng ảnh cho phép | jpg,jpeg,png |
| `OCR_LANGUAGES` | Ngôn ngữ OCR | en,vi |
| `MAX_TEXT_LENGTH` | Độ dài text tối đa cho tools | 2000 |
| `OPENAI_API_KEY` | API key cho research nâng cao (tùy chọn) | - |

## API Endpoints

### Authentication (`/api/auth`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/register` | Đăng ký tài khoản | ❌ |
| POST | `/login` | Đăng nhập | ❌ |
| POST | `/logout` | Đăng xuất | ✅ |
| GET | `/me` | Lấy thông tin user hiện tại | ✅ |

### OCR (`/api/ocr`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/single` | OCR một ảnh (field: `image`) | ✅ |
| POST | `/multi` | OCR nhiều ảnh, tối đa 5 (field: `images`) | ✅ |

### Works (`/api/works`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/` | Danh sách works của user | ✅ |
| POST | `/` | Tạo work mới | ✅ |
| GET | `/<id>` | Chi tiết work | ✅ |
| PUT | `/<id>` | Cập nhật work | ✅ |
| DELETE | `/<id>` | Xóa work | ✅ |
| POST | `/<id>/blocks` | Thêm text block vào work | ✅ |
| DELETE | `/<id>/blocks/<block_id>` | Xóa text block | ✅ |
| POST | `/<id>/merge` | Gộp nhiều text blocks | ✅ |

### Tools (`/api/tools`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/tts` | Chuyển text thành audio | ✅ |
| GET | `/tts/languages` | Danh sách ngôn ngữ TTS | ❌ |
| POST | `/translate` | Dịch văn bản | ✅ |
| GET | `/translate/languages` | Danh sách ngôn ngữ dịch | ❌ |
| POST | `/research` | Phân tích văn bản (summary/keywords/questions) | ✅ |

## Cấu trúc dự án

```
├── app/
│   ├── __init__.py          # App factory, khởi tạo extensions
│   ├── config.py            # Cấu hình ứng dụng
│   ├── models/              # Database models
│   │   ├── user.py          # User model
│   │   ├── work.py          # Work model
│   │   └── text_block.py    # TextBlock model
│   ├── routes/              # API routes
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── ocr.py           # OCR endpoints
│   │   ├── work.py          # Work management endpoints
│   │   └── tools.py         # TTS, Translate, Research endpoints
│   ├── services/            # Business logic
│   │   ├── ocr_service.py   # EasyOCR wrapper với preprocessing
│   │   ├── text_processing.py # Xử lý văn bản, spell-check
│   │   ├── tts_service.py   # Text-to-Speech service
│   │   ├── translate_service.py # Translation service
│   │   └── research_service.py  # Text analysis service
│   ├── static/              # Static files (CSS, JS, audio)
│   └── templates/           # Jinja2 templates
├── instance/                # SQLite database
├── static/audio/            # Generated TTS audio files
├── requirements.txt
├── run.py                   # Entry point
└── .env.example
```

## Yêu cầu hệ thống

- Python 3.9+
- RAM: Tối thiểu 4GB (EasyOCR cần bộ nhớ để load model)

## License

MIT
