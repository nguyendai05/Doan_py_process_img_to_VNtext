from googletrans import Translator
from app.services.translation_cache_service import TranslationCacheService


class TranslateService:
    """Translation service using Google Translate"""

    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'vi': 'Vietnamese',
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'th': 'Thai',
        'ru': 'Russian',
    }

    def __init__(self):
        self.translator = Translator()

    def translate(self, text, dest_lang, src_lang='auto'):
        """
        Translate text to target language
        Args:
            text: Text to translate
            dest_lang: Target language code
            src_lang: Source language code (auto-detect if 'auto')
        Returns:
            dict with translated text and detected source language
        """
        try:
            result = self.translator.translate(text, dest=dest_lang, src=src_lang)
            return {
                'success': True,
                'translated_text': result.text,
                'source_lang': result.src,
                'dest_lang': dest_lang
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def detect_language(self, text):
        """Detect language of text"""
        try:
            detection = self.translator.detect(text)
            return {
                'success': True,
                'language': detection.lang,
                'confidence': detection.confidence
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return TranslateService.SUPPORTED_LANGUAGES

    def translate_with_cache(self, text: str, dest_lang: str, src_lang: str = 'auto', user_id: int = None) -> dict:
        """
        Translate text with caching support.
        Checks cache first, performs translation if not cached, then saves to cache.
        
        Args:
            text: Text to translate
            dest_lang: Target language code
            src_lang: Source language code (auto-detect if 'auto')
            user_id: ID of the user requesting translation (required for caching)
            
        Returns:
            dict with:
                - success: bool
                - translated_text: str
                - source_lang: str (detected or specified)
                - dest_lang: str
                - from_cache: bool
                - error: str (if failed)
        """
        # Check cache first
        cached = TranslationCacheService.find_cached(text, src_lang, dest_lang)
        if cached:
            return {
                'success': True,
                'translated_text': cached.translated_text,
                'source_lang': cached.source_lang,
                'dest_lang': cached.dest_lang,
                'from_cache': True
            }
        
        # Cache miss - perform translation
        result = self.translate(text, dest_lang, src_lang)
        
        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error', 'Translation failed'),
                'from_cache': False
            }
        
        # Save to cache if user_id is provided
        if user_id is not None:
            try:
                # Use the detected source language for caching when src_lang is 'auto'
                cache_source_lang = result['source_lang'] if src_lang == 'auto' else src_lang
                TranslationCacheService.save_to_cache(
                    text=text,
                    source_lang=cache_source_lang,
                    dest_lang=dest_lang,
                    translated_text=result['translated_text'],
                    user_id=user_id
                )
            except Exception as e:
                # Log error but don't fail the translation
                # Cache save failure shouldn't affect the user experience
                pass
        
        return {
            'success': True,
            'translated_text': result['translated_text'],
            'source_lang': result['source_lang'],
            'dest_lang': dest_lang,
            'from_cache': False
        }
