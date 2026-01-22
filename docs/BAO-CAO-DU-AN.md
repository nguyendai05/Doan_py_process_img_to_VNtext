# BÁO CÁO DỰ ÁN: IMAGE TO TEXT OCR

## THÔNG TIN CHUNG

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | Image to Text OCR |
| **Mô tả** | Ứng dụng web nhận diện văn bản từ hình ảnh (OCR) sử dụng EasyOCR và VietOCR, tích hợp các công cụ xử lý văn bản như dịch thuật, text-to-speech, phân tích nội dung và sửa lỗi chính tả bằng AI (BARTpho) |
| **Ngôn ngữ lập trình** | Python 3.9+ |
| **Framework** | Flask 3.0 |
| **Database** | MySQL (production) / SQLite (development) |
| **Ngày cập nhật** | Tháng 1, 2026 |

---

## MỤC LỤC

1. [Tổng quan dự án](#1-tổng-quan-dự-án)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Công nghệ sử dụng](#3-công-nghệ-sử-dụng)
4. [Cấu trúc thư mục](#4-cấu-trúc-thư-mục)
5. [Chi tiết các Module](#5-chi-tiết-các-module)
6. [Database Schema](#6-database-schema)
7. [API Endpoints](#7-api-endpoints)
8. [Tính năng chi tiết](#8-tính-năng-chi-tiết)
9. [Testing](#9-testing)
10. [Hướng dẫn cài đặt](#10-hướng-dẫn-cài-đặt)
11. [Trạng thái công việc](#11-trạng-thái-công-việc)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1 Giới thiệu

**Image to Text OCR** là một ứng dụng web toàn diện cho việc nhận diện và xử lý văn bản từ hình ảnh. Ứng dụng được thiết kế để hỗ trợ người dùng trích xuất văn bản từ ảnh (đặc biệt là tiếng Việt), sau đó cung cấp các công cụ xử lý văn bản như dịch thuật, chuyển văn bản thành giọng nói, tóm tắt nội dung và trích xuất từ khóa.

### 1.2 Tính năng chính

| STT | Tính năng | Mô tả | Công nghệ |
|-----|-----------|-------|-----------|
| 1 | **OCR (Nhận diện văn bản)** | Nhận diện văn bản từ ảnh, hỗ trợ tiếng Việt và tiếng Anh | EasyOCR + VietOCR |
| 2 | **Tiền xử lý ảnh** | Tăng cường chất lượng ảnh trước khi OCR | OpenCV (CLAHE, Denoising) |
| 3 | **Sửa lỗi chính tả AI** | Sửa lỗi chính tả tiếng Việt bằng mô hình BARTpho | Transformers, PyTorch |
| 4 | **Text-to-Speech (TTS)** | Chuyển văn bản thành giọng nói, hỗ trợ 8 ngôn ngữ | gTTS |
| 5 | **Dịch thuật** | Dịch văn bản đa ngôn ngữ, hỗ trợ 11 ngôn ngữ | googletrans |
| 6 | **Dịch bằng Model** | Dịch Việt-Anh bằng model fine-tuned (OPUS-MT) | Transformers |
| 7 | **Tóm tắt văn bản** | Tóm tắt văn bản tiếng Việt bằng ensemble algorithm | TextRank, TF-IDF, underthesea |
| 8 | **Trích xuất từ khóa** | Trích xuất keyphrases từ văn bản tiếng Việt | POS tagging, N-gram |
| 9 | **Quản lý Work** | Quản lý phiên làm việc với text blocks, đổi tên inline | SQLAlchemy |
| 10 | **Hệ thống Chat** | Lưu trữ lịch sử chat sessions | Flask-SQLAlchemy |
| 11 | **Caching** | Cache kết quả TTS và Translation để tối ưu hiệu suất | SHA256 hash |
| 12 | **Authentication** | Đăng ký, đăng nhập, quản lý phiên | Flask-Login, bcrypt |
| 13 | **Paste từ Clipboard** | Upload ảnh bằng Ctrl+V từ clipboard | JavaScript Clipboard API |
| 14 | **BART Evaluation** | Thống kê chi tiết: similarity score, change rate, số câu | Python statistics |

### 1.3 Yêu cầu hệ thống

| Yêu cầu | Tối thiểu | Khuyến nghị |
|---------|-----------|-------------|
| Python | 3.9+ | 3.11 |
| RAM | 4GB | 8GB+ |
| Disk | 2GB | 5GB+ |
| GPU | Không bắt buộc | CUDA 11.8+ (tăng tốc OCR và AI) |
| OS | Windows/Linux/macOS | Windows 10+ / Ubuntu 20.04+ |

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 Sơ đồ kiến trúc tổng quan

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Upload    │  │   Tools     │  │   Works     │  │    Chat     │        │
│  │   Image     │  │   Panel     │  │   Manager   │  │   System    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│                         Jinja2 Templates + JavaScript                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER (Flask Blueprints)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  /api/auth  │  │  /api/ocr   │  │ /api/tools  │  │ /api/works  │        │
│  │  /api/chat  │  │             │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SERVICE LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ OCRService  │  │ TTSService  │  │ Translate   │  │  Research   │        │
│  │ + VietOCR   │  │ + Cache     │  │ + Cache     │  │  Service    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │    Text     │  │    BART     │  │  Summarize  │                         │
│  │ Processing  │  │  Inference  │  │   Service   │                         │
│  └─────────────┘  └─────────────┘  └─────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SQLAlchemy ORM Models                            │   │
│  │  User │ Image │ OCRResult │ Work │ TextBlock │ TTS │ Translation    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              MySQL (production) / SQLite (development)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Luồng xử lý OCR

```
Upload Image → Save to Disk → Preprocessing (OpenCV) → EasyOCR Detection
                                                              │
                                                              ▼
                                                       VietOCR Recognition
                                                              │
                                                              ▼
                                                       Text Processing
                                                              │
                                                              ▼
                                                       BART Correction
                                                              │
                                                              ▼
                                                    Save to Database
                                                    (Image, OCRResult, Work)
```

### 2.3 Luồng xử lý TTS với Caching

```
Request TTS → Validate Input → Check Cache (SHA256 hash)
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                    Cache HIT                 Cache MISS
                         │                         │
                         ▼                         ▼
                  Return cached            Generate audio (gTTS)
                  audio_url                        │
                                                   ▼
                                            Save to cache
                                                   │
                                                   ▼
                                            Return new audio_url
```

---

## 3. CÔNG NGHỆ SỬ DỤNG

### 3.1 Backend

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| Flask | 3.0.0 | Web framework |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| Flask-Login | 0.6.3 | Authentication |
| Flask-CORS | 4.0.0 | Cross-Origin Resource Sharing |
| SQLAlchemy | 2.0.44 | Database ORM |
| PyMySQL | 1.1.0 | MySQL connector |
| bcrypt | 4.1.2 | Password hashing |

### 3.2 OCR & Image Processing

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| EasyOCR | 1.7.1 | OCR engine chính (detection) |
| VietOCR | 0.3.13 | OCR tiếng Việt (recognition) |
| OpenCV | 4.8.1.78 | Image preprocessing |
| Pillow | 10.2.0 | Image manipulation |
| NumPy | 1.26.4 | Array operations |

### 3.3 AI/ML Models

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| PyTorch | 2.9.1 | Deep learning framework |
| Transformers | 4.57.3 | Hugging Face models |
| BARTpho | - | Sửa lỗi chính tả tiếng Việt |
| OPUS-MT | - | Dịch Việt-Anh |
| underthesea | 6.8.4 | Vietnamese NLP |

### 3.4 Text Processing & NLP

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| gTTS | 2.4.0 | Text-to-Speech |
| googletrans | 4.0.0rc1 | Translation |
| underthesea | 6.8.4 | Vietnamese tokenization, POS, NER |
| scikit-learn | 1.8.0 | TF-IDF, cosine similarity |
| networkx | 3.3 | TextRank algorithm |

### 3.5 Testing

| Công nghệ | Version | Mục đích |
|-----------|---------|----------|
| pytest | 9.0.2 | Unit testing |
| hypothesis | 6.149.0 | Property-based testing |

---

## 4. CẤU TRÚC THƯ MỤC

```
python-ocr/
├── app/                          # Application package
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── image.py             # Image model
│   │   ├── ocr_result.py        # OCRResult, OCRSegment models
│   │   ├── work.py              # Work, TextBlock models
│   │   ├── chat.py              # ChatSession, ChatMessage models
│   │   ├── tts_audio.py         # TTSAudio model
│   │   ├── translation.py       # Translation model
│   │   └── activity_log.py      # ActivityLog model
│   ├── routes/                  # API endpoints (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── ocr.py               # OCR routes
│   │   ├── work.py              # Work management routes
│   │   ├── tools.py             # TTS, Translate, Research routes
│   │   └── chat.py              # Chat routes
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── ocr_service.py       # OCR processing
│   │   ├── text_processing.py   # Text normalization
│   │   ├── model_inference.py   # BART model inference
│   │   ├── tts_service.py       # Text-to-Speech
│   │   ├── tts_cache_service.py # TTS caching
│   │   ├── translate_service.py # Translation
│   │   ├── translation_cache_service.py  # Translation caching
│   │   ├── translation_model_service.py  # Model-based translation
│   │   ├── research_service.py  # Keywords, questions
│   │   └── summarize_service.py # Text summarization
│   ├── static/                  # Static files
│   │   ├── css/style.css        # Styles
│   │   ├── js/app.js            # Frontend JavaScript
│   │   └── audio/               # Generated TTS audio files
│   └── templates/               # Jinja2 templates
│       ├── base.html            # Base template
│       └── index.html           # Main page
├── db/                          # Database
│   ├── schema.sql               # Full SQL schema
│   ├── apply_schema.py          # Schema application script
│   └── README.md                # Database documentation
├── docs/                        # Documentation
│   ├── 01-OVERVIEW.md
│   ├── 02-WORK-SUMMARY.md
│   ├── 03-ARCHITECTURE.md
│   └── ...
├── models/                      # AI Models
│   └── bartpho_correction_model/  # BARTpho model files
├── tests/                       # Test files
│   ├── test_translate_api_endpoint.py
│   ├── test_tts_api_endpoint.py
│   └── ...
├── uploads/                     # Uploaded images
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # Project README
```

---

## 5. CHI TIẾT CÁC MODULE

### 5.1 OCR Service (`app/services/ocr_service.py`)

**Chức năng:** Nhận diện văn bản từ hình ảnh

**Các thành phần:**
- `init_ocr_reader()`: Khởi tạo EasyOCR và VietOCR (singleton pattern)
- `OCRService.preprocess_image()`: Tiền xử lý ảnh với OpenCV
  - Chuyển grayscale
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)
  - Denoising (fastNlMeansDenoising)
  - Resize nếu ảnh quá nhỏ
- `OCRService.extract_text()`: Trích xuất văn bản
  - EasyOCR: Phát hiện vùng chứa text (bounding box)
  - VietOCR: Nhận diện text trong từng vùng (tùy chọn)
- `OCRService.segments_to_text()`: Ghép các segment thành văn bản hoàn chỉnh

**Output:**
```python
{
    "text": "Nội dung văn bản",
    "confidence": 0.95,
    "bbox": [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
}
```

### 5.2 Text Processing (`app/services/text_processing.py`)

**Chức năng:** Chuẩn hóa và sửa lỗi văn bản OCR

**Các phương thức:**
- `normalize_unicode()`: Chuẩn hóa Unicode (NFC)
- `normalize_whitespace()`: Chuẩn hóa khoảng trắng và xuống dòng
- `apply_ocr_rules()`: Sửa lỗi OCR phổ biến
  - `0` → `o`, `1` → `l`, `5` → `s`
  - `cl` → `d`, `rn` → `m`
- `clean_math_and_junk_chars()`: Loại bỏ ký tự không hợp lệ

### 5.3 BART Model Inference (`app/services/model_inference.py`)

**Chức năng:** Sửa lỗi chính tả tiếng Việt bằng AI

**Model:** BARTpho (fine-tuned cho spell correction)

**Quy trình:**
1. Load model từ `models/bartpho_correction_model/`
2. Chia văn bản thành các câu
3. Gộp câu thành chunks (~200 ký tự)
4. Xử lý từng chunk qua model
5. Ghép kết quả

**Cấu hình:**
- `max_length`: 256 tokens
- `num_beams`: 4
- `length_penalty`: 1.0
- `early_stopping`: True

**Thống kê đánh giá (Evaluation Metrics):**
| Metric | Mô tả |
|--------|-------|
| `original_char_count` | Số ký tự văn bản gốc |
| `corrected_char_count` | Số ký tự sau sửa |
| `char_diff` | Chênh lệch ký tự (+/-) |
| `original_word_count` | Số từ văn bản gốc |
| `corrected_word_count` | Số từ sau sửa |
| `original_sentence_count` | Số câu gốc |
| `corrected_sentence_count` | Số câu sau sửa |
| `changes_count` | Số từ thay đổi |
| `change_rate` | Tỷ lệ thay đổi (%) |
| `similarity_score` | Độ tương đồng Jaccard (%) |

### 5.4 TTS Service (`app/services/tts_service.py`)

**Chức năng:** Chuyển văn bản thành giọng nói

**Ngôn ngữ hỗ trợ:**
| Code | Ngôn ngữ |
|------|----------|
| vi | Tiếng Việt |
| en | English |
| fr | Français |
| de | Deutsch |
| es | Español |
| ja | 日本語 |
| ko | 한국어 |
| zh-CN | 中文 (简体) |

**Caching:**
- Cache key: SHA256(text + language)
- Lưu trong bảng `tts_audio`
- Kiểm tra file tồn tại trước khi trả về cache

### 5.5 Translation Service (`app/services/translate_service.py`)

**Chức năng:** Dịch văn bản đa ngôn ngữ

**Ngôn ngữ hỗ trợ:**
| Code | Ngôn ngữ |
|------|----------|
| auto | Tự động phát hiện |
| vi | Tiếng Việt |
| en | English |
| fr | Français |
| de | Deutsch |
| es | Español |
| ja | 日本語 |
| ko | 한국어 |
| zh-cn | 中文 (简体) |
| zh-tw | 中文 (繁體) |
| th | ไทย |
| ru | Русский |

**Caching:**
- Cache key: SHA256(text + source_lang + dest_lang)
- Unique constraint: (source_text_hash, source_lang, dest_lang)

### 5.6 Translation Model Service (`app/services/translation_model_service.py`)

**Chức năng:** Dịch Việt-Anh bằng model fine-tuned

**Model:** OPUS-MT (fine-tuned trên 100k samples)

**Đặc điểm:**
- Chunking thông minh theo câu
- Bảo toàn entities (URL, email, ngày tháng, số)
- Batch processing để tối ưu hiệu suất
- Hỗ trợ GPU acceleration

**Cấu hình:**
- `max_tokens_per_chunk`: 420
- `batch_size`: 12
- `max_new_tokens`: 220
- `num_beams`: 4

### 5.7 Research Service (`app/services/research_service.py`)

**Chức năng:** Phân tích và trích xuất thông tin từ văn bản

**Các loại phân tích:**
1. **Keywords**: Trích xuất từ khóa/keyphrases
   - POS tagging với underthesea
   - Proper noun extraction
   - N-gram generation (2-4 words)
   - TF-IDF scoring

2. **Summary**: Tóm tắt văn bản (delegate to SummarizeService)

3. **Questions**: Tạo câu hỏi ôn tập từ keywords

### 5.8 Summarize Service (`app/services/summarize_service.py`)

**Chức năng:** Tóm tắt văn bản tiếng Việt bằng ensemble algorithm

**Quy trình:**
1. **Normalize**: Chuẩn hóa văn bản, vá lỗi OCR
2. **Split**: Tách đoạn → câu → units (mệnh đề)
3. **Annotate**: Tokenize, POS, NER, NP với underthesea
4. **TF-IDF**: Tính vector và similarity matrix
5. **TextRank**: PageRank trên graph similarity
6. **Multi-criteria Scoring**:
   - Topic/Conclusion position
   - Cue markers (tóm lại, kết luận, do đó...)
   - Actionability (cần, yêu cầu, thực hiện...)
   - Keyphrase overlap
   - Centroid similarity
   - TextRank score
   - NP density, POS weight, NER bonus
7. **MMR Selection**: Chọn units đa dạng, giảm trùng lặp
8. **Output**: Bullet points

**Cấu hình:**
- `MIN_BULLETS`: 3
- `RATIO`: 0.30 (~30% văn bản gốc)
- `MAX_BULLETS`: 12

---

## 6. DATABASE SCHEMA

### 6.1 Sơ đồ quan hệ (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USERS                                          │
│  (id, email, password_hash, full_name, avatar_url, is_active, ...)         │
└─────────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         │ 1:N                │ 1:N                │ 1:N
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│     IMAGES      │  │     WORKS       │  │  CHAT_SESSIONS  │
│ (file, path...) │  │ (title, desc)   │  │ (title, work_id)│
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         │ 1:N                │ 1:N                │ 1:N
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   OCR_RESULTS   │  │   TEXT_BLOCKS   │  │  CHAT_MESSAGES  │
│ (raw, cleaned)  │  │ (content, type) │  │ (role, content) │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│  OCR_SEGMENTS   │
│ (text, bbox)    │
└─────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    TTS_AUDIO    │  │  TRANSLATIONS   │  │  ACTIVITY_LOGS  │
│ (file, lang)    │  │ (src, dest)     │  │ (action, entity)│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 6.2 Chi tiết các bảng

#### 6.2.1 users
Quản lý người dùng hệ thống.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| email | VARCHAR(255) | Email đăng nhập (unique) |
| password_hash | VARCHAR(255) | Mật khẩu đã hash (bcrypt) |
| full_name | VARCHAR(100) | Họ tên |
| avatar_url | VARCHAR(500) | URL avatar |
| is_active | BOOLEAN | Trạng thái hoạt động |
| last_login_at | DATETIME | Lần đăng nhập cuối |
| created_at | DATETIME | Ngày tạo |
| updated_at | DATETIME | Ngày cập nhật |

#### 6.2.2 images
Lưu trữ thông tin ảnh upload.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| user_id | INT | FK → users.id |
| file_name | VARCHAR(255) | Tên file gốc |
| file_path | VARCHAR(500) | Đường dẫn lưu trữ |
| file_size | INT | Kích thước (bytes) |
| mime_type | VARCHAR(50) | MIME type |
| width | INT | Chiều rộng (px) |
| height | INT | Chiều cao (px) |
| source | VARCHAR(50) | Nguồn: upload/url/camera |
| checksum | VARCHAR(64) | SHA256 hash |
| created_at | DATETIME | Ngày upload |

#### 6.2.3 ocr_results
Kết quả OCR từ ảnh.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| image_id | INT | FK → images.id |
| user_id | INT | FK → users.id |
| engine | VARCHAR(30) | OCR engine (easyocr) |
| language | VARCHAR(20) | Ngôn ngữ (vi,en) |
| raw_text | LONGTEXT | Text thô từ OCR |
| processed_text | LONGTEXT | Text đã xử lý |
| corrected_text | LONGTEXT | Text sau BART |
| confidence_avg | DECIMAL(5,4) | Độ tin cậy trung bình |
| processing_time_ms | INT | Thời gian xử lý (ms) |
| word_count | INT | Số từ |
| status | ENUM | pending/processing/completed/failed |
| error_message | TEXT | Lỗi (nếu có) |

#### 6.2.4 ocr_segments
Chi tiết từng segment OCR với bounding box.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| ocr_result_id | INT | FK → ocr_results.id |
| text | VARCHAR(1000) | Nội dung text |
| confidence | DECIMAL(5,4) | Độ tin cậy |
| bbox_x1, bbox_y1 | INT | Tọa độ góc trên trái |
| bbox_x2, bbox_y2 | INT | Tọa độ góc dưới phải |
| position | INT | Thứ tự trong ảnh |

#### 6.2.5 works
Phiên làm việc (workspace).

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| user_id | INT | FK → users.id |
| title | VARCHAR(255) | Tiêu đề |
| description | TEXT | Mô tả |
| ocr_result_id | INT | FK → ocr_results.id (optional) |
| is_archived | BOOLEAN | Đã lưu trữ |

#### 6.2.6 text_blocks
Khối văn bản trong work.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| work_id | INT | FK → works.id |
| source_type | ENUM | ocr/manual/translate/tts/research/edit |
| title | VARCHAR(255) | Tiêu đề |
| content | LONGTEXT | Nội dung |
| extra_data | JSON | Metadata bổ sung |
| position | INT | Thứ tự trong work |
| is_deleted | BOOLEAN | Soft delete |

#### 6.2.7 tts_audio
File audio TTS (có cache).

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| user_id | INT | FK → users.id |
| text_content | TEXT | Nội dung text |
| text_hash | VARCHAR(64) | SHA256 hash (cache key) |
| language | VARCHAR(10) | Ngôn ngữ |
| file_path | VARCHAR(500) | Đường dẫn file |
| file_size | INT | Kích thước |
| duration_ms | INT | Thời lượng (ms) |
| text_block_id | INT | FK → text_blocks.id (optional) |

#### 6.2.8 translations
Bản dịch (có cache).

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| user_id | INT | FK → users.id |
| source_text | TEXT | Text nguồn |
| source_text_hash | VARCHAR(64) | SHA256 hash |
| source_lang | VARCHAR(10) | Ngôn ngữ nguồn |
| translated_text | TEXT | Text đã dịch |
| dest_lang | VARCHAR(10) | Ngôn ngữ đích |
| engine | VARCHAR(30) | Engine dịch (google) |
| text_block_id | INT | FK → text_blocks.id (optional) |

**Unique constraint:** (source_text_hash, source_lang, dest_lang)

#### 6.2.9 chat_sessions
Phiên chat.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| user_id | INT | FK → users.id |
| title | VARCHAR(255) | Tiêu đề |
| work_id | INT | FK → works.id (optional) |
| is_archived | BOOLEAN | Đã lưu trữ |

#### 6.2.10 chat_messages
Tin nhắn trong chat.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| session_id | INT | FK → chat_sessions.id |
| role | ENUM | user/assistant/system |
| content | TEXT | Nội dung |
| message_type | ENUM | text/ocr_result/translation/tts/research/error |
| extra_data | JSON | Metadata |
| ocr_result_id | INT | FK → ocr_results.id (optional) |
| text_block_id | INT | FK → text_blocks.id (optional) |
| is_deleted | BOOLEAN | Soft delete |

#### 6.2.11 activity_logs
Ghi log hoạt động.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| user_id | INT | FK → users.id |
| action | VARCHAR(50) | Hành động (login, ocr, tts...) |
| entity_type | VARCHAR(50) | Loại entity |
| entity_id | INT | ID entity |
| details | JSON | Chi tiết |
| ip_address | VARCHAR(45) | IP address |
| user_agent | VARCHAR(500) | User agent |

---

## 7. API ENDPOINTS

### 7.1 Authentication (`/api/auth`)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/register` | Đăng ký tài khoản | No |
| POST | `/login` | Đăng nhập | No |
| POST | `/logout` | Đăng xuất | Yes |
| GET | `/me` | Lấy thông tin user hiện tại | Yes |

### 7.2 OCR (`/api/ocr`)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/single` | OCR một ảnh | Yes |

**Request (multipart/form-data):**
- `image`: File ảnh (jpg, jpeg, png)

**Response:**
```json
{
    "success": true,
    "raw_text": "...",
    "processed_text": "...",
    "bart_output": "...",
    "segments": [...],
    "image_id": 1,
    "ocr_result_id": 1,
    "work_id": 1
}
```

### 7.3 Tools (`/api/tools`)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/tts` | Text-to-Speech | Yes |
| GET | `/tts/languages` | Danh sách ngôn ngữ TTS | No |
| POST | `/translate` | Dịch văn bản | Yes |
| GET | `/translate/languages` | Danh sách ngôn ngữ dịch | No |
| POST | `/translate-model-all` | Dịch bằng model (Vi→En) | Yes |
| POST | `/research` | Phân tích văn bản | Yes |
| POST | `/summarize` | Tóm tắt văn bản | Yes |
| POST | `/bart-correction` | Sửa lỗi chính tả AI (BARTpho) | Yes |

**TTS Request:**
```json
{
    "text": "Văn bản cần đọc",
    "language": "vi"
}
```

**TTS Response:**
```json
{
    "success": true,
    "audio_url": "/static/audio/tts_xxx.mp3",
    "from_cache": false,
    "duration_ms": null
}
```

**Translate Request:**
```json
{
    "text": "Hello world",
    "dest_lang": "vi",
    "src_lang": "auto"
}
```

**Translate Response:**
```json
{
    "success": true,
    "translated_text": "Xin chào thế giới",
    "source_lang": "en",
    "dest_lang": "vi",
    "from_cache": false
}
```

**Research Request:**
```json
{
    "text": "Văn bản cần phân tích",
    "type": "keywords"  // keywords, summary, questions
}
```

### 7.4 Works (`/api/works`)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/` | Danh sách works | Yes |
| POST | `/` | Tạo work mới | Yes |
| GET | `/<work_id>` | Chi tiết work | Yes |
| PUT | `/<work_id>` | Cập nhật work | Yes |
| POST | `/<work_id>/rename` | Đổi tên work (inline edit) | Yes |
| DELETE | `/<work_id>` | Xóa work | Yes |
| POST | `/<work_id>/blocks` | Thêm text block | Yes |
| DELETE | `/<work_id>/blocks/<block_id>` | Xóa text block | Yes |
| POST | `/<work_id>/merge` | Gộp text blocks | Yes |

### 7.5 Chat (`/api/chat`)

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| GET | `/sessions` | Danh sách chat sessions | Yes |
| POST | `/sessions` | Tạo session mới | Yes |
| GET | `/sessions/<id>` | Chi tiết session | Yes |
| PUT | `/sessions/<id>` | Cập nhật session | Yes |
| DELETE | `/sessions/<id>` | Xóa session | Yes |
| GET | `/sessions/<id>/messages` | Danh sách messages | Yes |
| POST | `/sessions/<id>/messages` | Thêm message | Yes |
| DELETE | `/messages/<id>` | Xóa message | Yes |

---

## 8. TÍNH NĂNG CHI TIẾT

### 8.1 Luồng xử lý OCR đầy đủ

```
1. Upload Image (multipart/form-data)
   │
   ▼
2. Validate (extension, size ≤ 5MB)
   │
   ▼
3. Save to uploads/ directory
   │
   ▼
4. Preprocessing (OpenCV)
   ├── Grayscale conversion
   ├── CLAHE enhancement (clipLimit=2.0, tileGridSize=8x8)
   ├── Denoising (fastNlMeansDenoising: h=10, templateSize=7, searchSize=21)
   └── Resize if width < 300px (scale up with INTER_CUBIC)
   │
   ▼
5. OCR Detection (EasyOCR)
   ├── Detect text regions (bounding boxes)
   └── Return list of (bbox, text, confidence)
   │
   ▼
6. OCR Recognition (VietOCR - optional)
   ├── Crop from original image using bbox
   ├── PIL Image → VietOCR Predictor
   └── Return recognized text per region
   │
   ▼
7. Text Processing
   ├── Unicode normalization (NFC)
   ├── Whitespace cleanup
   ├── OCR error correction rules (0→o, 1→l, cl→d, rn→m)
   └── Math/junk character removal
   │
   ▼
8. BART AI Correction (optional)
   ├── Split text into sentences
   ├── Group sentences into chunks (~200 chars)
   ├── Process each chunk with BARTpho model
   └── Merge corrected results
   │
   ▼
9. Save to Database
   ├── Image record (file info, dimensions, checksum)
   ├── OCRResult (raw_text, processed_text, corrected_text)
   ├── OCRSegments (text, bbox, confidence per region)
   └── Work (workspace for further processing)
```

### 8.2 Text-to-Speech (TTS)

**Caching Strategy:**
- Cache key: SHA256(text + language)
- Check cache trước khi generate
- Nếu file đã tồn tại → trả về cached URL
- Nếu chưa có → generate mới bằng gTTS → save to DB + filesystem

**Ngôn ngữ hỗ trợ (8):**
| Code | Ngôn ngữ | gTTS tld |
|------|----------|----------|
| vi | Tiếng Việt | com.vn |
| en | English | com |
| fr | Français | fr |
| de | Deutsch | de |
| es | Español | es |
| ja | 日本語 | co.jp |
| ko | 한국어 | co.kr |
| zh-CN | 中文 (简体) | com.cn |

**Output:** MP3 file trong `/static/audio/tts_<hash>.mp3`

### 8.3 Translation Service

**Hai chế độ dịch:**

1. **Google Translate (googletrans):**
   - 11 ngôn ngữ: auto, vi, en, fr, de, es, ja, ko, zh-cn, zh-tw, th, ru
   - Free, nhanh, không cần API key
   - Caching với SHA256 hash

2. **Model-based Translation (OPUS-MT):**
   - Chỉ hỗ trợ Việt → Anh
   - Fine-tuned trên 100k samples
   - Chunking thông minh theo câu
   - Bảo toàn entities (URL, email, ngày tháng)
   - Batch processing (batch_size=12)
   - GPU acceleration support

**Translation Model Config:**
```python
max_tokens_per_chunk = 420
batch_size = 12
max_new_tokens = 220
num_beams = 4
```

### 8.4 Summarization Service (Ensemble Algorithm)

**Quy trình tóm tắt văn bản tiếng Việt:**

```
Input Text
    │
    ▼
1. Normalize (vá OCR, chuẩn hóa newline, whitespace)
    │
    ▼
2. Split: Paragraphs → Sentences → Units (mệnh đề)
   - Tách đoạn theo \n\n
   - Tách câu theo [.!?;]
   - Tách ý theo [,:;–—] và discourse markers
    │
    ▼
3. Annotate với underthesea:
   - word_tokenize: tách từ tiếng Việt
   - pos_tag: gán nhãn từ loại (N, V, A, ...)
   - ner: nhận diện thực thể (PER, LOC, ORG, ...)
   - NP heuristic: trích xuất danh từ ngữ
    │
    ▼
4. TF-IDF Vectorization:
   - Ngram range: (1, 2)
   - Cosine similarity matrix NxN
   - Centroid vector cho toàn văn bản
    │
    ▼
5. TextRank (PageRank on similarity graph):
   - Threshold: 0.10
   - Alpha: 0.85
   - Normalize scores to 0..1
    │
    ▼
6. Multi-criteria Scoring (15 signals):
   - Position: topic sentence, conclusion, doc start/end
   - Cue markers: "tóm lại", "kết luận", "do đó", ...
   - Actionability: "cần", "yêu cầu", "thực hiện", ...
   - Deadline/time markers
   - Keyphrase overlap
   - Centroid similarity
   - TextRank score
   - NP density, POS weight, NER bonus
   - Numeric content, length normalization
    │
    ▼
7. MMR Selection (Maximal Marginal Relevance):
   - Lambda: 0.70 (quality vs diversity)
   - Beta: 0.60 (redundancy penalty)
   - Hard skip threshold: 0.85
   - Target: max(3, ceil(num_sentences * 0.40))
   - Max bullets: 12
    │
    ▼
8. Build Bullets:
   - Group units by sentence
   - Join related units with ", "
   - Output: "- <bullet_text>"
```

**Cấu hình mặc định:**
| Param | Value | Mô tả |
|-------|-------|-------|
| MIN_BULLETS | 3 | Tối thiểu 3 ý |
| RATIO | 0.40 | ~40% số câu gốc |
| MAX_BULLETS | 12 | Tối đa 12 ý |

### 8.5 Keyword Extraction (Research Service)

**Phương pháp trích xuất keyphrases:**

1. **POS Tagging:** Sử dụng underthesea để gán nhãn từ loại
2. **Proper Noun Extraction:** Nhận diện danh từ riêng (viết hoa)
3. **N-gram Generation:** Tạo n-gram (2-4 từ) từ chuỗi danh từ + tính từ
4. **TF-IDF Scoring:** Tính trọng số cho các n-gram
5. **Filtering:**
   - Loại bỏ stopwords
   - Loại bỏ n-gram chỉ chứa số
   - Loại bỏ n-gram trùng lặp (subset/superset)

**Output Format:**
```json
{
  "success": true,
  "keywords": [
    {"term": "keyphrase 1", "score": 0.85},
    {"term": "keyphrase 2", "score": 0.72}
  ]
}
```

---

## 9. TESTING

### 9.1 Tổng quan Test Files

| File | Loại | Mô tả | Lines |
|------|------|-------|-------|
| `test_tts_api_endpoint.py` | Unit Test | Tests cho TTS API endpoint | ~300 |
| `test_tts_cache_roundtrip_property.py` | Property Test | Cache round-trip consistency | ~200 |
| `test_tts_hash_property.py` | Property Test | Hash consistency | ~100 |
| `test_tts_invalid_input_property.py` | Property Test | Invalid input rejection | ~330 |
| `test_translate_api_endpoint.py` | Unit Test | Tests cho Translate API endpoint | ~370 |
| `test_translation_cache_roundtrip_property.py` | Property Test | Cache round-trip consistency | ~230 |
| `test_translation_hash_property.py` | Property Test | Hash consistency | ~100 |
| `test_translation_invalid_input_property.py` | Property Test | Invalid input rejection | ~360 |

**Tổng:** 8 test files, ~2000 lines of test code

### 9.2 Unit Tests

**TTS API Endpoint Tests:**
| Test Case | Expected Result |
|-----------|-----------------|
| `test_successful_tts_generation` | Audio URL trả về thành công |
| `test_cache_hit_scenario` | Request thứ 2 trả về cached |
| `test_empty_text_error` | 400 + EMPTY_TEXT |
| `test_whitespace_only_text_error` | 400 + EMPTY_TEXT |
| `test_text_too_long_error` | 400 + TEXT_TOO_LONG |
| `test_unsupported_language_error` | 400 + UNSUPPORTED_LANGUAGE |
| `test_missing_text_field_error` | 400 + EMPTY_TEXT |
| `test_default_language_when_not_provided` | Default 'vi' |

**Translate API Endpoint Tests:**
| Test Case | Expected Result |
|-----------|-----------------|
| `test_successful_translation` | Translated text trả về |
| `test_cache_hit_scenario` | Request thứ 2 trả về cached |
| `test_empty_text_error` | 400 + EMPTY_TEXT |
| `test_text_too_long_error` | 400 + TEXT_TOO_LONG |
| `test_same_language_error` | 400 + error khi src=dest |
| `test_same_language_allowed_with_auto_detect` | OK khi src='auto' |
| `test_missing_text_field_error` | 400 + EMPTY_TEXT |
| `test_default_languages_when_not_provided` | Default dest='en', src='auto' |

### 9.3 Property-based Tests (Hypothesis)

**Sử dụng Hypothesis library để test với random inputs:**

```python
# Hash Consistency Test
@given(text=st.text(min_size=1, max_size=1000),
       language=st.sampled_from(['vi', 'en', 'fr']))
def test_hash_consistency(text, language):
    hash1 = TTSCacheService.get_cache_key(text, language)
    hash2 = TTSCacheService.get_cache_key(text, language)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex

# Cache Round-trip Test
@given(text=st.text(min_size=1, max_size=500),
       language=st.sampled_from(['vi', 'en']))
def test_cache_roundtrip(text, language):
    save_to_cache(text, language, file_path, user_id)
    cached = find_cached(text, language)
    assert cached is not None
    assert cached.text_content == text

# Invalid Input Rejection Test
@given(text=st.text(min_size=2001, max_size=3000))
def test_reject_long_text(text):
    response = client.post('/api/tools/tts', json={'text': text})
    assert response.status_code == 400
    assert response.json['error_code'] == 'TEXT_TOO_LONG'
```

**Properties tested:**
- Same input → Same hash (deterministic)
- Different input → Different hash (collision resistance)
- Saved data = Retrieved data (integrity)
- Invalid inputs rejected correctly (robustness)

### 9.4 Chạy Tests

```bash
# Chạy tất cả tests
pytest tests/ -v

# Chạy specific test file
pytest tests/test_tts_api_endpoint.py -v

# Chạy với coverage report
pytest tests/ --cov=app --cov-report=html

# Chạy property tests với nhiều iterations
pytest tests/test_tts_hash_property.py -v --hypothesis-seed=0

# Xem coverage report
open htmlcov/index.html
```

### 9.5 Test Configuration

```python
class TestConfig:
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
    TTS_OUTPUT_FOLDER = None  # Set to temp dir
    OCR_LANGUAGES = ['en', 'vi']
    MAX_TEXT_LENGTH = 2000
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
```

---

## 10. HƯỚNG DẪN CÀI ĐẶT

### 10.1 Yêu cầu hệ thống

| Yêu cầu | Tối thiểu | Khuyến nghị |
|---------|-----------|-------------|
| **Python** | 3.9+ | 3.11 |
| **RAM** | 4GB | 8GB+ (cho BART model) |
| **Disk** | 2GB | 5GB+ (models + audio cache) |
| **GPU** | Không bắt buộc | CUDA 11.8+ (tăng tốc OCR và AI) |
| **OS** | Windows/Linux/macOS | Windows 10+ / Ubuntu 20.04+ |

### 10.2 Các bước cài đặt

```bash
# 1. Clone repository
git clone <repo-url>
cd python-ocr

# 2. Tạo virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Cấu hình environment
cp .env.example .env
# Chỉnh sửa .env theo nhu cầu

# 5. Khởi tạo database (MySQL)
mysql -u root -p < db/schema.sql

# 6. Chạy ứng dụng
python run.py
```

**Truy cập:** http://127.0.0.1:5000

### 10.3 Cấu hình Environment (.env)

| Biến | Mặc định | Mô tả |
|------|----------|-------|
| **Flask** | | |
| `SECRET_KEY` | dev-secret-key | Flask secret key |
| `FLASK_ENV` | development | development/production |
| **Database** | | |
| `DB_HOST` | localhost | MySQL host |
| `DB_PORT` | 3306 | MySQL port |
| `DB_NAME` | doan_ocr | Database name |
| `DB_USER` | root | MySQL user |
| `DB_PASSWORD` | - | MySQL password |
| **Upload** | | |
| `MAX_CONTENT_LENGTH` | 5242880 | Max file size (5MB) |
| `UPLOAD_FOLDER` | uploads | Upload directory |
| `ALLOWED_EXTENSIONS` | jpg,jpeg,png | Allowed formats |
| **OCR** | | |
| `OCR_LANGUAGES` | en,vi | Ngôn ngữ OCR |
| `USE_BART_MODEL` | true | Enable/disable BART |
| **Tools** | | |
| `MAX_TEXT_LENGTH` | 2000 | Max text length |
| `TTS_OUTPUT_FOLDER` | app/static/audio | TTS output |
| **APIs (optional)** | | |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `GOOGLE_TRANSLATE_API_KEY` | - | Google API key |

### 10.4 Cấu hình Database

**MySQL (Production):**
```bash
# Tạo database
mysql -u root -p -e "CREATE DATABASE python_ocr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Apply schema
mysql -u root -p python_ocr < db/schema.sql
```

**.env:**
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=python_ocr
DB_USER=root
DB_PASSWORD=your_password
```

### 10.5 Cấu hình BART Model

Model được lưu tại: `models/bartpho_correction_model/`

**Cấu trúc:**
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

**Enable/Disable:**
```env
USE_BART_MODEL=true   # Enable
USE_BART_MODEL=false  # Disable (nếu thiếu RAM/GPU)
```

### 10.6 Troubleshooting

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-------------|-----------|
| EasyOCR không load model | Cache lỗi | `rm -rf ~/.EasyOCR` và chạy lại |
| CUDA out of memory | RAM GPU không đủ | Set `USE_BART_MODEL=false` hoặc giảm batch size |
| gTTS connection error | Không có internet | Kiểm tra kết nối mạng |
| MySQL connection refused | MySQL chưa chạy | `sudo systemctl start mysql` |
| Permission denied (uploads) | Thiếu quyền ghi | `chmod 755 uploads/` hoặc `icacls uploads /grant Everyone:F` |

---

## 11. TRẠNG THÁI CÔNG VIỆC

### 11.1 ✅ Đã hoàn thành (12 modules)

| STT | Module | Mô tả | Công nghệ | Status |
|-----|--------|-------|-----------|--------|
| 1 | **Authentication** | Đăng ký/đăng nhập/đăng xuất | Flask-Login, bcrypt | ✅ Done |
| 2 | **OCR Engine** | Nhận diện văn bản từ ảnh | EasyOCR + VietOCR + OpenCV | ✅ Done |
| 3 | **Text Processing** | Chuẩn hóa Unicode, sửa lỗi OCR | regex, Unicode NFC | ✅ Done |
| 4 | **BART Correction** | Sửa lỗi chính tả AI | Transformers, BARTpho | ✅ Done |
| 5 | **TTS Service** | Text-to-Speech với caching | gTTS, SHA256 | ✅ Done |
| 6 | **Translation** | Dịch đa ngôn ngữ với caching | googletrans, SHA256 | ✅ Done |
| 7 | **Translation Model** | Dịch Việt-Anh bằng AI | OPUS-MT, Transformers | ✅ Done |
| 8 | **Summarization** | Tóm tắt văn bản tiếng Việt | TextRank, TF-IDF, underthesea | ✅ Done |
| 9 | **Keyword Extraction** | Trích xuất keyphrases | POS tagging, N-gram | ✅ Done |
| 10 | **Work Management** | Quản lý phiên làm việc | SQLAlchemy, Flask | ✅ Done |
| 11 | **Chat System** | Lưu lịch sử chat | Flask-SQLAlchemy | ✅ Done |
| 12 | **Database Schema** | 10 tables với relationships | MySQL/SQLite | ✅ Done |
| 13 | **Testing** | Unit + Property-based tests | pytest, hypothesis | ✅ Done |

### 11.2 ⏳ Chưa hoàn thiện

| STT | Module | Mô tả | Priority | Ghi chú |
|-----|--------|-------|----------|---------|
| 1 | **Frontend UI/UX** | Giao diện người dùng | High | Cần cải thiện design |
| 2 | **OCR Multi-image** | OCR nhiều ảnh cùng lúc | Medium | Endpoint có, chưa test kỹ |
| 3 | **Research LLM** | Tích hợp OpenAI/Gemini | Low | Cần API key |
| 4 | **Activity Logging** | Ghi log hoạt động | Low | Model có, chưa implement service |
| 5 | **File Cleanup** | Dọn dẹp file cũ | Low | Stored procedure có, cần scheduled job |
| 6 | **API Documentation** | Swagger/OpenAPI docs | Medium | Cần tích hợp |
| 7 | **Docker Deployment** | Production deployment | Medium | Cần Dockerfile + docker-compose |
| 8 | **Rate Limiting** | Giới hạn request | Medium | Chống abuse API |

### 11.3 Dependencies Summary

**Tổng số packages:** 78 (trong requirements.txt)

**Phân loại:**
| Category | Packages | Examples |
|----------|----------|----------|
| Flask & Extensions | 6 | Flask, Flask-SQLAlchemy, Flask-Login, Flask-Cors, Flask-WTF |
| Database | 4 | PyMySQL, mysql-connector-python, SQLAlchemy, cryptography |
| Authentication | 2 | bcrypt, PyJWT |
| OCR + Image | 8 | easyocr, vietocr, opencv-python, Pillow, numpy, scikit-image |
| AI/ML | 6 | torch, torchvision, transformers, sentencepiece, huggingface-hub |
| NLP | 5 | underthesea, networkx, scikit-learn |
| TTS & Translation | 2 | gTTS, googletrans |
| Testing | 2 | pytest, hypothesis |
| Utilities | ~15 | python-dotenv, requests, tqdm, beautifulsoup4, ... |

---

## 12. KẾT LUẬN

### 12.1 Tóm tắt dự án

Python OCR Web Application là một ứng dụng web toàn diện cho việc nhận diện và xử lý văn bản từ hình ảnh. Dự án đã hoàn thành các tính năng cốt lõi:

1. **OCR Engine:** Tích hợp EasyOCR + VietOCR với preprocessing OpenCV
2. **AI Spell Correction:** Sử dụng BARTpho để sửa lỗi chính tả tiếng Việt
3. **Text Tools:** TTS (8 ngôn ngữ), Translation (11 ngôn ngữ), Summarization, Keyword Extraction
4. **Caching System:** SHA256-based caching cho TTS và Translation
5. **Database:** MySQL với 10 tables và relationships đầy đủ
6. **Testing:** 8 test files với unit tests và property-based tests

### 12.2 Điểm mạnh

- ✅ Hỗ trợ tiếng Việt tốt (VietOCR, BARTpho, underthesea)
- ✅ Caching thông minh giảm tải server
- ✅ Kiến trúc modular, dễ mở rộng
- ✅ API RESTful chuẩn
- ✅ Testing coverage tốt

### 12.3 Hạn chế và hướng phát triển

- ⚠️ Frontend cần cải thiện UI/UX
- ⚠️ Chưa có Docker deployment
- ⚠️ Chưa có API documentation (Swagger)
- ⚠️ Cần thêm rate limiting cho production

---

**Ngày cập nhật:** 23/01/2026

**Phiên bản:** 1.1.0

**Changelog v1.1.0:**
- ✅ Thêm tính năng paste ảnh từ clipboard (Ctrl+V)
- ✅ Thêm tính năng đổi tên work bằng double-click
- ✅ Thêm thống kê chi tiết cho BART correction (similarity score, change rate)
- ✅ Cải thiện UX: Modal không đóng khi click bên ngoài
- ✅ Thêm API endpoint `/api/tools/bart-correction`
- ✅ Thêm API endpoint `/api/works/<id>/rename`

**Tác giả:** Python OCR Team
