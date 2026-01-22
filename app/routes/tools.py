from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.services.translation_model_service import TranslationModelService
from app.services.tts_service import TTSService
from app.services.translate_service import TranslateService
from app.services.research_service import ResearchService

from app.services.summarize_service import SummarizeService
from app.services.model_inference import run_bart_model, model as bart_model

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

@tools_bp.route('/translate-model-all', methods=['POST'])
@login_required
def translate_all_by_model():
    """
    Dịch bằng MODEL (Vi -> En) cho text dài (chunking bên service xử lý).
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'No text provided', 'error_code': 'EMPTY_TEXT'}), 400

    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'Text is empty', 'error_code': 'EMPTY_TEXT'}), 400

    # Cho phép dài hơn translate cũ (vì model có chunking)
    max_len = current_app.config.get('MAX_MODEL_TEXT_LENGTH', 20000)
    if len(text) > max_len:
        return jsonify({
            'success': False,
            'error': f'Text too long. Max {max_len} characters',
            'error_code': 'TEXT_TOO_LONG'
        }), 400

    try:
        service = TranslationModelService(model_dir=r"D:\video\opus-vi-en-100k-final-20260122T171003Z-3-001\opus-vi-en-100k-final")
        result = service.translate(text)

        if result.get('success'):
            return jsonify({
                'success': True,
                'translated_text': result['translated_text'],
                'device': result.get('device', 'cpu'),
                'chunks_count': result.get('chunks_count', 1)
            })

        return jsonify({'success': False, 'error': 'Translation failed', 'error_code': 'TRANSLATION_FAILED'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'error_code': 'TRANSLATION_FAILED'}), 500

# tom tắt
@tools_bp.route('/summarize', methods=['POST'])
@login_required
def summarize_text():
    """
    NEW endpoint: /api/tools/summarize
    """
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'No text provided', 'error_code': 'EMPTY_TEXT'}), 400

    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'Text is empty', 'error_code': 'EMPTY_TEXT'}), 400

    # dùng cùng MAX_TEXT_LENGTH hiện có (đang 2000) :contentReference[oaicite:3]{index=3}
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 2000)
    if len(text) > max_length:
        return jsonify({
            'success': False,
            'error': f'Text too long. Max {max_length} characters',
            'error_code': 'TEXT_TOO_LONG'
        }), 400

    algo = data.get('algo', 'heuristic7')
    debug = bool(data.get('debug', False))

    service = SummarizeService()
    result = service.summarize(text, algo=algo, debug=debug)
    return jsonify(result)


# ==================== BART CORRECTION ====================
@tools_bp.route('/bart-correction', methods=['POST'])
@login_required
def bart_correction():
    """
    Sửa lỗi chính tả bằng BARTpho model.
    Request: { "text": "..." }
    Response: original_text, corrected_text, evaluation stats
    """
    # Check if BART model is loaded
    if bart_model is None:
        return jsonify({
            'success': False,
            'error': 'BART model chưa được load. Vui lòng kiểm tra folder models/bartpho_correction_model/',
            'error_code': 'MODEL_NOT_LOADED'
        }), 503

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'No text provided',
            'error_code': 'EMPTY_TEXT'
        }), 400

    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({
            'success': False,
            'error': 'Text is empty',
            'error_code': 'EMPTY_TEXT'
        }), 400

    # Check text length
    max_length = current_app.config.get('MAX_TEXT_LENGTH', 5000)
    if len(text) > max_length:
        return jsonify({
            'success': False,
            'error': f'Text too long. Max {max_length} characters',
            'error_code': 'TEXT_TOO_LONG'
        }), 400

    try:
        # Run BART correction
        corrected_text = run_bart_model(text)

        # Calculate evaluation metrics
        original_words = text.split()
        corrected_words = corrected_text.split()

        # Count differences (simple word-level diff)
        changes_count = 0
        max_len = max(len(original_words), len(corrected_words))
        for i in range(max_len):
            orig = original_words[i] if i < len(original_words) else ''
            corr = corrected_words[i] if i < len(corrected_words) else ''
            if orig != corr:
                changes_count += 1
        
        # Count sentences (simple split by . ! ?)
        import re
        original_sentences = len(re.split(r'[.!?]+', text.strip()))
        corrected_sentences = len(re.split(r'[.!?]+', corrected_text.strip()))
        
        # Calculate change rate
        change_rate = round((changes_count / max(len(original_words), 1)) * 100, 1)
        
        # Calculate character change
        char_diff = len(corrected_text) - len(text)
        char_change_percent = round((abs(char_diff) / max(len(text), 1)) * 100, 1)
        
        # Calculate similarity score (simple Jaccard-like)
        orig_set = set(original_words)
        corr_set = set(corrected_words)
        intersection = len(orig_set & corr_set)
        union = len(orig_set | corr_set)
        similarity_score = round((intersection / max(union, 1)) * 100, 1)

        return jsonify({
            'success': True,
            'original_text': text,
            'corrected_text': corrected_text,
            'evaluation': {
                'original_char_count': len(text),
                'corrected_char_count': len(corrected_text),
                'char_diff': char_diff,
                'char_change_percent': char_change_percent,
                'original_word_count': len(original_words),
                'corrected_word_count': len(corrected_words),
                'original_sentence_count': original_sentences,
                'corrected_sentence_count': corrected_sentences,
                'changes_count': changes_count,
                'change_rate': change_rate,
                'similarity_score': similarity_score
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': 'CORRECTION_FAILED'
        }), 500
