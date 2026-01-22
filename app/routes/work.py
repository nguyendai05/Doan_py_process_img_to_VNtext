from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Work, TextBlock

work_bp = Blueprint('work', __name__)


@work_bp.route('', methods=['GET'])
@login_required
def list_works():
    """List all works for current user"""
    works = Work.query.filter_by(user_id=current_user.id, is_archived=False)\
        .order_by(Work.updated_at.desc()).all()
    return jsonify({
        'works': [w.to_dict() for w in works]
    })


@work_bp.route('', methods=['POST'])
@login_required
def create_work():
    """Create new work"""
    data = request.get_json() or {}

    title = data.get('title', 'Untitled Work')
    content = data.get('content', '')
    source_type = data.get('source_type', 'ocr')

    # Create work
    work = Work(user_id=current_user.id, title=title)
    db.session.add(work)
    db.session.flush()  # Get work.id

    # Create initial text block if content provided
    if content:
        block = TextBlock(
            work_id=work.id,
            content=content,
            source_type=source_type,
            position=0
        )
        db.session.add(block)

    db.session.commit()

    return jsonify({
        'message': 'Work created',
        'work': work.to_dict(include_blocks=True)
    }), 201


@work_bp.route('/<int:work_id>', methods=['GET'])
@login_required
def get_work(work_id):
    """Get work details with all text blocks"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'error': 'Work not found'}), 404

    return jsonify({'work': work.to_dict(include_blocks=True)})


@work_bp.route('/<int:work_id>', methods=['PUT'])
@login_required
def update_work(work_id):
    """Update work title"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'error': 'Work not found'}), 404

    data = request.get_json() or {}
    if 'title' in data:
        work.title = data['title']

    db.session.commit()

    return jsonify({
        'message': 'Work updated',
        'work': work.to_dict()
    })


@work_bp.route('/<int:work_id>/rename', methods=['POST'])
@login_required
def rename_work(work_id):
    """Rename work title"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'success': False, 'error': 'Work not found'}), 404

    data = request.get_json() or {}
    new_title = data.get('title', '').strip()
    
    if not new_title:
        return jsonify({'success': False, 'error': 'Title cannot be empty'}), 400
    
    work.title = new_title
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Work renamed',
        'work': work.to_dict()
    })


@work_bp.route('/<int:work_id>', methods=['DELETE'])
@login_required
def delete_work(work_id):
    """Delete work and all its text blocks"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'error': 'Work not found'}), 404

    db.session.delete(work)
    db.session.commit()

    return jsonify({'message': 'Work deleted'})


@work_bp.route('/<int:work_id>/blocks', methods=['POST'])
@login_required
def add_text_block(work_id):
    """Add text block to work"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'error': 'Work not found'}), 404

    data = request.get_json() or {}
    content = data.get('content', '')
    source_type = data.get('source_type', 'ocr')
    title = data.get('title', '')

    # Get next position
    max_pos = db.session.query(db.func.max(TextBlock.position))\
        .filter_by(work_id=work_id).scalar() or 0

    block = TextBlock(
        work_id=work_id,
        content=content,
        source_type=source_type,
        title=title,
        position=max_pos + 1
    )
    db.session.add(block)
    db.session.commit()

    return jsonify({
        'message': 'Block added',
        'block': block.to_dict()
    }), 201


@work_bp.route('/<int:work_id>/blocks/<int:block_id>', methods=['DELETE'])
@login_required
def delete_text_block(work_id, block_id):
    """Delete text block from work"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'error': 'Work not found'}), 404

    block = TextBlock.query.filter_by(id=block_id, work_id=work_id).first()

    if not block:
        return jsonify({'error': 'Block not found'}), 404

    db.session.delete(block)
    db.session.commit()

    return jsonify({'message': 'Block deleted'})


@work_bp.route('/<int:work_id>/merge', methods=['POST'])
@login_required
def merge_blocks(work_id):
    """Merge multiple text blocks into one"""
    work = Work.query.filter_by(id=work_id, user_id=current_user.id).first()

    if not work:
        return jsonify({'error': 'Work not found'}), 404

    data = request.get_json() or {}
    block_ids = data.get('block_ids', [])

    if len(block_ids) < 2:
        return jsonify({'error': 'Need at least 2 blocks to merge'}), 400

    # Get blocks in order
    blocks = TextBlock.query.filter(
        TextBlock.id.in_(block_ids),
        TextBlock.work_id == work_id
    ).order_by(TextBlock.position).all()

    if len(blocks) != len(block_ids):
        return jsonify({'error': 'Some blocks not found'}), 404

    # Merge content
    merged_content = '\n\n'.join([b.content for b in blocks])

    # Create new merged block
    max_pos = db.session.query(db.func.max(TextBlock.position))\
        .filter_by(work_id=work_id).scalar() or 0

    new_block = TextBlock(
        work_id=work_id,
        content=merged_content,
        source_type='ocr',
        title='Merged Block',
        position=max_pos + 1
    )
    db.session.add(new_block)

    # Delete original blocks
    for block in blocks:
        db.session.delete(block)

    db.session.commit()

    return jsonify({
        'message': 'Blocks merged',
        'block': new_block.to_dict()
    })
