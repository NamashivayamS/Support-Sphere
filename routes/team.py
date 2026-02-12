from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Task, TaskNote, Project, TeamMember
from datetime import datetime

team_bp = Blueprint('team', __name__)

@team_bp.before_request
@login_required
def require_team_member():
    if current_user.role != 'team_member':
        flash('Access denied. Team member privileges required.', 'danger')
        return redirect(url_for('home'))

@team_bp.route('/dashboard')
def dashboard():
    # Get assigned tasks
    assigned_tasks = Task.query.filter_by(assignee_id=current_user.id)\
                               .order_by(Task.deadline).all()
    
    # Statistics
    total_tasks = len(assigned_tasks)
    completed = len([t for t in assigned_tasks if t.status == 'Completed'])
    in_progress = len([t for t in assigned_tasks if t.status == 'In Progress'])
    pending = len([t for t in assigned_tasks if t.status == 'Pending'])
    
    # Get projects user is assigned to
    team_assignments = TeamMember.query.filter_by(user_id=current_user.id).all()
    project_ids = [ta.project_id for ta in team_assignments]
    projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []
    
    stats = {
        'total_tasks': total_tasks,
        'completed': completed,
        'in_progress': in_progress,
        'pending': pending,
        'overdue': len([t for t in assigned_tasks if t.is_overdue])
    }
    
    return render_template('dashboard/team_dashboard.html',
                          tasks=assigned_tasks,
                          projects=projects,
                          stats=stats)


@team_bp.route('/projects')
def projects():
    # Get projects user is assigned to
    team_assignments = TeamMember.query.filter_by(user_id=current_user.id).all()
    project_ids = [ta.project_id for ta in team_assignments]
    projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []
    
    return render_template('team/team_projects.html', projects=projects)

@team_bp.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Verify access
    if task.assignee_id != current_user.id:
        flash('You do not have access to this task', 'danger')
        return redirect(url_for('team.dashboard'))
    
    return render_template('tasks/task_detail.html', task=task)

@team_bp.route('/task/<int:task_id>/update-progress', methods=['POST'])
def update_progress(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Verify access
    if task.assignee_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    progress = request.form.get('progress', type=int)
    status = request.form.get('status')
    note = request.form.get('note')
    
    # Update task
    if progress is not None:
        task.progress = progress
    
    if status:
        task.status = status
        if status == 'Completed':
            task.completed_at = datetime.utcnow()
            task.progress = 100
    
    # Add note if provided
    if note:
        task_note = TaskNote(
            content=note,
            task_id=task.id,
            author_id=current_user.id
        )
        db.session.add(task_note)
    
    db.session.commit()
    
    # Update project progress
    update_project_progress(task.project_id)
    
    flash('Task progress updated successfully!', 'success')
    return redirect(request.referrer or url_for('team.dashboard'))

@team_bp.route('/task/<int:task_id>/add-note', methods=['POST'])
def add_note(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Verify access
    if task.assignee_id != current_user.id:
        flash('You do not have access to this task', 'danger')
        return redirect(url_for('team.dashboard'))
    
    content = request.form.get('content')
    
    if content:
        note = TaskNote(
            content=content,
            task_id=task.id,
            author_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
    
    return redirect(request.referrer)

def update_project_progress(project_id):
    """Calculate and update project progress based on tasks"""
    project = Project.query.get(project_id)
    
    if project and project.tasks:
        total_progress = sum(task.progress for task in project.tasks)
        project.progress = total_progress // len(project.tasks)
        db.session.commit()
