import os
from gtts import gTTS
from flask import url_for
import hashlib

class TTSService:
    """Text-to-Speech service using gTTS"""

    @staticmethod
    def text_to_speech(text, language='vi'):
        """Convert text to speech and return audio file path"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            output_folder = os.path.join('app', 'static', 'audio')
            os.makedirs(output_folder, exist_ok=True)

            # Tạo tên file unique
            text_hash = hashlib.md5(text.encode()).hexdigest()
            filename = f"tts_{text_hash}.mp3"
            filepath = os.path.join(output_folder, filename)

            # Tạo file audio
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(filepath)

            # Trả về URL tương đối
            return f"/static/audio/{filename}"

        except Exception as e:
            raise Exception(f"TTS failed: {str(e)}")

    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return {
            'vi': 'Tiếng Việt',
            'en': 'English',
            'ja': '日本語',
            'ko': '한국어',
            'zh-cn': '中文',
            'fr': 'Français',
            'de': 'Deutsch',
            'es': 'Español'
        }