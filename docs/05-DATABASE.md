# 🗄️ Database Schema

## Entity Relationship Diagram

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
│ (file, hash)    │  │ (src, dest)     │  │ (action, entity)│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Tables Summary

| # | Table | Mô tả | Records |
|---|-------|-------|---------|
| 1 | `users` | Người dùng | - |
| 2 | `images` | Ảnh upload | - |
| 3 | `ocr_results` | Kết quả OCR | - |
| 4 | `ocr_segments` | Chi tiết OCR segments | - |
| 5 | `works` | Phiên làm việc | - |
| 6 | `text_blocks` | Khối văn bản | - |
| 7 | `tts_audio` | Audio TTS (cache) | - |
| 8 | `translations` | Bản dịch (cache) | - |
| 9 | `chat_sessions` | Phiên chat | - |
| 10 | `chat_messages` | Tin nhắn chat | - |
| 11 | `activity_logs` | Log hoạt động | - |

---

## Chi tiết Tables

### 1. users

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID user |
| email | VARCHAR(255) | NO | UNI | - | Email đăng nhập |
| password_hash | VARCHAR(255) | NO | - | - | Mật khẩu (bcrypt) |
| full_name | VARCHAR(100) | YES | - | NULL | Họ tên |
| avatar_url | VARCHAR(500) | YES | - | NULL | URL avatar |
| is_active | BOOLEAN | NO | IDX | TRUE | Trạng thái |
| last_login_at | DATETIME | YES | - | NULL | Lần đăng nhập cuối |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |
| updated_at | DATETIME | NO | - | NOW | Ngày cập nhật |

### 2. images

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID ảnh |
| user_id | INT | NO | FK | - | ID user |
| file_name | VARCHAR(255) | NO | - | - | Tên file gốc |
| file_path | VARCHAR(500) | NO | - | - | Đường dẫn |
| file_size | INT | YES | - | NULL | Kích thước (bytes) |
| mime_type | VARCHAR(50) | YES | - | NULL | MIME type |
| width | INT | YES | - | NULL | Chiều rộng (px) |
| height | INT | YES | - | NULL | Chiều cao (px) |
| source | VARCHAR(50) | NO | - | 'upload' | upload/url/camera |
| checksum | VARCHAR(64) | YES | IDX | NULL | SHA256 hash |
| created_at | DATETIME | NO | IDX | NOW | Ngày upload |

### 3. ocr_results

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID kết quả |
| image_id | INT | NO | FK | - | ID ảnh |
| user_id | INT | NO | FK | - | ID user |
| engine | VARCHAR(30) | NO | - | 'easyocr' | OCR engine |
| language | VARCHAR(20) | NO | - | 'vi,en' | Ngôn ngữ |
| raw_text | LONGTEXT | YES | - | NULL | Text thô |
| processed_text | LONGTEXT | YES | - | NULL | Text đã xử lý |
| corrected_text | LONGTEXT | YES | - | NULL | Text sau BART |
| confidence_avg | DECIMAL(5,4) | YES | - | NULL | Độ tin cậy TB |
| processing_time_ms | INT | YES | - | NULL | Thời gian xử lý |
| word_count | INT | YES | - | NULL | Số từ |
| status | ENUM | NO | IDX | 'pending' | pending/processing/completed/failed |
| error_message | TEXT | YES | - | NULL | Lỗi (nếu có) |
| created_at | DATETIME | NO | IDX | NOW | Ngày tạo |
| updated_at | DATETIME | NO | - | NOW | Ngày cập nhật |

### 4. ocr_segments

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID segment |
| ocr_result_id | INT | NO | FK | - | ID kết quả OCR |
| text | VARCHAR(1000) | NO | - | - | Nội dung text |
| confidence | DECIMAL(5,4) | NO | - | - | Độ tin cậy |
| bbox_x1 | INT | YES | - | NULL | Tọa độ x1 |
| bbox_y1 | INT | YES | - | NULL | Tọa độ y1 |
| bbox_x2 | INT | YES | - | NULL | Tọa độ x2 |
| bbox_y2 | INT | YES | - | NULL | Tọa độ y2 |
| position | INT | NO | IDX | 0 | Thứ tự |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |

