# 📋 Tổng Quan Dự Án

## Giới thiệu

**Python OCR Web Application** - Ứng dụng web nhận diện văn bản từ hình ảnh (OCR) sử dụng EasyOCR, tích hợp các công cụ xử lý văn bản như dịch thuật, text-to-speech, phân tích nội dung và sửa lỗi chính tả bằng AI (BARTpho).

## Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| 🔍 **OCR** | Nhận diện văn bản từ ảnh (tiếng Việt + tiếng Anh) |
| 🔧 **Text Processing** | Chuẩn hóa Unicode, sửa lỗi OCR rule-based |
| 🤖 **BART Correction** | Sửa lỗi chính tả bằng AI (BARTpho) |
| 🔊 **Text-to-Speech** | Chuyển văn bản thành giọng nói (8 ngôn ngữ) |
| 🌐 **Translation** | Dịch văn bản đa ngôn ngữ (11 ngôn ngữ) |
| 📊 **Research** | Tóm tắt, trích xuất từ khóa, tạo câu hỏi |
| 📁 **Work Management** | Quản lý phiên làm việc với text blocks |
| 💬 **Chat System** | Hệ thống chat sessions |

## Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| **Backend** | Flask 3.0, Flask-SQLAlchemy, Flask-Login |
| **Database** | SQLite (dev) / MySQL (production) |
| **OCR Engine** | EasyOCR + OpenCV preprocessing |
| **AI Model** | BARTpho (Transformers, PyTorch) |
| **TTS** | gTTS (Google Text-to-Speech) |
| **Translation** | googletrans |
| **Testing** | pytest, hypothesis |

## Yêu cầu hệ thống

| Yêu cầu | Tối thiểu | Khuyến nghị |
|---------|-----------|-------------|
| Python | 3.9+ | 3.11 |
| RAM | 4GB | 8GB |
| Disk | 2GB | 5GB |
| GPU | Không bắt buộc | CUDA 11.8 |

---

*Xem thêm: [02-WORK-SUMMARY.md](02-WORK-SUMMARY.md) - Bảng tóm tắt công việc*
