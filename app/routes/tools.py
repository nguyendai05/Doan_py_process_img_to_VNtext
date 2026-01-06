from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.tts_service import TTSService
from app.services.translate_service import TranslateService
from app.services.research_service import ResearchService

tools_bp = Blueprint('tools', __name__)


@tools_bp.route('/tts', methods=['POST'])
@login_required
def text_to_speech():
    """Convert text to speech with caching support"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided',
            'error_code': 'EMPTY_TEXT'
        }), 400

    text = data['text']
    language = data.get('language', 'vi')

    # Validate empty or whitespace-only text
    if not text or not text.strip():
        return jsonify({
            'success': False,
            'error': 'Text is empty or contains only whitespace',
            'error_code': 'EMPTY_TEXT'
        }), 400

    # Check text length
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 2000)
    if len(text) > max_length:
        return jsonify({
            'success': False,
            'error': f'Text too long. Max {max_length} characters',
            'error_code': 'TEXT_TOO_LONG'
        }), 400

    # Validate language
    if language not in TTSService.SUPPORTED_LANGUAGES:
        return jsonify({
            'success': False,
            'error': f'Unsupported language: {language}',
            'error_code': 'UNSUPPORTED_LANGUAGE'
        }), 400

    try:
        result = TTSService.text_to_speech_with_cache(text, language, current_user.id)
        return jsonify({
            'success': True,
            'audio_url': result['audio_url'],
            'from_cache': result['from_cache'],
            'duration_ms': result.get('duration_ms')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': 'GENERATION_FAILED'
        }), 500


@tools_bp.route('/tts/languages', methods=['GET'])
def get_tts_languages():
    """Get supported TTS languages"""
    return jsonify({
        'languages': TTSService.get_supported_languages()
    })


@tools_bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """Translate text with caching support"""
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided',
            'error_code': 'EMPTY_TEXT'
        }), 400

    text = data['text']
    dest_lang = data.get('dest_lang', 'en')
    src_lang = data.get('src_lang', 'auto')

    # Validate empty or whitespace-only text
    if not text or not text.strip():
        return jsonify({
            'success': False,
            'error': 'Text is empty or contains only whitespace',
            'error_code': 'EMPTY_TEXT'
        }), 400

    # Check text length
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 2000)
    if len(text) > max_length:
        return jsonify({
            'success': False,
            'error': f'Text too long. Max {max_length} characters',
            'error_code': 'TEXT_TOO_LONG'
        }), 400

    # Validate same source and destination language (only when source is not 'auto')
    if src_lang != 'auto' and src_lang == dest_lang:
        return jsonify({
            'success': False,
            'error': 'Source and destination languages cannot be the same',
            'error_code': 'SAME_LANGUAGE'
        }), 400

    try:
        service = TranslateService()
        result = service.translate_with_cache(text, dest_lang, src_lang, current_user.id)

        if result['success']:
            return jsonify({
                'success': True,
                'translated_text': result['translated_text'],
                'source_lang': result['source_lang'],
                'dest_lang': result['dest_lang'],
                'from_cache': result['from_cache']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Translation failed'),
                'error_code': 'TRANSLATION_FAILED'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': 'TRANSLATION_FAILED'
        }), 500


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
