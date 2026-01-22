from datetime import datetime
from app import db


class OCRResult(db.Model):
    """Kết quả OCR từ ảnh"""
    __tablename__ = 'ocr_results'

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # OCR Engine info
    engine = db.Column(db.String(30), default='easyocr')
    language = db.Column(db.String(20), default='vi,en')
    
    # Text outputs
    raw_text = db.Column(db.Text, nullable=True)
    processed_text = db.Column(db.Text, nullable=True)
    corrected_text = db.Column(db.Text, nullable=True)
    
    # Metadata
    confidence_avg = db.Column(db.Numeric(5, 4), nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    word_count = db.Column(db.Integer, nullable=True)
    
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed'), default='pending', index=True)
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    segments = db.relationship('OCRSegment', backref='ocr_result', lazy='dynamic', cascade='all, delete-orphan')
    works = db.relationship('Work', backref='ocr_result', lazy='dynamic')
    chat_messages = db.relationship('ChatMessage', backref='ocr_result', lazy='dynamic')

    def to_dict(self, include_segments=False):
        data = {
            'id': self.id,
            'image_id': self.image_id,
            'user_id': self.user_id,
            'engine': self.engine,
            'language': self.language,
            'raw_text': self.raw_text,
            'processed_text': self.processed_text,
            'corrected_text': self.corrected_text,
            'confidence_avg': float(self.confidence_avg) if self.confidence_avg else None,
            'processing_time_ms': self.processing_time_ms,
            'word_count': self.word_count,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_segments:
            data['segments'] = [seg.to_dict() for seg in self.segments.order_by(OCRSegment.position).all()]
        return data


class OCRSegment(db.Model):
    """Chi tiết từng segment OCR với bounding box"""
    __tablename__ = 'ocr_segments'

    id = db.Column(db.Integer, primary_key=True)
    ocr_result_id = db.Column(db.Integer, db.ForeignKey('ocr_results.id'), nullable=False, index=True)
    
    text = db.Column(db.String(1000), nullable=False)
    confidence = db.Column(db.Numeric(5, 4), nullable=False)
    
    # Bounding box
    bbox_x1 = db.Column(db.Integer, nullable=True)
    bbox_y1 = db.Column(db.Integer, nullable=True)
    bbox_x2 = db.Column(db.Integer, nullable=True)
    bbox_y2 = db.Column(db.Integer, nullable=True)
    
    position = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ocr_result_id': self.ocr_result_id,
            'text': self.text,
            'confidence': float(self.confidence),
            'bbox': {
                'x1': self.bbox_x1,
                'y1': self.bbox_y1,
                'x2': self.bbox_x2,
                'y2': self.bbox_y2
            } if self.bbox_x1 is not None else None,
            'position': self.position,
            'created_at': self.created_at.isoformat()
        }
