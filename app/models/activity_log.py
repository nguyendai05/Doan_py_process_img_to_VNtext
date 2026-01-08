from datetime import datetime
from app import db


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    action = db.Column(db.String(50), nullable=False, index=True)  # login, logout, ocr, tts, translate, etc.
    entity_type = db.Column(db.String(50), nullable=True)  # image, work, ocr_result, etc.
    entity_id = db.Column(db.Integer, nullable=True)
    
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 support
    user_agent = db.Column(db.String(500), nullable=True)
    
    extra_data = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
