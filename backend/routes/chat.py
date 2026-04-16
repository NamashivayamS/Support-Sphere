from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import ChatMessage, Project, TeamMember

chat_bp = Blueprint('chat', __name__)
# ... rest of your chat code

@chat_bp.route('/project/<int:project_id>')
@login_required
def project_chat(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Verify access
    if not can_access_project(project):
        flash('You do not have access to this project chat', 'danger')
        return redirect(url_for('home'))
    
    messages = ChatMessage.query.filter_by(project_id=project_id)\
                               .order_by(ChatMessage.timestamp).all()
    
    return render_template('communication/project_chat.html',
                          project=project,
                          messages=messages)

@chat_bp.route('/project/<int:project_id>/send', methods=['POST'])
@login_required
def send_message(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Verify access
    if not can_access_project(project):
        return jsonify({'error': 'Unauthorized'}), 403
    
    message_text = request.form.get('message')
    
    if message_text:
        message = ChatMessage(
            message=message_text,
            project_id=project_id,
            sender_id=current_user.id
        )
        db.session.add(message)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': {
                    'id': message.id,
                    'text': message.message,
                    'sender': current_user.name,
                    'role': current_user.role,
                    'timestamp': message.timestamp.strftime('%H:%M %p'),
                    'avatar': f'https://ui-avatars.com/api/?name={current_user.name}&background={get_role_color(current_user.role)}&color=fff'
                }
            })
    
    return redirect(url_for('chat.project_chat', project_id=project_id))

@chat_bp.route('/project/<int:project_id>/messages')
@login_required
def get_messages(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Verify access
    if not can_access_project(project):
        return jsonify({'error': 'Unauthorized'}), 403
    
    since = request.args.get('since', type=int, default=0)
    
    query = ChatMessage.query.filter_by(project_id=project_id)
    
    if since > 0:
        query = query.filter(ChatMessage.id > since)
    
    messages = query.order_by(ChatMessage.timestamp).all()
    
    return jsonify({
        'messages': [{
            'id': m.id,
            'text': m.message,
            'sender': m.sender_name,
            'role': m.sender_role,
            'timestamp': m.timestamp.strftime('%H:%M %p'),
            'avatar': f'https://ui-avatars.com/api/?name={m.sender_name}&background={get_role_color(m.sender_role)}&color=fff'
        } for m in messages]
    })

def can_access_project(project):
    """Check if current user has access to project"""
    if current_user.role == 'manager':
        return True
    elif current_user.role == 'customer':
        return project.customer_id == current_user.id
    elif current_user.role == 'team_member':
        from app import TeamMember
        return TeamMember.query.filter_by(
            project_id=project.id,
            user_id=current_user.id
        ).first() is not None
    return False

def get_role_color(role):
    """Get avatar color based on role"""
    colors = {
        'manager': '198754',
        'team_member': '6c757d',
        'customer': '0d6efd'
    }
    return colors.get(role, '6c757d')