"""Translation Cache Service for managing translation result caching"""
import hashlib
from typing import Optional
from app import db
from app.models.translation import Translation


class TranslationCacheService:
    """Service for managing translation result caching"""

    @staticmethod
    def get_cache_key(text: str, source_lang: str, dest_lang: str) -> str:
        """
        Generate SHA256 hash from text + source_lang + dest_lang combination.
        This ensures different language pairs for the same text have different cache keys.
        
        Args:
            text: The text content to hash
            source_lang: The source language code (e.g., 'vi', 'en', 'auto')
            dest_lang: The destination language code (e.g., 'vi', 'en')
            
        Returns:
            64-character hexadecimal SHA256 hash string
        """
        combined = f"{text}:{source_lang}:{dest_lang}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    @staticmethod
    def find_cached(text: str, source_lang: str, dest_lang: str) -> Optional[Translation]:
        """
        Find cached translation by text and language pair.
        Uses the Translation model's existing find_cached method.
        
        Args:
            text: The text content to search for
            source_lang: The source language code
            dest_lang: The destination language code
            
        Returns:
            Translation instance if found, None otherwise
        """
        return Translation.find_cached(text, source_lang, dest_lang)

    @staticmethod
    def save_to_cache(text: str, source_lang: str, dest_lang: str, 
                      translated_text: str, user_id: int,
                      text_block_id: int = None) -> Translation:
        """
        Save translation result to cache in database.
        
        Args:
            text: The source text that was translated
            source_lang: The source language code
            dest_lang: The destination language code
            translated_text: The translated text result
            user_id: ID of the user who requested the translation
            text_block_id: Associated text block ID (optional)
            
        Returns:
            The created Translation instance
        """
        text_hash = Translation.generate_hash(text)
        
        translation = Translation(
            user_id=user_id,
            source_text=text,
            source_text_hash=text_hash,
            source_lang=source_lang,
            translated_text=translated_text,
            dest_lang=dest_lang,
            engine='google',
            text_block_id=text_block_id
        )
        
        db.session.add(translation)
        db.session.commit()
        
        return translation
