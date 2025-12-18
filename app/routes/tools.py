from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from app.services.tts_service import TTSService
from app.services.translate_service import TranslateService
from app.services.research_service import ResearchService

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
