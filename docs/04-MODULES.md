# 🔧 Chi Tiết Các Modules

## 1. Authentication Module

**Files:** `app/routes/auth.py`, `app/models/user.py`

### Công nghệ sử dụng
- `Flask-Login`: Quản lý session người dùng
- `bcrypt`: Mã hóa mật khẩu an toàn
- `Flask-SQLAlchemy`: ORM cho database

### API Endpoints

| Method | Endpoint | Chức năng | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/register` | Đăng ký tài khoản | ❌ |
| POST | `/api/auth/login` | Đăng nhập | ❌ |
| POST | `/api/auth/logout` | Đăng xuất | ✅ |
| GET | `/api/auth/me` | Lấy thông tin user | ✅ |

### Chi tiết implementation
- Mật khẩu hash bằng bcrypt với salt tự động
- Validation: email unique, password >= 6 ký tự
- Session-based authentication
- Cập nhật `last_login_at` mỗi lần đăng nhập

---

## 2. OCR Module

**Files:** `app/routes/ocr.py`, `app/services/ocr_service.py`

### Công nghệ sử dụng
- `EasyOCR`: Engine OCR chính (80+ ngôn ngữ)
- `OpenCV`: Tiền xử lý ảnh
- `PIL/Pillow`: Xử lý ảnh
- `NumPy`: Xử lý mảng

### Quy trình xử lý

```
Upload Image → Preprocessing → EasyOCR → Raw Text → Text Processing → BART → Final
```

### Preprocessing steps
1. Convert to grayscale
2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
3. Denoise với fastNlMeansDenoising
4. Resize nếu ảnh < 300px width

### Output
```json
{
  "raw_text": "Text thô từ OCR",
  "processed_text": "Text sau chuẩn hóa",
  "corrected_text": "Text sau BART",
  "segments": [
    {
      "text": "segment text",
      "confidence": 0.95,
      "bbox": [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
    }
  ]
}
```

---

## 3. Text Processing Module

**Files:** `app/services/text_processing.py`

### Các bước xử lý

#### 1. Unicode Normalization (NFC)
```python
text = unicodedata.normalize('NFC', text)
```

#### 2. Whitespace Normalization
- Loại bỏ multiple spaces
- Chuẩn hóa line breaks
- Trim whitespace

#### 3. OCR Error Correction (Rule-based)

| Lỗi | Sửa thành | Giải thích |
|-----|-----------|------------|
| 0 | o | Số 0 thành chữ o |
| 1 | l | Số 1 thành chữ l |
| 5 | s | Số 5 thành chữ s |
| 8 | B | Số 8 thành chữ B |
| cl | d | Lỗi OCR phổ biến |
| rn | m | Lỗi OCR phổ biến |

#### 4. Junk Character Removal
- Loại bỏ ký tự toán học, ký tự lạ
- Giữ: Vietnamese chars, số, dấu câu cơ bản

---

## 4. BART Correction Module

**Files:** `app/services/model_inference.py`

### Công nghệ
- `Transformers`: Hugging Face library
- `BARTpho`: Model fine-tuned cho tiếng Việt
- `PyTorch`: Deep learning framework
- `SentencePiece`: Tokenization

### Model path
```
models/bartpho_correction_model/
├── config.json
├── model.safetensors
├── tokenizer_config.json
├── sentencepiece.bpe.model
└── ...
```

### Quy trình
1. Chia text thành sentences
2. Gộp sentences thành chunks (~200 chars)
3. Xử lý từng chunk qua BART
4. Ghép kết quả

### Cấu hình
```env
USE_BART_MODEL=true  # Enable/disable
```

---

## 5. TTS Service

**Files:** `app/services/tts_service.py`, `app/services/tts_cache_service.py`

### Ngôn ngữ hỗ trợ

| Code | Language |
|------|----------|
| vi | Vietnamese |
| en | English |
| fr | French |
| de | German |
| es | Spanish |
| ja | Japanese |
| ko | Korean |
| zh-CN | Chinese (Simplified) |

### Caching mechanism
```
Hash = SHA256(text + ":" + language)
```

### API Response
```json
{
  "success": true,
  "audio_url": "/static/audio/tts_xxx.mp3",
  "from_cache": false,
  "duration_ms": null
}
```

### Error codes
| Code | Mô tả |
|------|-------|
| EMPTY_TEXT | Text rỗng hoặc chỉ whitespace |
| TEXT_TOO_LONG | Text > 2000 ký tự |
| UNSUPPORTED_LANGUAGE | Ngôn ngữ không hỗ trợ |
| GENERATION_FAILED | Lỗi khi generate audio |

---

## 6. Translation Service

**Files:** `app/services/translate_service.py`, `app/services/translation_cache_service.py`

### Ngôn ngữ hỗ trợ

| Code | Language |
|------|----------|
| auto | Auto-detect |
| vi | Vietnamese |
| en | English |
| fr | French |
| de | German |
| es | Spanish |
| ja | Japanese |
| ko | Korean |
| zh-cn | Chinese (Simplified) |
| zh-tw | Chinese (Traditional) |
| th | Thai |
| ru | Russian |

### Caching mechanism
```
Hash = SHA256(text + ":" + source_lang + ":" + dest_lang)
```

### API Response
```json
{
  "success": true,
  "translated_text": "Xin chào",
  "source_lang": "en",
  "dest_lang": "vi",
  "from_cache": false
}
```

### Error codes
| Code | Mô tả |
|------|-------|
| EMPTY_TEXT | Text rỗng |
| TEXT_TOO_LONG | Text > 2000 ký tự |
| SAME_LANGUAGE | Source = Destination |
| TRANSLATION_FAILED | Lỗi khi dịch |

---

## 7. Research Service

**Files:** `app/services/research_service.py`

### Analysis types

| Type | Mô tả | Mode |
|------|-------|------|
| summary | Tóm tắt văn bản | Basic + LLM |
| keywords | Trích xuất từ khóa | Basic + LLM |
| questions | Tạo câu hỏi review | Basic + LLM |
| explain | Giải thích đơn giản | LLM only |

### Basic Mode (không cần API key)
- `keywords`: Top 10 keywords (loại stop words)
- `summary`: 3 câu đầu tiên
- `questions`: Câu hỏi từ keywords

### LLM Mode (cần OPENAI_API_KEY)
- Sử dụng GPT-3.5-turbo
- Max 500 tokens response

---

## 8. Work Management

**Files:** `app/routes/work.py`, `app/models/work.py`

### Entities

#### Work
| Field | Type | Mô tả |
|-------|------|-------|
| id | INT | Primary key |
| user_id | INT | FK to users |
| title | VARCHAR(255) | Tiêu đề |
| description | TEXT | Mô tả |
| ocr_result_id | INT | FK to ocr_results |
| is_archived | BOOLEAN | Đã lưu trữ |

#### TextBlock
| Field | Type | Mô tả |
|-------|------|-------|
| id | INT | Primary key |
| work_id | INT | FK to works |
| source_type | ENUM | ocr/manual/translate/tts/research/edit |
| title | VARCHAR(255) | Tiêu đề |
| content | TEXT | Nội dung |
| position | INT | Thứ tự |

### API Endpoints

| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET | `/api/works` | Danh sách works |
| POST | `/api/works` | Tạo work mới |
| GET | `/api/works/<id>` | Chi tiết work |
| PUT | `/api/works/<id>` | Cập nhật work |
| DELETE | `/api/works/<id>` | Xóa work |
| POST | `/api/works/<id>/blocks` | Thêm block |
| DELETE | `/api/works/<id>/blocks/<bid>` | Xóa block |
| POST | `/api/works/<id>/merge` | Gộp blocks |

---

## 9. Chat System

**Files:** `app/routes/chat.py`, `app/models/chat.py`

### Entities

#### ChatSession
| Field | Type | Mô tả |
|-------|------|-------|
| id | INT | Primary key |
| user_id | INT | FK to users |
| title | VARCHAR(255) | Tiêu đề |
| work_id | INT | FK to works (optional) |
| is_archived | BOOLEAN | Đã lưu trữ |

#### ChatMessage
| Field | Type | Mô tả |
|-------|------|-------|
| id | INT | Primary key |
| session_id | INT | FK to chat_sessions |
| role | ENUM | user/assistant/system |
| content | TEXT | Nội dung |
| message_type | ENUM | text/ocr_result/translation/tts/research/error |
| extra_data | JSON | Metadata |

### API Endpoints

| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| GET | `/api/chat/sessions` | Danh sách sessions |
| POST | `/api/chat/sessions` | Tạo session |
| GET | `/api/chat/sessions/<id>` | Chi tiết session |
| PUT | `/api/chat/sessions/<id>` | Cập nhật session |
| DELETE | `/api/chat/sessions/<id>` | Xóa session |
| GET | `/api/chat/sessions/<id>/messages` | Lấy messages |
| POST | `/api/chat/sessions/<id>/messages` | Thêm message |
| DELETE | `/api/chat/messages/<id>` | Xóa message |

---

*Xem thêm: [05-DATABASE.md](05-DATABASE.md) - Database Schema*
