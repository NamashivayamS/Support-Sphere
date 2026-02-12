from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Project, ChatMessage
from datetime import datetime

customer_bp = Blueprint('customer', __name__)

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

@customer_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        complexity = request.form.get('complexity')
        deadline_str = request.form.get('deadline')
        budget_range = request.form.get('budget_range', '').strip()
        nda_required = request.form.get('nda_required') == 'on'
        
        # Validation
        if not title or not description or not complexity or not deadline_str:
            flash('Please fill in all required fields.', 'danger')
            return render_template('project/create_project.html')
        
        if len(title) < 5:
            flash('Project title must be at least 5 characters long.', 'danger')
            return render_template('project/create_project.html')
        
        if len(description) < 20:
            flash('Project description must be at least 20 characters long.', 'danger')
            return render_template('project/create_project.html')
        
        # Parse deadline
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            
            # Check if deadline is in the future
            if deadline.date() < datetime.utcnow().date():
                flash('Deadline must be in the future.', 'danger')
                return render_template('project/create_project.html')
                
        except ValueError:
            flash('Invalid deadline format.', 'danger')
            return render_template('project/create_project.html')
        
        try:
            # Create project
            project = Project(
                title=title,
                description=description,
                complexity=complexity,
                deadline=deadline,
                budget_range=budget_range if budget_range else None,
                nda_required=nda_required,
                customer_id=current_user.id,
                status='Pending',
                progress=0
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash(f'Project "{title}" created successfully! Our team will review it shortly.', 'success')
            return redirect(url_for('customer.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your project. Please try again.', 'danger')
            print(f"Project creation error: {str(e)}")
            return render_template('project/create_project.html')
    
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