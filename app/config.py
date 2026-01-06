import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'doan_ocr')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Use SQLite for quick dev, set USE_SQLITE=false in .env for MySQL
    USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() == 'true'
    
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    else:
        # URL encode password to handle special characters like @
        encoded_password = quote_plus(DB_PASSWORD)
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))  # 5MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png').split(','))
    
    # OCR
    OCR_LANGUAGES = os.getenv('OCR_LANGUAGES', 'en,vi').split(',')
    
    # Text Processing
    MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', 2000))
    
    # TTS
    TTS_OUTPUT_FOLDER = os.getenv('TTS_OUTPUT_FOLDER', 'app/static/audio')
    
    # External APIs
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
