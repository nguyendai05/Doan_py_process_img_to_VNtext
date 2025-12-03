from googletrans import Translator


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
