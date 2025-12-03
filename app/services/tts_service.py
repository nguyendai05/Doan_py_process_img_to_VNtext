import os
import uuid
from gtts import gTTS
from flask import current_app


class TTSService:
    """Text-to-Speech service using gTTS"""

    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'vi': 'Vietnamese',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-CN': 'Chinese (Simplified)',
    }

    @staticmethod
    def text_to_speech(text, language='en'):
        """
        Convert text to speech audio file
        Returns: path to generated audio file
        """
        if language not in TTSService.SUPPORTED_LANGUAGES:
            language = 'en'

        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        output_folder = current_app.config.get('TTS_OUTPUT_FOLDER', 'app/static/audio')

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        filepath = os.path.join(output_folder, filename)

        # Generate audio
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filepath)

        # Return relative path for web access
        return f"/static/audio/{filename}"

    @staticmethod
    def get_supported_languages():
        """Get list of supported TTS languages"""
        return TTSService.SUPPORTED_LANGUAGES
