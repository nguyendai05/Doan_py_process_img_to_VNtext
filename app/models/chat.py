from datetime import datetime
from app import db


class ChatSession(db.Model):
    """Phiên chat"""
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), default='Cuộc trò chuyện mới')
    work_id = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=True, index=True)
    
    is_archived = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_messages=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'work_id': self.work_id,
            'is_archived': self.is_archived,
            'message_count': self.messages.filter_by(is_deleted=False).count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_messages:
            data['messages'] = [
                msg.to_dict() 
                for msg in self.messages.filter_by(is_deleted=False).order_by(ChatMessage.created_at).all()
            ]
        return data


class ChatMessage(db.Model):
    """Tin nhắn trong chat"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False, index=True)
    
    role = db.Column(db.Enum('user', 'assistant', 'system'), nullable=False, default='user', index=True)
    content = db.Column(db.Text, nullable=False)
    
    message_type = db.Column(
        db.Enum('text', 'ocr_result', 'translation', 'tts', 'research', 'error'),
        default='text',
        index=True
    )
    
    extra_data = db.Column(db.JSON, nullable=True)  # audio_url, source_lang, dest_lang, etc.
    
    # Links to related entities
    ocr_result_id = db.Column(db.Integer, db.ForeignKey('ocr_results.id'), nullable=True)
    text_block_id = db.Column(db.Integer, db.ForeignKey('text_blocks.id'), nullable=True)
    
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'message_type': self.message_type,
            'extra_data': self.extra_data,
            'ocr_result_id': self.ocr_result_id,
            'text_block_id': self.text_block_id,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat()
        }

    def soft_delete(self):
        """Soft delete message"""
        self.is_deleted = True
