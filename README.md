# Python OCR Web Application

Ứng dụng web nhận diện văn bản từ hình ảnh (OCR) sử dụng EasyOCR, tích hợp các công cụ xử lý văn bản như dịch thuật, text-to-speech, phân tích nội dung và sửa lỗi chính tả bằng AI (BARTpho).

## 🌟 Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| 🔍 **OCR** | Nhận diện văn bản từ ảnh (tiếng Việt + tiếng Anh) |
| 🤖 **BART Correction** | Sửa lỗi chính tả bằng AI (BARTpho) |
| 🔊 **Text-to-Speech** | Chuyển văn bản thành giọng nói (8 ngôn ngữ) |
| 🌐 **Translation** | Dịch văn bản đa ngôn ngữ (11 ngôn ngữ) |
| 📊 **Research** | Tóm tắt, trích xuất từ khóa, tạo câu hỏi |
| 📁 **Work Management** | Quản lý phiên làm việc với text blocks |

## 🛠️ Tech Stack

- **Backend:** Flask 3.0, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite (dev) / MySQL (production)
- **OCR Engine:** EasyOCR + OpenCV
- **AI Model:** BARTpho (Transformers, PyTorch)
- **TTS:** gTTS | **Translation:** googletrans
- **Testing:** pytest, hypothesis

## 🚀 Quick Start

```bash
# Clone và setup
git clone <repo-url>
cd python-ocr
python -m venv venv
venv\Scripts\activate  # Windows

# Install và chạy
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Truy cập: http://127.0.0.1:5000

## 📚 Documentation

| Tài liệu | Mô tả |
|----------|-------|
| [01-OVERVIEW.md](docs/01-OVERVIEW.md) | Tổng quan dự án |
| [02-WORK-SUMMARY.md](docs/02-WORK-SUMMARY.md) | Bảng tóm tắt công việc đã làm/chưa làm |
| [03-ARCHITECTURE.md](docs/03-ARCHITECTURE.md) | Kiến trúc hệ thống |
| [04-MODULES.md](docs/04-MODULES.md) | Chi tiết các modules |
| [05-DATABASE.md](docs/05-DATABASE.md) | Database schema |
| [06-TESTING.md](docs/06-TESTING.md) | Hướng dẫn testing |
| [07-INSTALLATION.md](docs/07-INSTALLATION.md) | Hướng dẫn cài đặt chi tiết |
| [08-API-REFERENCE.md](docs/08-API-REFERENCE.md) | API Reference |
| [09-PROJECT-STRUCTURE.md](docs/09-PROJECT-STRUCTURE.md) | Cấu trúc dự án |

## 📋 Trạng thái công việc

### ✅ Đã hoàn thành (12 modules)
- Authentication, OCR Engine, Text Processing, BART Correction
- TTS Service (với caching), Translation Service (với caching)
- Research Service, Work Management, Chat System
- Database Schema, Testing (Unit + Property tests)

### ⏳ Chưa hoàn thiện
- Frontend UI/UX cần cải thiện
- API Documentation (Swagger)
- Production deployment (Docker)
- Rate limiting

*Chi tiết: [02-WORK-SUMMARY.md](docs/02-WORK-SUMMARY.md)*

## 📁 Cấu trúc chính

```
python-ocr/
├── app/
│   ├── models/      # Database models
│   ├── routes/      # API endpoints
│   ├── services/    # Business logic
│   ├── static/      # CSS, JS, audio
│   └── templates/   # HTML templates
├── db/              # Database schema
├── docs/            # Documentation
├── models/          # BART model
├── tests/           # Test files
└── run.py           # Entry point
```

## 📄 License

MIT

---

*Last updated: January 7, 2026*
