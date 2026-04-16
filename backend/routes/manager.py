from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db, mail
from models import User, Project, Task, TeamMember
from utils.email_service import send_task_assignment_email, send_project_status_change_email
from datetime import datetime

manager_bp = Blueprint('manager', __name__)

@manager_bp.before_request
@login_required
def require_manager():
    if current_user.role != 'manager':
        flash('Access denied. Manager privileges required.', 'danger')
        return redirect(url_for('home'))

@manager_bp.route('/dashboard')
def dashboard():
    # Get all projects
    projects = Project.query.order_by(Project.created_at.desc()).all()
    
    # Get team members
    team_members = User.query.filter_by(role='team_member', is_active=True).all()
    
    # Get customers for project creation form
    customers = User.query.filter_by(role='customer', is_active=True).all()
    
    # Statistics
    total_projects = len(projects)
    in_progress = len([p for p in projects if p.status == 'In Progress'])
    completed = len([p for p in projects if p.status == 'Completed'])
    pending = len([p for p in projects if p.status == 'Pending'])
    
    stats = {
        'total_projects': total_projects,
        'in_progress': in_progress,
        'completed': completed,
        'pending': pending,
        'team_count': len(team_members)
    }
    
    return render_template('dashboard/manager_dashboard.html',
                          projects=projects,
                          team_members=team_members,
                          customers=customers,
                          stats=stats)

@manager_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    team_members = User.query.filter_by(role='team_member', is_active=True).all()
    return render_template('project/project_detail.html',
                          project=project,
                          team_members=team_members)

@manager_bp.route('/project/create', methods=['POST'])
def create_project():
    title = request.form.get('title')
    description = request.form.get('description')
    complexity = request.form.get('complexity')
    deadline_str = request.form.get('deadline')
    customer_id = request.form.get('customer_id')
    
    # Validate inputs
    if not all([title, description, complexity, deadline_str, customer_id]):
        flash('All fields are required', 'danger')
        return redirect(url_for('customer.new_project'))
    
    # Parse deadline
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    except:
        flash('Invalid deadline format', 'danger')
        return redirect(url_for('customer.new_project'))
    
    # Create project
    project = Project(
        title=title,
        description=description,
        complexity=complexity,
        deadline=deadline,
        customer_id=customer_id,
        manager_id=current_user.id,
        status='Pending'
    )
    
    db.session.add(project)
    db.session.commit()
    
    flash('Project created successfully!', 'success')
    return redirect(url_for('manager.dashboard'))

@manager_bp.route('/project/<int:project_id>/assign-team', methods=['POST'])
def assign_team(project_id):
    project = Project.query.get_or_404(project_id)
    member_ids = request.form.getlist('team_members')
    
    # Clear existing assignments
    TeamMember.query.filter_by(project_id=project_id).delete()
    
    # Add new assignments
    for member_id in member_ids:
        team_member = TeamMember(
            project_id=project_id,
            user_id=member_id,
            role='Developer'  # Default role
        )
        db.session.add(team_member)
    
    # Update project status
    if project.status == 'Pending':
        project.status = 'In Progress'
    
    db.session.commit()
    
    flash('Team assigned successfully!', 'success')
    return redirect(url_for('manager.project_detail', project_id=project_id))

@manager_bp.route('/task/create', methods=['POST'])
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')
    role = request.form.get('role')
    priority = request.form.get('priority')
    deadline_str = request.form.get('deadline')
    project_id = request.form.get('project_id')
    assignee_id = request.form.get('assignee_id')
    
    if not all([title, role, deadline_str, project_id]):
        flash('Required fields missing', 'danger')
        return redirect(request.referrer)
    
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    except:
        flash('Invalid deadline format', 'danger')
        return redirect(request.referrer)
    
    task = Task(
        title=title,
        description=description,
        role=role,
        priority=priority,
        deadline=deadline,
        project_id=project_id,
        assignee_id=assignee_id if assignee_id else None,
        created_by_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    # Send email notification if task is assigned
    if assignee_id:
        assignee = User.query.get(assignee_id)
        if assignee and assignee.notification_settings:
            if assignee.notification_settings.should_send_email('task_assigned'):
                try:
                    send_task_assignment_email(mail, current_app._get_current_object(), task, assignee)
                except Exception as e:
                    print(f"Error sending email notification: {str(e)}")
    
    flash('Task created successfully!', 'success')
    return redirect(url_for('manager.project_detail', project_id=project_id))

@manager_bp.route('/task/<int:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    assignee_id = request.form.get('assignee_id')
    
    old_assignee_id = task.assignee_id
    task.assignee_id = assignee_id
    task.status = 'In Progress'
    
    db.session.commit()
    
    # Send email notification to new assignee
    if assignee_id and assignee_id != old_assignee_id:
        assignee = User.query.get(assignee_id)
        if assignee and assignee.notification_settings:
            if assignee.notification_settings.should_send_email('task_assigned'):
                try:
                    send_task_assignment_email(mail, current_app._get_current_object(), task, assignee)
                except Exception as e:
                    print(f"Error sending email notification: {str(e)}")
    
    flash('Task assigned successfully!', 'success')
    return redirect(request.referrer)

@manager_bp.route('/project/<int:project_id>/update-status', methods=['POST'])
def update_project_status(project_id):
    project = Project.query.get_or_404(project_id)
    old_status = project.status
    new_status = request.form.get('status')
    
    project.status = new_status
    
    if new_status == 'Completed':
        project.completed_at = datetime.utcnow()
        project.progress = 100
    
    db.session.commit()
    
    # Send email notifications to all project stakeholders
    if old_status != new_status:
        recipients = []
        
        # Add customer
        if project.customer:
            recipients.append(project.customer)
        
        # Add manager
        if project.manager and project.manager.id != current_user.id:
            recipients.append(project.manager)
        
        # Add team members
        for team_member in project.team_members:
            if team_member.member:
                recipients.append(team_member.member)
        
        # Filter recipients who want email notifications
        email_recipients = [
            r for r in recipients 
            if r.notification_settings and r.notification_settings.should_send_email('project_status_change')
        ]
        
        if email_recipients:
            try:
                send_project_status_change_email(
                    mail, 
                    current_app._get_current_object(), 
                    project, 
                    email_recipients, 
                    old_status, 
                    new_status
                )
            except Exception as e:
                print(f"Error sending email notifications: {str(e)}")
    
    flash(f'Project status updated to {new_status}', 'success')
    return redirect(request.referrer)

@manager_bp.route('/team-members')
def team_members():
    members = User.query.filter_by(role='team_member').all()
    return render_template('team/team_members.html', members=members)

@manager_bp.route('/reports')
def reports():
    # Project analytics
    projects = Project.query.all()
    
    # Calculate metrics
    total_projects = len(projects)
    completed_projects = len([p for p in projects if p.status == 'Completed'])
    active_projects = len([p for p in projects if p.status == 'In Progress'])
    
    completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
    
    # Tasks by status
    all_tasks = Task.query.all()
    tasks_by_status = {
        'pending': len([t for t in all_tasks if t.status == 'Pending']),
        'in_progress': len([t for t in all_tasks if t.status == 'In Progress']),
        'completed': len([t for t in all_tasks if t.status == 'Completed']),
        'blocked': len([t for t in all_tasks if t.status == 'Blocked'])
    }
    
    return render_template('reports/project_reports.html',
                          total_projects=total_projects,
                          completed_projects=completed_projects,
                          active_projects=active_projects,
                          completion_rate=round(completion_rate, 1),
                          tasks_by_status=tasks_by_status)