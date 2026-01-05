import hashlib
import os
from gtts import gTTS


class AdvancedTTSService:
    # map key bạn dùng ở frontend -> gTTS lang
    LANG_MAP = {
        "vi": "vi",
        "en": "en",
        "ja": "ja",
        "ko": "ko",
        "fr": "fr",
        "de": "de",
        "es": "es",
        "zh-CN": "zh-cn",
        "zh": "zh-cn",
        "ru": "ru",
        "th": "th",
        "ar": "ar",
        "hi": "hi",
    }

    VOICE_TLDS = {
        "en": ["com", "co.uk", "com.au", "ca"],   # US, UK, AU, CA
        "fr": ["fr", "ca", "com", "co.uk"],
        "de": ["de", "at", "ch", "com"],
        "es": ["es", "com.mx", "com", "co.uk"],
        # các ngôn ngữ khác: để 1 lựa chọn mặc định
        "vi": ["com"],
        "ja": ["com"],
        "ko": ["com"],
        "zh-cn": ["com"],
        "ru": ["com"],
        "th": ["com"],
        "ar": ["com"],
        "hi": ["com"],
    }

    @staticmethod
    def _audio_dir():
        return os.path.join("app", "static", "audio")

    @staticmethod
    def _ok_mp3(path: str) -> bool:
        return os.path.exists(path) and os.path.getsize(path) > 1024

    @classmethod
    def get_available_voices(cls, language=None):
        """
        Trả về format giống cũ:
        voices[lang].female[] / male[] để UI không hỏng.
        Nhưng thực chất là list "voice indexes" đại diện cho tld variants.
        """
        def build_for_lang(lang_key: str):
            gtts_lang = cls.LANG_MAP.get(lang_key, "vi")
            tlvs = cls.VOICE_TLDS.get(gtts_lang, ["com"])
            females = tlvs[:2]
            males = tlvs[2:4] if len(tlvs) > 2 else tlvs[:2]
            return {"female": females, "male": males}

        if language:
            return build_for_lang(language)

        return {k: build_for_lang(k) for k in cls.LANG_MAP.keys()}

    @classmethod
    def text_to_speech(cls, text, target_lang="vi", voice_gender="female", voice_index=0):
        text = (text or "").strip()
        if not text:
            return {"success": False, "error": "Text cannot be empty"}

        gtts_lang = cls.LANG_MAP.get(target_lang, "vi")
        tlvs = cls.VOICE_TLDS.get(gtts_lang, ["com"])

        # gender chỉ dùng để chọn “nửa” danh sách tld
        if voice_gender == "male":
            pool = tlvs[2:4] if len(tlvs) >= 4 else tlvs
        else:
            pool = tlvs[:2] if len(tlvs) >= 2 else tlvs

        try:
            idx = int(voice_index)
        except Exception:
            idx = 0
        if idx < 0 or idx >= len(pool):
            idx = 0

        tld = pool[idx]

        out_dir = cls._audio_dir()
        os.makedirs(out_dir, exist_ok=True)

        key = hashlib.md5(f"{text}{gtts_lang}{tld}".encode("utf-8")).hexdigest()
        filename = f"tts_gtts_{key}.mp3"
        path = os.path.join(out_dir, filename)

        if cls._ok_mp3(path):
            return {
                "success": True,
                "audio_url": f"/static/audio/{filename}",
                "filename": filename,
                "voice": f"gTTS({gtts_lang}, tld={tld})",
                "language": target_lang,
                "engine": "gtts",
            }

        try:
            gTTS(text=text, lang=gtts_lang, tld=tld, slow=False).save(path)
            if not cls._ok_mp3(path):
                return {"success": False, "error": "gTTS generated invalid mp3"}

            return {
                "success": True,
                "audio_url": f"/static/audio/{filename}",
                "filename": filename,
                "voice": f"gTTS({gtts_lang}, tld={tld})",
                "language": target_lang,
                "engine": "gtts",
            }
        except Exception:
            return {"success": False, "error": "TTS failed"}
