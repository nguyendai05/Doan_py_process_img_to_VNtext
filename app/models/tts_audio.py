from datetime import datetime
from app import db
import hashlib


class TTSAudio(db.Model):
    """File audio TTS (có cache theo text hash)"""
    __tablename__ = 'tts_audio'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    text_content = db.Column(db.Text, nullable=False)
    text_hash = db.Column(db.String(64), nullable=False, index=True)
    
    language = db.Column(db.String(10), nullable=False, default='vi', index=True)
    
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)
    
    text_block_id = db.Column(db.Integer, db.ForeignKey('text_blocks.id'), nullable=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_hash(text):
        """Generate SHA256 hash for text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @classmethod
    def find_cached(cls, text, language):
        """Find cached audio by text hash and language"""
        text_hash = cls.generate_hash(text)
        return cls.query.filter_by(text_hash=text_hash, language=language).first()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'text_content': self.text_content,
            'text_hash': self.text_hash,
            'language': self.language,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration_ms': self.duration_ms,
            'text_block_id': self.text_block_id,
            'created_at': self.created_at.isoformat()
        }
