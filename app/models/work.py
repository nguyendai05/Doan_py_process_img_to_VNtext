from datetime import datetime
from app import db


class Work(db.Model):
    __tablename__ = 'works'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, default='Untitled Work')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    text_blocks = db.relationship('TextBlock', backref='work', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_blocks=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'block_count': self.text_blocks.count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_blocks:
            data['text_blocks'] = [block.to_dict() for block in self.text_blocks.all()]
        return data
