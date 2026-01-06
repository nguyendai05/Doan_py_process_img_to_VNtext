"""Apply database schema to MySQL"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Kết nối MySQL (không chọn database để có thể tạo mới)
conn = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    charset='utf8mb4',
    autocommit=True
)

cursor = conn.cursor()

print("=" * 60)
print("🔄 APPLYING DATABASE SCHEMA")
print("=" * 60)

# Đọc và thực thi schema
schema_statements = [
    # Tạo database
    """CREATE DATABASE IF NOT EXISTS doan_ocr
       CHARACTER SET utf8mb4
       COLLATE utf8mb4_unicode_ci""",
    
    "USE doan_ocr",
    
    # Xóa tables cũ
    "SET FOREIGN_KEY_CHECKS = 0",
    "DROP TABLE IF EXISTS chat_messages",
    "DROP TABLE IF EXISTS chat_sessions", 
    "DROP TABLE IF EXISTS tts_audio",
    "DROP TABLE IF EXISTS translations",
    "DROP TABLE IF EXISTS activity_logs",
    "DROP TABLE IF EXISTS ocr_segments",
    "DROP TABLE IF EXISTS ocr_results",
    "DROP TABLE IF EXISTS images",
    "DROP TABLE IF EXISTS text_blocks",
    "DROP TABLE IF EXISTS works",
    "DROP TABLE IF EXISTS users",
    "SET FOREIGN_KEY_CHECKS = 1",
    
    # 1. USERS
    """CREATE TABLE users (
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
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 2. IMAGES
    """CREATE TABLE images (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size INT UNSIGNED NULL,
        mime_type VARCHAR(50) NULL,
        width INT UNSIGNED NULL,
        height INT UNSIGNED NULL,
        source VARCHAR(50) DEFAULT 'upload',
        checksum VARCHAR(64) NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_checksum (checksum),
        INDEX idx_created_at (created_at),
        CONSTRAINT fk_images_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 3. OCR_RESULTS
    """CREATE TABLE ocr_results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        image_id INT NOT NULL,
        user_id INT NOT NULL,
        engine VARCHAR(30) DEFAULT 'easyocr',
        language VARCHAR(20) DEFAULT 'vi,en',
        raw_text LONGTEXT NULL,
        processed_text LONGTEXT NULL,
        corrected_text LONGTEXT NULL,
        confidence_avg DECIMAL(5,4) NULL,
        processing_time_ms INT UNSIGNED NULL,
        word_count INT UNSIGNED NULL,
        status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
        error_message TEXT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_image_id (image_id),
        INDEX idx_user_id (user_id),
        INDEX idx_status (status),
        INDEX idx_created_at (created_at),
        CONSTRAINT fk_ocr_results_image FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
        CONSTRAINT fk_ocr_results_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 4. OCR_SEGMENTS
    """CREATE TABLE ocr_segments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ocr_result_id INT NOT NULL,
        text VARCHAR(1000) NOT NULL,
        confidence DECIMAL(5,4) NOT NULL,
        bbox_x1 INT NULL,
        bbox_y1 INT NULL,
        bbox_x2 INT NULL,
        bbox_y2 INT NULL,
        position INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_ocr_result_id (ocr_result_id),
        INDEX idx_position (position),
        CONSTRAINT fk_ocr_segments_result FOREIGN KEY (ocr_result_id) REFERENCES ocr_results(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 5. WORKS
    """CREATE TABLE works (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255) NOT NULL DEFAULT 'Untitled Work',
        description TEXT NULL,
        ocr_result_id INT NULL,
        is_archived BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_ocr_result_id (ocr_result_id),
        INDEX idx_is_archived (is_archived),
        INDEX idx_updated_at (updated_at),
        CONSTRAINT fk_works_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_works_ocr_result FOREIGN KEY (ocr_result_id) REFERENCES ocr_results(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 6. TEXT_BLOCKS
    """CREATE TABLE text_blocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        work_id INT NOT NULL,
        source_type ENUM('ocr', 'manual', 'translate', 'tts', 'research', 'edit') DEFAULT 'ocr',
        title VARCHAR(255) NULL,
        content LONGTEXT NOT NULL,
        extra_data JSON NULL,
        position INT DEFAULT 0,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_work_id (work_id),
        INDEX idx_source_type (source_type),
        INDEX idx_position (position),
        INDEX idx_is_deleted (is_deleted),
        CONSTRAINT fk_text_blocks_work FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 7. CHAT_SESSIONS
    """CREATE TABLE chat_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(255) DEFAULT 'Cuộc trò chuyện mới',
        work_id INT NULL,
        is_archived BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_work_id (work_id),
        INDEX idx_is_archived (is_archived),
        INDEX idx_updated_at (updated_at),
        CONSTRAINT fk_chat_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_chat_sessions_work FOREIGN KEY (work_id) REFERENCES works(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 8. CHAT_MESSAGES
    """CREATE TABLE chat_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL,
        role ENUM('user', 'assistant', 'system') NOT NULL DEFAULT 'user',
        content TEXT NOT NULL,
        message_type ENUM('text', 'ocr_result', 'translation', 'tts', 'research', 'error') DEFAULT 'text',
        extra_data JSON NULL,
        ocr_result_id INT NULL,
        text_block_id INT NULL,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_session_id (session_id),
        INDEX idx_role (role),
        INDEX idx_message_type (message_type),
        INDEX idx_created_at (created_at),
        INDEX idx_is_deleted (is_deleted),
        CONSTRAINT fk_chat_messages_session FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
        CONSTRAINT fk_chat_messages_ocr_result FOREIGN KEY (ocr_result_id) REFERENCES ocr_results(id) ON DELETE SET NULL,
        CONSTRAINT fk_chat_messages_text_block FOREIGN KEY (text_block_id) REFERENCES text_blocks(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 9. TTS_AUDIO
    """CREATE TABLE tts_audio (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        text_content TEXT NOT NULL,
        text_hash VARCHAR(64) NOT NULL,
        language VARCHAR(10) NOT NULL DEFAULT 'vi',
        file_path VARCHAR(500) NOT NULL,
        file_size INT UNSIGNED NULL,
        duration_ms INT UNSIGNED NULL,
        text_block_id INT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_text_hash (text_hash),
        INDEX idx_language (language),
        INDEX idx_text_block_id (text_block_id),
        CONSTRAINT fk_tts_audio_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_tts_audio_text_block FOREIGN KEY (text_block_id) REFERENCES text_blocks(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 10. TRANSLATIONS
    """CREATE TABLE translations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        source_text TEXT NOT NULL,
        source_text_hash VARCHAR(64) NOT NULL,
        source_lang VARCHAR(10) NOT NULL,
        translated_text TEXT NOT NULL,
        dest_lang VARCHAR(10) NOT NULL,
        engine VARCHAR(30) DEFAULT 'google',
        text_block_id INT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_source_text_hash (source_text_hash),
        INDEX idx_source_lang (source_lang),
        INDEX idx_dest_lang (dest_lang),
        INDEX idx_text_block_id (text_block_id),
        UNIQUE INDEX idx_cache (source_text_hash, source_lang, dest_lang),
        CONSTRAINT fk_translations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_translations_text_block FOREIGN KEY (text_block_id) REFERENCES text_blocks(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    
    # 11. ACTIVITY_LOGS
    """CREATE TABLE activity_logs (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        action VARCHAR(50) NOT NULL,
        entity_type VARCHAR(50) NULL,
        entity_id INT NULL,
        details JSON NULL,
        ip_address VARCHAR(45) NULL,
        user_agent VARCHAR(500) NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_action (action),
        INDEX idx_entity (entity_type, entity_id),
        INDEX idx_created_at (created_at),
        CONSTRAINT fk_activity_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
]

# Thực thi từng statement
for i, sql in enumerate(schema_statements):
    try:
        cursor.execute(sql)
        # Chỉ in các statement quan trọng
        if 'CREATE TABLE' in sql:
            table_name = sql.split('CREATE TABLE ')[1].split(' ')[0]
            print(f"✅ Created table: {table_name}")
        elif 'DROP TABLE' in sql:
            pass  # Không in drop
        elif 'USE ' in sql:
            print(f"📂 Using database: doan_ocr")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   SQL: {sql[:100]}...")

# Kiểm tra kết quả
print("\n" + "=" * 60)
print("📋 TABLES CREATED:")
print("=" * 60)
cursor.execute("USE doan_ocr")
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  ✓ {table[0]} ({count} records)")

cursor.close()
conn.close()

print("\n✅ Schema applied successfully!")
