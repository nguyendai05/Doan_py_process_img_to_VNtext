import os
import hashlib
import time
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Image, OCRResult, OCRSegment, Work, TextBlock
from app.services.ocr_service import OCRService
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
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png'}), 400

    try:
        start_time = time.time()

        # Read image bytes
        image_bytes = file.read()

        # Check file size
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
        if len(image_bytes) > max_size:
            return jsonify({'error': f'File too large. Max size: {max_size // (1024*1024)}MB'}), 400

        # Calculate checksum
        checksum = hashlib.sha256(image_bytes).hexdigest()

        # Save image file
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Generate unique filename
        unique_filename = f"{current_user.id}_{int(time.time())}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        # Save Image record to database
        image = Image(
            user_id=current_user.id,
            file_name=filename,
            file_path=file_path,
            file_size=len(image_bytes),
            mime_type=file.content_type,
            source='upload',
            checksum=checksum
        )
        db.session.add(image)
        db.session.flush()  # Get image.id

        # Run OCR
        segments = OCRService.extract_text(image_bytes)
        raw_text = OCRService.segments_to_text(segments)

        # Process text
        # processor = raw_text
        processed_text = raw_text

        # bart_output = run_bart_model(processed_text)

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        # Calculate average confidence
        confidence_avg = None
        if segments:
            confidences = [seg.get('confidence', 0) for seg in segments if 'confidence' in seg]
            if confidences:
                confidence_avg = sum(confidences) / len(confidences)

        # Save OCR Result
        ocr_result = OCRResult(
            image_id=image.id,
            user_id=current_user.id,
            engine='easyocr',
            language='vi,en',
            raw_text=raw_text,
            processed_text=processed_text,
            corrected_text=raw_text,
            confidence_avg=confidence_avg,
            processing_time_ms=processing_time_ms,
            word_count=len(processed_text.split()) if processed_text else 0,
            status='completed'
        )
        db.session.add(ocr_result)
        db.session.flush()  # Get ocr_result.id

        # Save OCR Segments
        for idx, seg in enumerate(segments):
            bbox = seg.get('bbox', [])
            ocr_segment = OCRSegment(
                ocr_result_id=ocr_result.id,
                text=seg.get('text', ''),
                confidence=seg.get('confidence', 0),
                bbox_x1=int(bbox[0][0]) if len(bbox) > 0 else None,
                bbox_y1=int(bbox[0][1]) if len(bbox) > 0 else None,
                bbox_x2=int(bbox[2][0]) if len(bbox) > 2 else None,
                bbox_y2=int(bbox[2][1]) if len(bbox) > 2 else None,
                position=idx
            )
            db.session.add(ocr_segment)

        # Create Work with text block
        work = Work(
            user_id=current_user.id,
            title=filename,
            ocr_result_id=ocr_result.id
        )
        db.session.add(work)
        db.session.flush()  # Get work.id

        # Create initial text block with OCR result
        text_block = TextBlock(
            work_id=work.id,
            source_type='ocr',
            title='OCR Result',
            content=processed_text or raw_text,
            position=0
        )
        db.session.add(text_block)

        db.session.commit()

        return jsonify({
            'success': True,
            'raw_text': raw_text,
            'processed_text': processed_text,
            'bart_output': raw_text,
            'segments': segments,
            'image_id': image.id,
            'ocr_result_id': ocr_result.id,
            'work_id': work.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



