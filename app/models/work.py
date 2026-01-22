from datetime import datetime
from app import db


class Work(db.Model):
    """Phiên làm việc (workspace)"""
    __tablename__ = 'works'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False, default='Untitled Work')
    description = db.Column(db.Text, nullable=True)
    
    ocr_result_id = db.Column(db.Integer, db.ForeignKey('ocr_results.id'), nullable=True, index=True)
    
    is_archived = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relationships
    text_blocks = db.relationship('TextBlock', backref='work', lazy='dynamic', cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='work', lazy='dynamic')

    def to_dict(self, include_blocks=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'ocr_result_id': self.ocr_result_id,
            'is_archived': self.is_archived,
            'block_count': self.text_blocks.filter_by(is_deleted=False).count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_blocks:
            data['text_blocks'] = [
                block.to_dict() 
                for block in self.text_blocks.filter_by(is_deleted=False).order_by(TextBlock.position).all()
            ]
        return data


class TextBlock(db.Model):
    """Khối văn bản trong work"""
    __tablename__ = 'text_blocks'

    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=False, index=True)
    
    source_type = db.Column(
        db.Enum('ocr', 'manual', 'translate', 'tts', 'research', 'edit'),
        default='ocr',
        index=True
    )
    
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    extra_data = db.Column(db.JSON, nullable=True)  # Lưu thông tin bổ sung
    
    position = db.Column(db.Integer, default=0, index=True)
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tts_audios = db.relationship('TTSAudio', backref='text_block', lazy='dynamic')
    translations = db.relationship('Translation', backref='text_block', lazy='dynamic')
    chat_messages = db.relationship('ChatMessage', backref='text_block', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'work_id': self.work_id,
            'source_type': self.source_type,
            'title': self.title,
            'content': self.content,
            'extra_data': self.extra_data,
            'position': self.position,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def soft_delete(self):
        """Soft delete block"""
        self.is_deleted = True
