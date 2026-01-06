# Database Schema - doan_ocr

## Tổng quan

Database cho ứng dụng OCR nhận diện văn bản tiếng Việt.

## Sơ đồ quan hệ (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USERS                                          │
│  (id, email, password_hash, full_name, avatar_url, is_active, ...)         │
└─────────────────────────────────────────────────────────────────────────────┘
         │                    │                    
         │ 1:N                │ 1:N                
         ▼                    ▼                    
┌─────────────────┐  ┌─────────────────┐  
│     IMAGES      │  │     WORKS       │  
│ (file, path...) │  │ (title, desc)   │  
└─────────────────┘  └─────────────────┘  
         │                    │                    
         │ 1:N                │ 1:N                
         ▼                    ▼                    
┌─────────────────┐  ┌─────────────────┐  
│   OCR_RESULTS   │  │   TEXT_BLOCKS   │  
│ (raw, cleaned)  │  │ (content, type) │  
└─────────────────┘  └─────────────────┘  
         │
         │ 1:N
         ▼
┌─────────────────┐
│  OCR_SEGMENTS   │
│ (text, bbox)    │
└─────────────────┘

┌─────────────────┐  ┌─────────────────┐
│    TTS_AUDIO    │  │  TRANSLATIONS   │
│ (file, lang)    │  │ (src, dest)     │
└─────────────────┘  └─────────────────┘
```

## Danh sách Tables

| # | Table | Mô tả | Records |
|---|-------|-------|---------|
| 1 | `users` | Quản lý người dùng | - |
| 2 | `images` | Lưu trữ ảnh upload | - |
| 3 | `ocr_results` | Kết quả OCR từ ảnh | - |
| 4 | `ocr_segments` | Chi tiết từng segment OCR | - |
| 5 | `works` | Phiên làm việc (workspace) | - |
| 6 | `text_blocks` | Khối văn bản trong work | - |
| 7 | `tts_audio` | File audio TTS (có cache) | - |
| 8 | `translations` | Bản dịch (có cache) | - |

## Chi tiết Tables

### 1. users
Quản lý người dùng hệ thống.

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID user |
| email | VARCHAR(255) | NO | UNI | - | Email đăng nhập |
| password_hash | VARCHAR(255) | NO | - | - | Mật khẩu đã hash (bcrypt) |
| full_name | VARCHAR(100) | YES | - | NULL | Họ tên |
| avatar_url | VARCHAR(500) | YES | - | NULL | URL avatar |
| is_active | BOOLEAN | NO | IDX | TRUE | Trạng thái hoạt động |
| last_login_at | DATETIME | YES | - | NULL | Lần đăng nhập cuối |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |
| updated_at | DATETIME | NO | - | NOW | Ngày cập nhật |

### 2. images
Lưu trữ thông tin ảnh upload.

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID ảnh |
| user_id | INT | NO | FK | - | ID user upload |
| file_name | VARCHAR(255) | NO | - | - | Tên file gốc |
| file_path | VARCHAR(500) | NO | - | - | Đường dẫn lưu trữ |
| file_size | INT UNSIGNED | YES | - | NULL | Kích thước (bytes) |
| mime_type | VARCHAR(50) | YES | - | NULL | MIME type |
| width | INT UNSIGNED | YES | - | NULL | Chiều rộng (px) |
| height | INT UNSIGNED | YES | - | NULL | Chiều cao (px) |
| source | VARCHAR(50) | NO | - | 'upload' | Nguồn: upload/url/camera |
| checksum | VARCHAR(64) | YES | IDX | NULL | SHA256 hash |
| created_at | DATETIME | NO | IDX | NOW | Ngày upload |

### 3. ocr_results
Kết quả OCR từ ảnh.

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
| processing_time_ms | INT UNSIGNED | YES | - | NULL | Thời gian xử lý |
| word_count | INT UNSIGNED | YES | - | NULL | Số từ |
| status | ENUM | NO | IDX | 'pending' | Trạng thái |
| error_message | TEXT | YES | - | NULL | Lỗi (nếu có) |
| created_at | DATETIME | NO | IDX | NOW | Ngày tạo |
| updated_at | DATETIME | NO | - | NOW | Ngày cập nhật |

**Status values:** `pending`, `processing`, `completed`, `failed`

### 4. ocr_segments
Chi tiết từng segment OCR với bounding box.

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
Phiên làm việc (workspace).

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
Khối văn bản trong work.

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID block |
| work_id | INT | NO | FK | - | ID work |
| source_type | ENUM | NO | IDX | 'ocr' | Nguồn gốc |
| title | VARCHAR(255) | YES | - | NULL | Tiêu đề |
| content | LONGTEXT | NO | - | - | Nội dung |
| metadata | JSON | YES | - | NULL | Metadata |
| position | INT | NO | IDX | 0 | Thứ tự |
| is_deleted | BOOLEAN | NO | IDX | FALSE | Soft delete |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |
| updated_at | DATETIME | NO | - | NOW | Ngày cập nhật |

**Source types:** `ocr`, `manual`, `translate`, `tts`, `research`, `edit`

### 7. tts_audio
File audio TTS (có cache).

| Column | Type | Null | Key | Default | Description |
|--------|------|------|-----|---------|-------------|
| id | INT | NO | PRI | auto | ID audio |
| user_id | INT | NO | FK | - | ID user |
| text_content | TEXT | NO | - | - | Nội dung text |
| text_hash | VARCHAR(64) | NO | IDX | - | SHA256 hash (cache) |
| language | VARCHAR(10) | NO | IDX | 'vi' | Ngôn ngữ |
| file_path | VARCHAR(500) | NO | - | - | Đường dẫn file |
| file_size | INT UNSIGNED | YES | - | NULL | Kích thước |
| duration_ms | INT UNSIGNED | YES | - | NULL | Thời lượng |
| text_block_id | INT | YES | FK | NULL | Link text block |
| created_at | DATETIME | NO | - | NOW | Ngày tạo |

### 8. translations
Bản dịch (có cache).

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

**Unique constraint:** (source_text_hash, source_lang, dest_lang) - để cache

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

## Cách sử dụng

### Tạo database mới
```bash
mysql -u root -p < db/schema.sql
```

### Reset database
```bash
mysql -u root -p doan_ocr < db/schema.sql
```

## Lưu ý

1. **Charset**: Sử dụng `utf8mb4` để hỗ trợ emoji và ký tự đặc biệt
2. **Collation**: `utf8mb4_unicode_ci` cho tiếng Việt
3. **Engine**: InnoDB cho transaction support
4. **Soft delete**: Một số tables sử dụng `is_deleted` thay vì xóa thật
5. **Cache**: `tts_audio` và `translations` có cache theo hash
