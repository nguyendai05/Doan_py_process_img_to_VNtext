from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from app.services.tts_service import TTSService
from app.services.translate_service import TranslateService
from app.services.research_service import ResearchService
from app.services.gemini_service import GeminiService
from app.services.advanced_tts_service import AdvancedTTSService


tools_bp = Blueprint('tools', __name__)


@tools_bp.route('/tts', methods=['POST'])
@login_required
def text_to_speech():
    """Convert text to speech"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']
    language = data.get('language', 'en')

    # Check text length
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 2000)
    if len(text) > max_length:
        return jsonify({'error': f'Text too long. Max {max_length} characters'}), 400

    try:
        audio_path = TTSService.text_to_speech(text, language)
        return jsonify({
            'success': True,
            'audio_url': audio_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tts/languages', methods=['GET'])
def get_tts_languages():
    """Get supported TTS languages"""
    return jsonify({
        'languages': TTSService.get_supported_languages()
    })


@tools_bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """Translate text"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']
    dest_lang = data.get('dest_lang', 'en')
    src_lang = data.get('src_lang', 'auto')

    # Check text length
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 2000)
    if len(text) > max_length:
        return jsonify({'error': f'Text too long. Max {max_length} characters'}), 400

    service = TranslateService()
    result = service.translate(text, dest_lang, src_lang)

    if result['success']:
        return jsonify(result)
    else:
        return jsonify({'error': result.get('error', 'Translation failed')}), 500


@tools_bp.route('/translate/languages', methods=['GET'])
def get_translate_languages():
    """Get supported translation languages"""
    return jsonify({
        'languages': TranslateService.get_supported_languages()
    })


@tools_bp.route('/research', methods=['POST'])
@login_required
def research_text():
    """Analyze/research text"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']
    analysis_type = data.get('type', 'summary')  # summary, explain, keywords, questions

    # Check text length
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 2000)
    if len(text) > max_length:
        return jsonify({'error': f'Text too long. Max {max_length} characters'}), 400

    service = ResearchService()
    result = service.analyze(text, analysis_type)

    return jsonify(result)



@tools_bp.route('/summarize-image', methods=['POST'])
@login_required
def summarize_image():
    """Summarize image content using Gemini AI"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        image_bytes = file.read()

        gemini_service = GeminiService()
        result = gemini_service.summarize_image(image_bytes)

        if result['success']:
            return jsonify({
                'success': True,
                'summary': result['summary']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tools_bp.route('/advanced-tts', methods=['POST'])
@login_required
def advanced_text_to_speech():
    """
    Advanced Text-to-Speech with multiple voices and styles
    FIXED: normalize rate & pitch to +N% / +NHz for edge-tts
    """
    import re

    data = request.get_json() or {}

    # ---------- Validate text ----------
    if 'text' not in data:
        return jsonify({'success': False, 'error': 'No text provided'}), 400

    text = str(data.get('text', '')).strip()
    if not text:
        return jsonify({'success': False, 'error': 'Text cannot be empty'}), 400

    if len(text) > 5000:
        return jsonify({'success': False, 'error': 'Text too long (max 5000 characters)'}), 400

    # ---------- Helpers ----------
    def normalize_rate(rate):
        s = str(rate if rate is not None else "0").strip()

        # "0" / "10"  -> "+0%" / "+10%"
        if re.fullmatch(r"\d+", s):
            return f"+{s}%"

        # "0%" / "10%" -> "+0%" / "+10%"
        if re.fullmatch(r"\d+%", s):
            return f"+{s}"

        # "+10" / "-5" -> "+10%" / "-5%"
        if re.fullmatch(r"[+-]\d+", s):
            return f"{s}%"

        # "+10%" / "-5%" -> OK
        if re.fullmatch(r"[+-]\d+%", s):
            return s

        # fallback an toàn
        return "+0%"

    def normalize_pitch(pitch):
        s = str(pitch if pitch is not None else "0").strip()

        # "0" / "20" -> "+0Hz" / "+20Hz"
        if re.fullmatch(r"\d+", s):
            return f"+{s}Hz"

        # "0Hz" / "20Hz" -> "+0Hz" / "+20Hz"
        if re.fullmatch(r"\d+Hz", s):
            return f"+{s}"

        # "+20" / "-10" -> "+20Hz" / "-10Hz"
        if re.fullmatch(r"[+-]\d+", s):
            return f"{s}Hz"

        # "+20Hz" / "-10Hz" -> OK
        if re.fullmatch(r"[+-]\d+Hz", s):
            return s

        return "+0Hz"

    # ---------- Normalize params ----------
    rate = normalize_rate(data.get('rate'))
    pitch = normalize_pitch(data.get('pitch'))

    target_lang = data.get('target_lang', 'vi')
    voice_gender = data.get('voice_gender', 'female')
    voice_index = int(data.get('voice_index', 0))
    style = data.get('style', 'general')

    # ---------- Run service ----------
    try:
        service = AdvancedTTSService()
        result = service.text_to_speech(
            text=text,
            target_lang=target_lang,
            voice_gender=voice_gender,
            voice_index=voice_index,
            rate=rate,
            pitch=pitch,
            style=style
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@tools_bp.route('/tts/voices', methods=['GET'])
@login_required
def get_voices():
    """Get available TTS voices"""
    language = request.args.get('language', None)
    voices = AdvancedTTSService.get_available_voices(language)
    styles = AdvancedTTSService.get_available_styles()

    return jsonify({
        'success': True,
        'voices': voices,
        'styles': styles
    })


