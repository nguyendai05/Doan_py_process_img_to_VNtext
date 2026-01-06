-- ============================================================
-- DATABASE SCHEMA: doan_ocr
-- Ứng dụng OCR nhận diện văn bản tiếng Việt
-- Version: 2.0
-- Updated: 2026-01-07
-- ============================================================

-- Tạo database (nếu chưa có)
CREATE DATABASE IF NOT EXISTS doan_ocr
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE doan_ocr;

-- ============================================================
-- XÓA TABLES CŨ (theo thứ tự dependency)
-- ============================================================
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS activity_logs;
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS ocr_segments;
DROP TABLE IF EXISTS ocr_results;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS text_blocks;
DROP TABLE IF EXISTS works;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 1. USERS - Quản lý người dùng
-- ============================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NULL,
    avatar_url VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE INDEX idx_email (email),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng quản lý người dùng';

-- ============================================================
-- 2. IMAGES - Lưu trữ ảnh upload
-- ============================================================
CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL COMMENT 'Tên file gốc',
    file_path VARCHAR(500) NOT NULL COMMENT 'Đường dẫn lưu trữ',
    file_size INT UNSIGNED NULL COMMENT 'Kích thước file (bytes)',
    mime_type VARCHAR(50) NULL COMMENT 'image/jpeg, image/png',
    width INT UNSIGNED NULL COMMENT 'Chiều rộng ảnh (px)',
    height INT UNSIGNED NULL COMMENT 'Chiều cao ảnh (px)',
    source VARCHAR(50) DEFAULT 'upload' COMMENT 'upload, url, camera',
    checksum VARCHAR(64) NULL COMMENT 'SHA256 hash để detect duplicate',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_checksum (checksum),
    INDEX idx_created_at (created_at),
    
    CONSTRAINT fk_images_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu trữ ảnh upload';

