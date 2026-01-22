import os
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.ocr_service import OCRService
from app.services.text_processing import TextProcessor
from app.services.model_inference import run_bart_model

ocr_bp = Blueprint('ocr', __name__)

"""
Check if file extension is allowed
right split token to check extension
"""
def allowed_file(filename):
    allowed_extension = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension


@ocr_bp.route('/single', methods=['POST'])
@login_required
def single_image_ocr():
    """Process single image OCR"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png'}), 400

    try:
        # Read image bytes
        image_bytes = file.read()

        # Check file size
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
        if len(image_bytes) > max_size:
            return jsonify({'error': f'File too large. Max size: {max_size // (1024*1024)}MB'}), 400

        # Run OCR
        segments = OCRService.extract_text(image_bytes)
        raw_text = OCRService.segments_to_text(segments)

        # Process text
        processor = TextProcessor(language='vi')
        processed_text = processor.process(raw_text)

        bart_output = run_bart_model(processed_text)

        return jsonify({
            'success': True,
            'raw_text': raw_text,
            'processed_text': processed_text,
            'bart_output': bart_output,
            'segments': segments
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500



