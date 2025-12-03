from datetime import datetime
from app import db


class TextBlock(db.Model):
    __tablename__ = 'text_blocks'

    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey('works.id'), nullable=False, index=True)
    source_type = db.Column(db.String(50), nullable=False, default='ocr')  # ocr, translate, tts_note, research
    title = db.Column(db.String(255), default='')
    content = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, default=0)  # For ordering blocks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'work_id': self.work_id,
            'source_type': self.source_type,
            'title': self.title,
            'content': self.content,
            'position': self.position,
            'created_at': self.created_at.isoformat()
        }
