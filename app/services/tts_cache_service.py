"""TTS Cache Service for managing audio file caching"""
import hashlib
from typing import Optional
from app import db
from app.models.tts_audio import TTSAudio


class TTSCacheService:
    """Service for managing TTS audio caching"""

    @staticmethod
    def get_cache_key(text: str, language: str) -> str:
        """
        Generate SHA256 hash from text + language combination.
        This ensures different languages for the same text have different cache keys.
        
        Args:
            text: The text content to hash
            language: The language code (e.g., 'vi', 'en')
            
        Returns:
            64-character hexadecimal SHA256 hash string
        """
        combined = f"{text}:{language}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    @staticmethod
    def find_cached(text: str, language: str) -> Optional[TTSAudio]:
        """
        Find cached audio by text and language.
        Uses the TTSAudio model's existing find_cached method.
        
        Args:
            text: The text content to search for
            language: The language code
            
        Returns:
            TTSAudio instance if found, None otherwise
        """
        return TTSAudio.find_cached(text, language)

    @staticmethod
    def save_to_cache(text: str, language: str, file_path: str, user_id: int, 
                      file_size: int = None, duration_ms: int = None,
                      text_block_id: int = None) -> TTSAudio:
        """
        Save generated audio to cache in database.
        
        Args:
            text: The text content that was converted to speech
            language: The language code used for TTS
            file_path: Path to the generated audio file
            user_id: ID of the user who generated the audio
            file_size: Size of the audio file in bytes (optional)
            duration_ms: Duration of the audio in milliseconds (optional)
            text_block_id: Associated text block ID (optional)
            
        Returns:
            The created TTSAudio instance
        """
        text_hash = TTSAudio.generate_hash(text)
        
        tts_audio = TTSAudio(
            user_id=user_id,
            text_content=text,
            text_hash=text_hash,
            language=language,
            file_path=file_path,
            file_size=file_size,
            duration_ms=duration_ms,
            text_block_id=text_block_id
        )
        
        db.session.add(tts_audio)
        db.session.commit()
        
        return tts_audio
