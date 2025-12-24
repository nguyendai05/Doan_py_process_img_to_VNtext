from deep_translator import GoogleTranslator


class TranslateService:
    """Translation service using Google Translate (via deep-translator)"""

    @staticmethod
    def translate(text, dest_lang='en', src_lang='auto'):
        """Translate text to target language"""
        try:
            result = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)

            return {
                'success': True,
                'translated_text': result,
                'src_lang': src_lang,
                'dest_lang': dest_lang
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_supported_languages():
        """Get list of supported languages"""
        return {
            'en': 'English',
            'vi': 'Tiếng Việt',
            'ja': '日本語',
            'ko': '한국어',
            'zh-CN': '中文',
            'fr': 'Français',
            'de': 'Deutsch',
            'es': 'Español',
            'ru': 'Русский',
            'th': 'ไทย',
            'ar': 'العربية',
            'hi': 'हिन्दी'
        }
