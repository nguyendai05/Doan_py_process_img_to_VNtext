import asyncio
import hashlib
import os
import random

import edge_tts
from gtts import gTTS


class AdvancedTTSService:
    """Advanced Text-to-Speech service using Microsoft Edge TTS + gTTS fallback"""

    VOICES = {
        "vi": {
            "female": ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"],
            "male": ["vi-VN-NamMinhNeural"],
        },
        # bạn có thể giữ thêm các ngôn ngữ khác ở đây
    }

    STYLES = [
        "general",
        "cheerful",
        "sad",
        "angry",
        "terrified",
        "shouting",
        "whispering",
        "newscast",
        "customer-service",
        "assistant",
    ]

    @staticmethod
    def _audio_dir():
        return os.path.join("app", "static", "audio")

    @staticmethod
    def _is_valid_mp3(path: str) -> bool:
        # tránh cache file rỗng/hỏng
        return os.path.exists(path) and os.path.getsize(path) > 1024

    @staticmethod
    async def _edge_generate_with_retry(text, voice, rate, pitch, style=None, max_retries=3):
        """
        Edge-TTS generator with retry.
        If still fails -> raise, so caller can fallback to gTTS.
        """
        # Cache key (edge)
        text_hash = hashlib.md5(f"{text}{voice}{rate}{pitch}{style}".encode()).hexdigest()
        filename = f"tts_{text_hash}.mp3"
        output_dir = AdvancedTTSService._audio_dir()
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        # cache chỉ khi hợp lệ
        if AdvancedTTSService._is_valid_mp3(filepath):
            return filename

        # nếu có file nhưng rỗng/hỏng -> xóa
        if os.path.exists(filepath) and not AdvancedTTSService._is_valid_mp3(filepath):
            try:
                os.remove(filepath)
            except:
                pass

        # đảm bảo format rate/pitch đúng kiểu edge-tts: +N% / -N% ; +NHz / -NHz
        # (route của bạn đã normalize rồi, nhưng giữ thêm phòng thủ)
        if rate and rate[0].isdigit():
            rate = "+" + rate
        if pitch and pitch[0].isdigit():
            pitch = "+" + pitch
        if not str(rate).endswith("%"):
            rate = f"{rate}%"
        if not str(pitch).endswith("Hz"):
            pitch = f"{pitch}Hz"

        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                print(f"🎤 TTS attempt {attempt}/{max_retries}")
                # jitter nhỏ (không giải quyết 403, nhưng giữ lại cũng ok)
                await asyncio.sleep(random.uniform(0.2, 0.8))

                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate,
                    pitch=pitch,
                )
                await communicate.save(filepath)

                # verify
                if not AdvancedTTSService._is_valid_mp3(filepath):
                    raise RuntimeError("edge-tts generated empty/invalid mp3")

                return filename

            except Exception as e:
                last_err = e
                print(f"⚠️ TTS attempt {attempt} failed: {e}")

                # dọn file hỏng
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass

                # backoff (không cứu được 403 nhưng để không spam)
                if attempt < max_retries:
                    await asyncio.sleep((2 ** (attempt - 1)) + random.uniform(0, 0.5))

        raise RuntimeError(f"TTS failed after {max_retries} attempts: {last_err}")

    @staticmethod
    def _gtts_generate(text, target_lang):
        """
        Fallback TTS using Google TTS (gTTS).
        """
        # map lang cho gTTS
        lang_map = {
            "vi": "vi",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
            "fr": "fr",
            "de": "de",
            "es": "es",
            "zh-CN": "zh-cn",
            "zh": "zh-cn",
        }
        gtts_lang = lang_map.get(target_lang, "vi")

        text_hash = hashlib.md5(f"{text}{gtts_lang}gtts".encode()).hexdigest()
        filename = f"tts_gtts_{text_hash}.mp3"
        output_dir = AdvancedTTSService._audio_dir()
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        if AdvancedTTSService._is_valid_mp3(filepath):
            return filename

        if os.path.exists(filepath) and not AdvancedTTSService._is_valid_mp3(filepath):
            try:
                os.remove(filepath)
            except:
                pass

        gTTS(text=text, lang=gtts_lang, slow=False).save(filepath)

        if not AdvancedTTSService._is_valid_mp3(filepath):
            raise RuntimeError("gTTS generated empty/invalid mp3")

        return filename

    @staticmethod
    def text_to_speech(
        text,
        target_lang="vi",
        voice_gender="female",
        voice_index=0,
        rate="+0%",
        pitch="+0Hz",
        style="general",
    ):
        """
        Convert text to speech.
        Try Edge-TTS first. If Edge fails (403...), fallback to gTTS.
        """
        try:
            text = (text or "").strip()
            if not text:
                return {"success": False, "error": "Text cannot be empty"}

            # chọn voice cho edge (nếu lang không có, fallback gTTS luôn)
            if target_lang not in AdvancedTTSService.VOICES:
                filename = AdvancedTTSService._gtts_generate(text, target_lang)
                return {
                    "success": True,
                    "audio_url": f"/static/audio/{filename}",
                    "filename": filename,
                    "voice": "gTTS",
                    "language": target_lang,
                    "engine": "gtts",
                }

            voices = AdvancedTTSService.VOICES[target_lang].get(voice_gender, [])
            if not voices or voice_index >= len(voices):
                return {"success": False, "error": "Invalid voice selection"}

            voice = voices[voice_index]

            # ---- TRY EDGE ----
            try:
                filename = asyncio.run(
                    AdvancedTTSService._edge_generate_with_retry(
                        text=text,
                        voice=voice,
                        rate=rate,
                        pitch=pitch,
                        style=style,
                        max_retries=3,
                    )
                )
                return {
                    "success": True,
                    "audio_url": f"/static/audio/{filename}",
                    "filename": filename,
                    "voice": voice,
                    "language": target_lang,
                    "engine": "edge-tts",
                }

            except Exception as e:
                # ---- FALLBACK gTTS ----
                filename = AdvancedTTSService._gtts_generate(text, target_lang)
                return {
                    "success": True,
                    "audio_url": f"/static/audio/{filename}",
                    "filename": filename,
                    "voice": "gTTS",
                    "language": target_lang,
                    "engine": "gtts",
                    "warning": f"edge-tts failed, fallback to gTTS: {str(e)}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_available_voices(language=None):
        if language:
            return AdvancedTTSService.VOICES.get(language, {})
        return AdvancedTTSService.VOICES

    @staticmethod
    def get_available_styles():
        return AdvancedTTSService.STYLES
