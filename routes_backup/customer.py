from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Project, ChatMessage
from datetime import datetime

customer_bp = Blueprint('customer', __name__)
# ... rest of your customer code

@customer_bp.before_request
@login_required
def require_customer():
    if current_user.role != 'customer':
        flash('Access denied. Customer privileges required.', 'danger')
        return redirect(url_for('home'))

@customer_bp.route('/dashboard')
def dashboard():
    # Get customer's projects
    projects = Project.query.filter_by(customer_id=current_user.id)\
                           .order_by(Project.created_at.desc()).all()
    
    return render_template('dashboard/customer_dashboard.html', projects=projects)

@customer_bp.route('/projects/new')
def new_project():
    return render_template('project/create_project.html')

@customer_bp.route('/projects/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Verify access
    if project.customer_id != current_user.id:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('customer.dashboard'))
    
    return render_template('project/customer_project_detail.html', project=project)

@customer_bp.route('/projects/<int:project_id>/chat')
def project_chat(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Verify access
    if project.customer_id != current_user.id:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('customer.dashboard'))
    
    messages = ChatMessage.query.filter_by(project_id=project_id)\
                               .order_by(ChatMessage.timestamp).all()
    
    return render_template('communication/project_chat.html',
                          project=project,
                          messages=messages)