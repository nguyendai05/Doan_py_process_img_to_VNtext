# 📁 Cấu Trúc Dự Án

```
python-ocr/
│
├── app/                              # Main application package
│   ├── __init__.py                   # App factory, extensions init
│   ├── config.py                     # Configuration from .env
│   │
│   ├── models/                       # Database models (SQLAlchemy)
│   │   ├── __init__.py               # Export all models
│   │   ├── user.py                   # User model (bcrypt auth)
│   │   ├── image.py                  # Image upload model
│   │   ├── ocr_result.py             # OCRResult + OCRSegment
│   │   ├── work.py                   # Work + TextBlock
│   │   ├── tts_audio.py              # TTS audio cache
│   │   ├── translation.py            # Translation cache
│   │   ├── chat.py                   # ChatSession + ChatMessage
│   │   └── activity_log.py           # Activity logging
│   │
│   ├── routes/                       # API routes (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py                   # /api/auth/*
│   │   ├── ocr.py                    # /api/ocr/*
│   │   ├── work.py                   # /api/works/*
│   │   ├── tools.py                  # /api/tools/*
│   │   └── chat.py                   # /api/chat/*
│   │
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── ocr_service.py            # EasyOCR wrapper
│   │   ├── text_processing.py        # Text normalization
│   │   ├── model_inference.py        # BART model
│   │   ├── tts_service.py            # gTTS wrapper
│   │   ├── tts_cache_service.py      # TTS caching
│   │   ├── translate_service.py      # Google Translate
│   │   ├── translation_cache_service.py  # Translation caching
│   │   └── research_service.py       # Text analysis
│   │
│   ├── static/                       # Static files
│   │   ├── css/
│   │   │   └── style.css             # Main styles
│   │   ├── js/
│   │   │   └── app.js                # Frontend JavaScript
│   │   └── audio/                    # Generated TTS files
│   │
│   └── templates/                    # Jinja2 templates
│       ├── base.html                 # Base template
│       └── index.html                # Main page
│
├── db/                               # Database files
│   ├── schema.sql                    # MySQL schema
│   ├── seed.sql                      # Sample data
│   ├── apply_schema.py               # Migration script
│   ├── migrations/                   # Migration files
│   │   └── 001_initial_schema.sql
│   └── README.md                     # DB documentation
│
├── docs/                             # Documentation
│   ├── 01-OVERVIEW.md
│   ├── 02-WORK-SUMMARY.md
│   ├── 03-ARCHITECTURE.md
│   ├── 04-MODULES.md
│   ├── 05-DATABASE.md
│   ├── 06-TESTING.md
│   ├── 07-INSTALLATION.md
│   ├── 08-API-REFERENCE.md
│   └── 09-PROJECT-STRUCTURE.md
│
├── models/                           # AI Models
│   └── bartpho_correction_model/     # BART model files
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer_config.json
│       ├── sentencepiece.bpe.model
│       └── ...
│
├── tests/                            # Test files
│   ├── test_tts_api_endpoint.py
│   ├── test_tts_cache_roundtrip_property.py
│   ├── test_tts_hash_property.py
│   ├── test_tts_invalid_input_property.py
│   ├── test_translate_api_endpoint.py
│   ├── test_translation_cache_roundtrip_property.py
│   ├── test_translation_hash_property.py
│   └── test_translation_invalid_input_property.py
│
├── instance/                         # Instance-specific files
│   └── app.db                        # SQLite database (dev)
│
├── uploads/                          # Uploaded images
│
├── static/                           # Alternative static folder
│   └── audio/                        # TTS audio files
│
├── .kiro/                            # Kiro specs
│   └── specs/
│       ├── tts-selected-text-update/
│       │   └── tasks.md
│       └── translate-selected-text-update/
│           └── tasks.md
│
├── venv/                             # Virtual environment
│
├── .env                              # Environment variables
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── run.py                            # Application entry point
└── README.md                         # Main README
```

---

## Chi tiết các thư mục

### app/

Thư mục chính chứa code ứng dụng Flask.

| Folder | Mô tả |
|--------|-------|
| `models/` | SQLAlchemy ORM models |
| `routes/` | Flask Blueprints (API endpoints) |
| `services/` | Business logic layer |
| `static/` | CSS, JS, audio files |
| `templates/` | Jinja2 HTML templates |

### db/

Thư mục chứa database schema và migrations.

| File | Mô tả |
|------|-------|
| `schema.sql` | Full MySQL schema |
| `seed.sql` | Sample data |
| `apply_schema.py` | Python script để apply schema |
| `migrations/` | Incremental migrations |

### docs/

Documentation được tách thành các file riêng.

| File | Nội dung |
|------|----------|
| `01-OVERVIEW.md` | Tổng quan dự án |
| `02-WORK-SUMMARY.md` | Bảng tóm tắt công việc |
| `03-ARCHITECTURE.md` | Kiến trúc hệ thống |
| `04-MODULES.md` | Chi tiết các modules |
| `05-DATABASE.md` | Database schema |
| `06-TESTING.md` | Testing guide |
| `07-INSTALLATION.md` | Hướng dẫn cài đặt |
| `08-API-REFERENCE.md` | API documentation |
| `09-PROJECT-STRUCTURE.md` | Cấu trúc dự án |

### models/

Chứa AI models (BART).

### tests/

Unit tests và property-based tests.

### instance/

Instance-specific files (SQLite database).

### uploads/

Thư mục lưu ảnh upload từ users.

---

## File quan trọng

| File | Mô tả |
|------|-------|
| `run.py` | Entry point, chạy Flask app |
| `requirements.txt` | Python dependencies |
| `.env` | Environment variables |
| `.env.example` | Template cho .env |
| `.gitignore` | Git ignore rules |

---

*Quay lại: [README.md](../README.md)*
