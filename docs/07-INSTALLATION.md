# 🚀 Hướng Dẫn Cài Đặt

## Yêu cầu hệ thống

| Yêu cầu | Tối thiểu | Khuyến nghị |
|---------|-----------|-------------|
| Python | 3.9+ | 3.11 |
| RAM | 4GB | 8GB |
| Disk | 2GB | 5GB |
| GPU | Không bắt buộc | CUDA 11.8 |

## Cài đặt

### 1. Clone repository

```bash
git clone <repo-url>
cd python-ocr
```

### 2. Tạo virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình environment

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` theo nhu cầu.

### 5. Chạy ứng dụng

```bash
python run.py
```

Ứng dụng sẽ chạy tại: http://127.0.0.1:5000

---

## Cấu hình (.env)

### Flask Settings

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `SECRET_KEY` | Flask secret key | dev-secret-key |

### Database Settings

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `USE_SQLITE` | Sử dụng SQLite | true |
| `DB_HOST` | MySQL host | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_NAME` | Database name | doan_ocr |
| `DB_USER` | MySQL user | root |
| `DB_PASSWORD` | MySQL password | - |

### Upload Settings

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | 5242880 (5MB) |
| `UPLOAD_FOLDER` | Upload folder | uploads |
| `ALLOWED_EXTENSIONS` | Allowed formats | jpg,jpeg,png |

### OCR Settings

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `OCR_LANGUAGES` | OCR languages | en,vi |
| `USE_BART_MODEL` | Enable BART | true |

### Tools Settings

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `MAX_TEXT_LENGTH` | Max text length | 2000 |
| `TTS_OUTPUT_FOLDER` | TTS output | app/static/audio |

### External APIs

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_TRANSLATE_API_KEY` | Google API key | - |

---

## Cấu hình Database

### SQLite (Development)

Mặc định sử dụng SQLite, không cần cấu hình thêm.

```env
USE_SQLITE=true
```

Database file: `instance/app.db`

### MySQL (Production)

```env
USE_SQLITE=false
DB_HOST=localhost
DB_PORT=3306
DB_NAME=doan_ocr
DB_USER=root
DB_PASSWORD=your_password
```

Tạo database:

```bash
mysql -u root -p < db/schema.sql
```

---

## Cấu hình BART Model

### Download model

Model được lưu tại: `models/bartpho_correction_model/`

Cấu trúc:
```
models/bartpho_correction_model/
├── config.json
├── model.safetensors
├── tokenizer_config.json
├── sentencepiece.bpe.model
├── special_tokens_map.json
├── generation_config.json
└── training_args.bin
```

### Enable/Disable

```env
USE_BART_MODEL=true   # Enable
USE_BART_MODEL=false  # Disable
```

### GPU Support

Model tự động detect GPU (CUDA). Nếu không có GPU, sẽ chạy trên CPU.

---

## Troubleshooting

### Lỗi: EasyOCR không load được model

```bash
# Xóa cache và download lại
rm -rf ~/.EasyOCR
python -c "import easyocr; easyocr.Reader(['en', 'vi'])"
```

### Lỗi: CUDA out of memory

```env
# Disable BART model
USE_BART_MODEL=false
```

Hoặc giảm batch size trong `model_inference.py`.

### Lỗi: gTTS connection error

Kiểm tra kết nối internet. gTTS cần kết nối để generate audio.

### Lỗi: MySQL connection refused

```bash
# Kiểm tra MySQL service
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql
```

### Lỗi: Permission denied (uploads folder)

```bash
# Linux/Mac
chmod 755 uploads/
chmod 755 app/static/audio/

# Windows (Run as Administrator)
icacls uploads /grant Everyone:F
```

---

## Development

### Chạy với debug mode

```bash
FLASK_DEBUG=1 python run.py
```

### Chạy tests

```bash
pytest tests/ -v
```

### Chạy với coverage

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

*Xem thêm: [08-API-REFERENCE.md](08-API-REFERENCE.md) - API Reference*
