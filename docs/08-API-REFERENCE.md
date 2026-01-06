# 📚 API Reference

## Base URL

```
http://localhost:5000/api
```

## Authentication

Tất cả endpoints (trừ register, login, và một số GET endpoints) yêu cầu authentication.

Session cookie được set sau khi login thành công.

---

## Auth Endpoints

### POST /api/auth/register

Đăng ký tài khoản mới.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "message": "Registration successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": null,
    "is_active": true,
    "created_at": "2026-01-07T10:00:00"
  }
}
```

**Errors:**
- 400: Email/password required, password < 6 chars
- 409: Email already registered

---

### POST /api/auth/login

Đăng nhập.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "last_login_at": "2026-01-07T10:00:00"
  }
}
```

**Errors:**
- 400: No data provided
- 401: Invalid email or password
- 403: Account is disabled

---

### POST /api/auth/logout

Đăng xuất. Requires auth.

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

### GET /api/auth/me

Lấy thông tin user hiện tại. Requires auth.

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "avatar_url": null,
    "is_active": true,
    "last_login_at": "2026-01-07T10:00:00",
    "created_at": "2026-01-01T00:00:00"
  }
}
```

---

## OCR Endpoints

### POST /api/ocr/single

OCR một ảnh. Requires auth.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `image` (file)

**cURL:**
```bash
curl -X POST http://localhost:5000/api/ocr/single \
  -H "Cookie: session=..." \
  -F "image=@/path/to/image.jpg"
```

**Response (200):**
```json
{
  "success": true,
  "raw_text": "Text thô từ OCR",
  "processed_text": "Text sau xử lý",
  "bart_output": "Text sau BART correction",
  "segments": [
    {
      "text": "segment text",
      "confidence": 0.95,
      "bbox": [[0,0], [100,0], [100,30], [0,30]]
    }
  ],
  "image_id": 1,
  "ocr_result_id": 1,
  "work_id": 1
}
```

**Errors:**
- 400: No image, invalid file type, file too large
- 500: Processing error

---

## Tools Endpoints

### POST /api/tools/tts

Text-to-Speech. Requires auth.

**Request:**
```json
{
  "text": "Xin chào",
  "language": "vi"
}
```

**Response (200):**
```json
{
  "success": true,
  "audio_url": "/static/audio/tts_xxx.mp3",
  "from_cache": false,
  "duration_ms": null
}
```

**Errors:**
- 400: EMPTY_TEXT, TEXT_TOO_LONG, UNSUPPORTED_LANGUAGE
- 500: GENERATION_FAILED

**Supported languages:** vi, en, fr, de, es, ja, ko, zh-CN

---

### GET /api/tools/tts/languages

Lấy danh sách ngôn ngữ TTS. No auth required.

**Response (200):**
```json
{
  "languages": {
    "vi": "Vietnamese",
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-CN": "Chinese (Simplified)"
  }
}
```

---

### POST /api/tools/translate

Dịch văn bản. Requires auth.

**Request:**
```json
{
  "text": "Hello world",
  "dest_lang": "vi",
  "src_lang": "en"
}
```

**Response (200):**
```json
{
  "success": true,
  "translated_text": "Xin chào thế giới",
  "source_lang": "en",
  "dest_lang": "vi",
  "from_cache": false
}
```

**Errors:**
- 400: EMPTY_TEXT, TEXT_TOO_LONG, SAME_LANGUAGE
- 500: TRANSLATION_FAILED

**Supported languages:** auto, vi, en, fr, de, es, ja, ko, zh-cn, zh-tw, th, ru

---

### GET /api/tools/translate/languages

Lấy danh sách ngôn ngữ dịch. No auth required.

**Response (200):**
```json
{
  "languages": {
    "en": "English",
    "vi": "Vietnamese",
    "fr": "French",
    ...
  }
}
```

---

### POST /api/tools/research

Phân tích văn bản. Requires auth.

**Request:**
```json
{
  "text": "Your text here",
  "type": "summary"
}
```

**Types:** summary, keywords, questions, explain (LLM only)

**Response (200):**
```json
{
  "success": true,
  "type": "summary",
  "result": "Tóm tắt văn bản..."
}
```

---

## Works Endpoints

### GET /api/works

Danh sách works. Requires auth.

**Response (200):**
```json
{
  "works": [
    {
      "id": 1,
      "title": "My Work",
      "description": null,
      "block_count": 2,
      "created_at": "2026-01-07T10:00:00"
    }
  ]
}
```

---

### POST /api/works

Tạo work mới. Requires auth.

**Request:**
```json
{
  "title": "New Work",
  "content": "Initial content",
  "source_type": "manual"
}
```

**Response (201):**
```json
{
  "message": "Work created",
  "work": {
    "id": 1,
    "title": "New Work",
    "text_blocks": [...]
  }
}
```

---

### GET /api/works/:id

Chi tiết work. Requires auth.

**Response (200):**
```json
{
  "work": {
    "id": 1,
    "title": "My Work",
    "text_blocks": [
      {
        "id": 1,
        "content": "Block content",
        "source_type": "ocr",
        "position": 0
      }
    ]
  }
}
```

---

### PUT /api/works/:id

Cập nhật work. Requires auth.

**Request:**
```json
{
  "title": "Updated Title"
}
```

---

### DELETE /api/works/:id

Xóa work. Requires auth.

---

### POST /api/works/:id/blocks

Thêm text block. Requires auth.

**Request:**
```json
{
  "content": "New block content",
  "source_type": "manual",
  "title": "Block Title"
}
```

---

### DELETE /api/works/:id/blocks/:block_id

Xóa text block. Requires auth.

---

### POST /api/works/:id/merge

Gộp nhiều blocks. Requires auth.

**Request:**
```json
{
  "block_ids": [1, 2, 3]
}
```

---

## Chat Endpoints

### GET /api/chat/sessions

Danh sách chat sessions. Requires auth.

---

### POST /api/chat/sessions

Tạo session mới. Requires auth.

**Request:**
```json
{
  "title": "New Chat"
}
```

---

### GET /api/chat/sessions/:id

Chi tiết session với messages. Requires auth.

---

### PUT /api/chat/sessions/:id

Cập nhật session. Requires auth.

---

### DELETE /api/chat/sessions/:id

Xóa session. Requires auth.

---

### GET /api/chat/sessions/:id/messages

Lấy messages của session. Requires auth.

---

### POST /api/chat/sessions/:id/messages

Thêm message. Requires auth.

**Request:**
```json
{
  "content": "Message content",
  "role": "user",
  "message_type": "text"
}
```

---

### DELETE /api/chat/messages/:id

Xóa message. Requires auth.

---

## Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE"
}
```

**Common error codes:**
- EMPTY_TEXT
- TEXT_TOO_LONG
- SAME_LANGUAGE
- UNSUPPORTED_LANGUAGE
- GENERATION_FAILED
- TRANSLATION_FAILED

---

*Xem thêm: [09-PROJECT-STRUCTURE.md](09-PROJECT-STRUCTURE.md) - Cấu trúc dự án*
