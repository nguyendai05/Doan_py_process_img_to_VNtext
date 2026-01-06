from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import ChatSession, ChatMessage

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/sessions', methods=['GET'])
@login_required
def get_sessions():
    """Lấy danh sách phiên chat của user"""
    sessions = ChatSession.query.filter_by(user_id=current_user.id, is_archived=False)\
        .order_by(ChatSession.updated_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions])


@chat_bp.route('/sessions', methods=['POST'])
@login_required
def create_session():
    """Tạo phiên chat mới"""
    data = request.get_json() or {}
    title = data.get('title', 'Cuộc trò chuyện mới')
    
    session = ChatSession(user_id=current_user.id, title=title)
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201


@chat_bp.route('/sessions/<int:session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """Lấy chi tiết phiên chat với tất cả tin nhắn"""
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'Không tìm thấy phiên chat'}), 404
    return jsonify(session.to_dict(include_messages=True))


@chat_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@login_required
def update_session(session_id):
    """Cập nhật tiêu đề phiên chat"""
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'Không tìm thấy phiên chat'}), 404
    
    data = request.get_json() or {}
    if 'title' in data:
        session.title = data['title']
    
    db.session.commit()
    return jsonify(session.to_dict())


@chat_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Xóa phiên chat"""
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'Không tìm thấy phiên chat'}), 404
    
    db.session.delete(session)
    db.session.commit()
    return jsonify({'message': 'Đã xóa phiên chat'})


@chat_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@login_required
def get_messages(session_id):
    """Lấy tin nhắn của phiên chat"""
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'Không tìm thấy phiên chat'}), 404
    
    messages = session.messages.order_by(ChatMessage.created_at).all()
    return jsonify([m.to_dict() for m in messages])


@chat_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@login_required
def add_message(session_id):
    """Thêm tin nhắn vào phiên chat"""
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({'error': 'Không tìm thấy phiên chat'}), 404
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Thiếu nội dung tin nhắn'}), 400
    
    message = ChatMessage(
        session_id=session_id,
        role=data.get('role', 'user'),
        content=data['content'],
        message_type=data.get('message_type', 'text'),
        metadata=data.get('metadata')
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify(message.to_dict()), 201


@chat_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """Xóa tin nhắn"""
    message = ChatMessage.query.join(ChatSession).filter(
        ChatMessage.id == message_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not message:
        return jsonify({'error': 'Không tìm thấy tin nhắn'}), 404
    
    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Đã xóa tin nhắn'})
