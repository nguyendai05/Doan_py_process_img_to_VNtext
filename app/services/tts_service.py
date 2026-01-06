import os
import uuid
from gtts import gTTS
from flask import current_app
from app.services.tts_cache_service import TTSCacheService


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
            language = 'vi'

        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        
        # Use Flask's static folder path for correct absolute path
        output_folder = os.path.join(current_app.static_folder, 'audio')

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        filepath = os.path.join(output_folder, filename)
        
        print(f"[TTS] Generating audio to: {filepath}")

        # Generate audio
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filepath)
        
        print(f"[TTS] File created: {os.path.exists(filepath)}")

        # Return relative path for web access
        return f"/static/audio/{filename}"

    @staticmethod
    def text_to_speech_with_cache(text: str, language: str, user_id: int) -> dict:
        """
        Generate TTS with caching support.
        Checks cache first, generates new audio if not cached.
        
        Args:
            text: The text content to convert to speech
            language: The language code (e.g., 'vi', 'en')
            user_id: ID of the user requesting TTS
            
        Returns:
            dict with keys:
                - audio_url: URL path to the audio file
                - from_cache: True if returned from cache, False if newly generated
                - duration_ms: Duration in milliseconds (if available)
        """
        if language not in TTSService.SUPPORTED_LANGUAGES:
            language = 'vi'

        # Check cache first
        cached_audio = TTSCacheService.find_cached(text, language)
        if cached_audio:
            # Verify the cached file actually exists on disk
            output_folder = os.path.join(current_app.static_folder, 'audio')
            filename = cached_audio.file_path.split('/')[-1]
            filepath = os.path.join(output_folder, filename)
            
            if os.path.exists(filepath):
                return {
                    'audio_url': cached_audio.file_path,
                    'from_cache': True,
                    'duration_ms': cached_audio.duration_ms
                }
            # File doesn't exist, delete stale cache entry and regenerate
            from app import db
            db.session.delete(cached_audio)
            db.session.commit()

        # Generate new audio
        audio_url = TTSService.text_to_speech(text, language)
        
        # Get file size for cache entry
        output_folder = os.path.join(current_app.static_folder, 'audio')
        filename = audio_url.split('/')[-1]
        filepath = os.path.join(output_folder, filename)
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else None

        # Save to cache
        TTSCacheService.save_to_cache(
            text=text,
            language=language,
            file_path=audio_url,
            user_id=user_id,
            file_size=file_size
        )

        return {
            'audio_url': audio_url,
            'from_cache': False,
            'duration_ms': None
        }

    @staticmethod
    def get_supported_languages():
        """Get list of supported TTS languages"""
        return TTSService.SUPPORTED_LANGUAGES
