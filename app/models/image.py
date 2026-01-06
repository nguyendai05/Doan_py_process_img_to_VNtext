from datetime import datetime
from app import db


class Image(db.Model):
    """Lưu trữ ảnh upload"""
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # bytes
    mime_type = db.Column(db.String(50), nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(50), default='upload')  # upload, url, camera
    checksum = db.Column(db.String(64), nullable=True, index=True)  # SHA256
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    ocr_results = db.relationship('OCRResult', backref='image', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'source': self.source,
            'checksum': self.checksum,
            'created_at': self.created_at.isoformat()
        }