-- ============================================================
-- 3. OCR_RESULTS - Kết quả OCR từ ảnh
-- ============================================================
CREATE TABLE ocr_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    user_id INT NOT NULL,
    
    -- OCR Engine info
    engine VARCHAR(30) DEFAULT 'easyocr' COMMENT 'easyocr, tesseract, google_vision',
    language VARCHAR(20) DEFAULT 'vi,en' COMMENT 'Ngôn ngữ OCR',
    
    -- Text outputs
    raw_text LONGTEXT NULL COMMENT 'Text thô từ OCR',
    processed_text LONGTEXT NULL COMMENT 'Text sau khi xử lý (normalize, clean)',
    corrected_text LONGTEXT NULL COMMENT 'Text sau BART correction',
    
    -- Metadata
    confidence_avg DECIMAL(5,4) NULL COMMENT 'Độ tin cậy trung bình (0-1)',
    processing_time_ms INT UNSIGNED NULL COMMENT 'Thời gian xử lý (ms)',
    word_count INT UNSIGNED NULL COMMENT 'Số từ nhận diện được',
    
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_image_id (image_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    
    CONSTRAINT fk_ocr_results_image 
        FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    CONSTRAINT fk_ocr_results_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu kết quả OCR';

-- ============================================================
-- 4. OCR_SEGMENTS - Chi tiết từng đoạn text OCR
-- ============================================================
CREATE TABLE ocr_segments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ocr_result_id INT NOT NULL,
    
    text VARCHAR(1000) NOT NULL COMMENT 'Nội dung text segment',
    confidence DECIMAL(5,4) NOT NULL COMMENT 'Độ tin cậy (0-1)',
    
    -- Bounding box coordinates
    bbox_x1 INT NULL,
    bbox_y1 INT NULL,
    bbox_x2 INT NULL,
    bbox_y2 INT NULL,
    
    position INT DEFAULT 0 COMMENT 'Thứ tự segment trong ảnh',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_ocr_result_id (ocr_result_id),
    INDEX idx_position (position),
    
    CONSTRAINT fk_ocr_segments_result 
        FOREIGN KEY (ocr_result_id) REFERENCES ocr_results(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu chi tiết từng segment OCR với bounding box';

-- ============================================================
-- 5. WORKS - Phiên làm việc (workspace)
-- ============================================================
CREATE TABLE works (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    title VARCHAR(255) NOT NULL DEFAULT 'Untitled Work',
    description TEXT NULL,
    
    -- Có thể link với OCR result
    ocr_result_id INT NULL COMMENT 'Link đến kết quả OCR gốc (nếu có)',
    
    is_archived BOOLEAN DEFAULT FALSE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_ocr_result_id (ocr_result_id),
    INDEX idx_is_archived (is_archived),
    INDEX idx_updated_at (updated_at),
    
    CONSTRAINT fk_works_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_works_ocr_result 
        FOREIGN KEY (ocr_result_id) REFERENCES ocr_results(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng quản lý phiên làm việc';

-- ============================================================
-- 6. TEXT_BLOCKS - Khối văn bản trong work
-- ============================================================
CREATE TABLE text_blocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    work_id INT NOT NULL,
    
    source_type ENUM('ocr', 'manual', 'translate', 'tts', 'research', 'edit') 
        DEFAULT 'ocr' COMMENT 'Nguồn gốc text block',
    
    title VARCHAR(255) NULL,
    content LONGTEXT NOT NULL,
    
    -- Metadata cho các loại khác nhau
    extra_data JSON NULL COMMENT 'Lưu thông tin bổ sung (audio_url, source_lang, etc.)',
    
    position INT DEFAULT 0 COMMENT 'Thứ tự trong work',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT 'Soft delete',
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_work_id (work_id),
    INDEX idx_source_type (source_type),
    INDEX idx_position (position),
    INDEX idx_is_deleted (is_deleted),
    
    CONSTRAINT fk_text_blocks_work 
        FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu các khối văn bản trong work';

-- ============================================================
-- 7. TTS_AUDIO - Lưu trữ file audio TTS
-- ============================================================
CREATE TABLE tts_audio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    text_content TEXT NOT NULL COMMENT 'Nội dung text đã convert',
    text_hash VARCHAR(64) NOT NULL COMMENT 'SHA256 hash của text để cache',
    
    language VARCHAR(10) NOT NULL DEFAULT 'vi',
    
    file_path VARCHAR(500) NOT NULL,
    file_size INT UNSIGNED NULL,
    duration_ms INT UNSIGNED NULL COMMENT 'Thời lượng audio (ms)',
    
    -- Link đến text block nếu có
    text_block_id INT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_text_hash (text_hash),
    INDEX idx_language (language),
    INDEX idx_text_block_id (text_block_id),
    
    CONSTRAINT fk_tts_audio_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_tts_audio_text_block 
        FOREIGN KEY (text_block_id) REFERENCES text_blocks(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu file audio TTS (có cache theo text hash)';

-- ============================================================
-- 8. TRANSLATIONS - Lưu trữ bản dịch
-- ============================================================
CREATE TABLE translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    source_text TEXT NOT NULL,
    source_text_hash VARCHAR(64) NOT NULL COMMENT 'SHA256 hash để cache',
    source_lang VARCHAR(10) NOT NULL,
    
    translated_text TEXT NOT NULL,
    dest_lang VARCHAR(10) NOT NULL,
    
    engine VARCHAR(30) DEFAULT 'google' COMMENT 'google, deepl, etc.',
    
    -- Link đến text block nếu có
    text_block_id INT NULL,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_id (user_id),
    INDEX idx_source_text_hash (source_text_hash),
    INDEX idx_source_lang (source_lang),
    INDEX idx_dest_lang (dest_lang),
    INDEX idx_text_block_id (text_block_id),
    
    -- Unique constraint để cache
    UNIQUE INDEX idx_cache (source_text_hash, source_lang, dest_lang),
    
    CONSTRAINT fk_translations_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_translations_text_block 
        FOREIGN KEY (text_block_id) REFERENCES text_blocks(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Bảng lưu bản dịch (có cache)';

-- ============================================================
-- VIEWS - Các view hữu ích
-- ============================================================

-- View: Thống kê user
CREATE OR REPLACE VIEW v_user_stats AS
SELECT 
    u.id AS user_id,
    u.email,
    u.full_name,
    COUNT(DISTINCT i.id) AS total_images,
    COUNT(DISTINCT o.id) AS total_ocr_results,
    COUNT(DISTINCT w.id) AS total_works,
    u.last_login_at,
    u.created_at
FROM users u
LEFT JOIN images i ON u.id = i.user_id
LEFT JOIN ocr_results o ON u.id = o.user_id
LEFT JOIN works w ON u.id = w.user_id
WHERE u.is_active = TRUE
GROUP BY u.id;

-- View: OCR results với image info
CREATE OR REPLACE VIEW v_ocr_results_detail AS
SELECT 
    o.id AS ocr_result_id,
    o.user_id,
    o.image_id,
    i.file_name,
    i.file_path,
    o.engine,
    o.language,
    o.raw_text,
    o.processed_text,
    o.corrected_text,
    o.confidence_avg,
    o.processing_time_ms,
    o.word_count,
    o.status,
    o.created_at
FROM ocr_results o
JOIN images i ON o.image_id = i.id;

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

DELIMITER //

-- Procedure: Cleanup old TTS audio files (older than 30 days)
CREATE PROCEDURE sp_cleanup_old_tts_audio(IN days_old INT)
BEGIN
    DELETE FROM tts_audio 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY);
    
    SELECT ROW_COUNT() AS deleted_count;
END //

DELIMITER ;

-- ============================================================
-- INITIAL DATA
-- ============================================================

-- Không có initial data cần thiết

-- ============================================================
-- VERIFICATION
-- ============================================================
SELECT 'Schema created successfully!' AS status;
SHOW TABLES;