### 5. works

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID work |
| user_id | INT | NO | FK | - | ID user |
| title | VARCHAR(255) | NO | - | 'Untitled Work' | Tiêu đề |
| description | TEXT | YES | - | NULL | Mô tả |
| ocr_result_id | INT | YES | FK | NULL | Link OCR result |
| is_archived | BOOLEAN | NO | IDX | FALSE | Đã lưu trữ |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |
| updated_at | DATETIME | NO | IDX | NOW | Ngày cập nhật |

### 6. text_blocks

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID block |
| work_id | INT | NO | FK | - | ID work |
| source_type | ENUM | NO | IDX | 'ocr' | ocr/manual/translate/tts/research/edit |
| title | VARCHAR(255) | YES | - | NULL | Tiêu đề |
| content | LONGTEXT | NO | - | - | Nội dung |
| extra_data | JSON | YES | - | NULL | Metadata |
| position | INT | NO | IDX | 0 | Thứ tự |
| is_deleted | BOOLEAN | NO | IDX | FALSE | Soft delete |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |
| updated_at | DATETIME | NO | - | NOW | Ngày cập nhật |

### 7. tts_audio

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID audio |
| user_id | INT | NO | FK | - | ID user |
| text_content | TEXT | NO | - | - | Nội dung text |
| text_hash | VARCHAR(64) | NO | IDX | - | SHA256 hash (cache) |
| language | VARCHAR(10) | NO | IDX | 'vi' | Ngôn ngữ |
| file_path | VARCHAR(500) | NO | - | - | Đường dẫn file |
| file_size | INT | YES | - | NULL | Kích thước |
| duration_ms | INT | YES | - | NULL | Thời lượng |
| text_block_id | INT | YES | FK | NULL | Link text block |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |

### 8. translations

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID translation |
| user_id | INT | NO | FK | - | ID user |
| source_text | TEXT | NO | - | - | Text nguồn |
| source_text_hash | VARCHAR(64) | NO | IDX | - | SHA256 hash |
| source_lang | VARCHAR(10) | NO | IDX | - | Ngôn ngữ nguồn |
| translated_text | TEXT | NO | - | - | Text đã dịch |
| dest_lang | VARCHAR(10) | NO | IDX | - | Ngôn ngữ đích |
| engine | VARCHAR(30) | NO | - | 'google' | Engine dịch |
| text_block_id | INT | YES | FK | NULL | Link text block |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |

**Unique constraint:** `(source_text_hash, source_lang, dest_lang)`

### 9. chat_sessions

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID session |
| user_id | INT | NO | FK | - | ID user |
| title | VARCHAR(255) | NO | - | 'Cuộc trò chuyện mới' | Tiêu đề |
| work_id | INT | YES | FK | NULL | Link work |
| is_archived | BOOLEAN | NO | IDX | FALSE | Đã lưu trữ |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |
| updated_at | DATETIME | NO | IDX | NOW | Ngày cập nhật |

### 10. chat_messages

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID message |
| session_id | INT | NO | FK | - | ID session |
| role | ENUM | NO | IDX | 'user' | user/assistant/system |
| content | TEXT | NO | - | - | Nội dung |
| message_type | ENUM | NO | IDX | 'text' | text/ocr_result/translation/tts/research/error |
| extra_data | JSON | YES | - | NULL | Metadata |
| ocr_result_id | INT | YES | FK | NULL | Link OCR result |
| text_block_id | INT | YES | FK | NULL | Link text block |
| is_deleted | BOOLEAN | NO | IDX | FALSE | Soft delete |
| created_at | DATETIME | NO | IDX | NOW | Ngày tạo |

---

## Views

### v_user_stats
Thống kê user (images, ocr_results, works).

```sql
SELECT * FROM v_user_stats WHERE user_id = 1;
```

### v_ocr_results_detail
OCR results với image info.

```sql
SELECT * FROM v_ocr_results_detail WHERE user_id = 1;
```

## Stored Procedures

### sp_cleanup_old_tts_audio
Xóa file TTS audio cũ.

```sql
CALL sp_cleanup_old_tts_audio(30); -- Xóa audio > 30 ngày
```

---

*Xem thêm: [06-TESTING.md](06-TESTING.md) - Testing*
