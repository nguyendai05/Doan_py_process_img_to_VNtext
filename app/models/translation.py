from datetime import datetime
from app import db
import hashlib


class Translation(db.Model):
    """Bản dịch (có cache)"""
    __tablename__ = 'translations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    source_text = db.Column(db.Text, nullable=False)
    source_text_hash = db.Column(db.String(64), nullable=False, index=True)
    source_lang = db.Column(db.String(10), nullable=False, index=True)
    
    translated_text = db.Column(db.Text, nullable=False)
    dest_lang = db.Column(db.String(10), nullable=False, index=True)
    
    engine = db.Column(db.String(30), default='google')
    
    text_block_id = db.Column(db.Integer, db.ForeignKey('text_blocks.id'), nullable=True, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint for caching
    __table_args__ = (
        db.UniqueConstraint('source_text_hash', 'source_lang', 'dest_lang', name='idx_cache'),
    )

    @staticmethod
    def generate_hash(text):
        """Generate SHA256 hash for text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @classmethod
    def find_cached(cls, text, source_lang, dest_lang):
        """Find cached translation"""
        text_hash = cls.generate_hash(text)
        return cls.query.filter_by(
            source_text_hash=text_hash,
            source_lang=source_lang,
            dest_lang=dest_lang
        ).first()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source_text': self.source_text,
            'source_lang': self.source_lang,
            'translated_text': self.translated_text,
            'dest_lang': self.dest_lang,
            'engine': self.engine,
            'text_block_id': self.text_block_id,
            'created_at': self.created_at.isoformat()
        }
