from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import extensions and models
from extensions import db, login_manager, mail
from models import User, NotificationSettings, Project, Task, TeamMember, ChatMessage, TaskNote, Milestone, TaskDependency

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supportsphere-project-key-v2')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'SupportSphere <noreply@supportsphere.com>')

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
login_manager.login_view = 'auth.login'

# Register blueprints
from routes.auth import auth_bp
from routes.manager import manager_bp
from routes.team import team_bp
from routes.customer import customer_bp
from routes.notifications import notifications_bp
from routes.chat import chat_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(manager_bp, url_prefix='/manager')
app.register_blueprint(team_bp, url_prefix='/team')
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(notifications_bp, url_prefix='/notifications')
app.register_blueprint(chat_bp, url_prefix='/chat')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== TEMPLATE FILTERS ====================

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if not value:
        return ''
    if isinstance(value, str):
        return value
    return value.strftime(format)

@app.template_filter('dateformat')
def dateformat(value):
    return datetimeformat(value, '%Y-%m-%d')

@app.template_filter('timeuntil')
def timeuntil(value):
    if not value:
        return ''
    delta = value - datetime.utcnow()
    days = delta.days
    hours = delta.seconds // 3600
    
    if days > 0:
        return f'{days} days'
    elif hours > 0:
        return f'{hours} hours'
    else:
        return 'Today'

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}


# ==================== ROOT ROUTE ====================

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'manager':
            return redirect(url_for('manager.dashboard'))
        elif current_user.role == 'team_member':
            return redirect(url_for('team.dashboard'))
        elif current_user.role == 'customer':
            return redirect(url_for('customer.dashboard'))
    return render_template('pages/index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """General dashboard route that redirects based on user role"""
    if current_user.role == 'manager':
        return redirect(url_for('manager.dashboard'))
    elif current_user.role == 'team_member':
        return redirect(url_for('team.dashboard'))
    elif current_user.role == 'customer':
        return redirect(url_for('customer.dashboard'))
    else:
        flash('Invalid user role', 'danger')
        return redirect(url_for('home'))


@app.route('/help')
def help():
    return render_template('pages/help.html')


# ==================== PROFILE ROUTE ====================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from flask import request, flash
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Update profile information
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            avatar = request.form.get('avatar', '').strip()  # Placeholder for avatar upload
            
            # Validation
            if not name or not email:
                flash('Name and email are required.', 'danger')
                return render_template('pages/profile.html')
            
            if len(name) < 2:
                flash('Name must be at least 2 characters long.', 'danger')
                return render_template('pages/profile.html')
            
            # Email validation
            if '@' not in email or '.' not in email:
                flash('Please provide a valid email address.', 'danger')
                return render_template('pages/profile.html')
            
            # Check if email is already taken by another user
            if email != current_user.email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash('This email is already in use by another account.', 'danger')
                    return render_template('pages/profile.html')
            
            try:
                # Update user information
                current_user.name = name
                current_user.email = email
                if avatar:
                    current_user.avatar = avatar
                
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while updating your profile.', 'danger')
                print(f"Profile update error: {str(e)}")
        
        # Change password
        elif action == 'change_password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not current_password or not new_password or not confirm_password:
                flash('All password fields are required.', 'danger')
                return render_template('pages/profile.html')
            
            # Verify current password
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('pages/profile.html')
            
            # Check password length
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('pages/profile.html')
            
            # Check password confirmation
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('pages/profile.html')
            
            # Check if new password is different from current
            if current_user.check_password(new_password):
                flash('New password must be different from current password.', 'danger')
                return render_template('pages/profile.html')
            
            try:
                # Update password
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully!', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while changing your password.', 'danger')
                print(f"Password change error: {str(e)}")
    
    return render_template('pages/profile.html')


# ==================== SETTINGS ROUTE ====================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    from flask import request, flash
    
    if request.method == 'POST':
        theme = request.form.get('theme', 'light')
        
        # Validate theme value
        if theme not in ['light', 'dark']:
            flash('Invalid theme selection.', 'danger')
            return render_template('pages/settings.html')
        
        try:
            # Update theme preference
            current_user.theme = theme
            db.session.commit()
            flash(f'Theme changed to {theme} mode successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating settings.', 'danger')
            print(f"Settings update error: {str(e)}")
    
    return render_template('pages/settings.html')


# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database with sample data"""
    from datetime import timedelta
    
    with app.app_context():
        db.create_all()
        
        # Check if users exist
        if User.query.count() == 0:
            print("Creating sample data...")
            
            # Create manager
            manager = User(
                name='Sarah Chen',
                email='manager@supportsphere.com',
                role='manager'
            )
            manager.set_password('manager123')
            
            # Create team members
            team1 = User(
                name='Mike Wong',
                email='mike@supportsphere.com',
                role='team_member'
            )
            team1.set_password('team123')
            
            team2 = User(
                name='Lisa Patel',
                email='lisa@supportsphere.com',
                role='team_member'
            )
            team2.set_password('team123')
            
            team3 = User(
                name='James Wilson',
                email='james@supportsphere.com',
                role='team_member'
            )
            team3.set_password('team123')
            
            # Create customers
            customer1 = User(
                name='John Smith',
                email='john@example.com',
                role='customer'
            )
            customer1.set_password('customer123')
            
            customer2 = User(
                name='Emily Davis',
                email='emily@example.com',
                role='customer'
            )
            customer2.set_password('customer123')
            
            db.session.add_all([manager, team1, team2, team3, customer1, customer2])
            db.session.commit()
            
            # Create notification settings
            for user in [manager, team1, team2, team3, customer1, customer2]:
                settings = NotificationSettings(user_id=user.id)
                db.session.add(settings)
            db.session.commit()
            
            # Create project
            project = Project(
                title='E-commerce Website Development',
                description='Build a modern e-commerce platform with React, Node.js, and PostgreSQL',
                complexity='High',
                status='In Progress',
                progress=35,
                deadline=datetime.utcnow() + timedelta(days=45),
                customer_id=customer1.id,
                manager_id=manager.id
            )
            db.session.add(project)
            db.session.commit()
            
            # Assign team members
            team_members = [
                TeamMember(project_id=project.id, user_id=team1.id, role='Lead Developer'),
                TeamMember(project_id=project.id, user_id=team2.id, role='Frontend Developer'),
                TeamMember(project_id=project.id, user_id=team3.id, role='Backend Developer')
            ]
            db.session.add_all(team_members)
            
            # Create tasks
            tasks = [
                Task(
                    title='Setup project repository',
                    description='Initialize Git repo, setup project structure, install dependencies',
                    role='Backend',
                    priority='High',
                    deadline=datetime.utcnow() + timedelta(days=3),
                    project_id=project.id,
                    assignee_id=team1.id,
                    created_by_id=manager.id,
                    progress=100,
                    status='Completed',
                    completed_at=datetime.utcnow() - timedelta(days=1)
                ),
                Task(
                    title='Design database schema',
                    description='Create ERD, define tables, relationships, and indexes',
                    role='DB',
                    priority='High',
                    deadline=datetime.utcnow() + timedelta(days=5),
                    project_id=project.id,
                    assignee_id=team3.id,
                    created_by_id=manager.id,
                    progress=80,
                    status='In Progress'
                ),
                Task(
                    title='Create homepage UI',
                    description='Responsive homepage with product grid, search bar, categories',
                    role='Frontend',
                    priority='Medium',
                    deadline=datetime.utcnow() + timedelta(days=10),
                    project_id=project.id,
                    assignee_id=team2.id,
                    created_by_id=manager.id,
                    progress=30,
                    status='In Progress'
                )
            ]
            db.session.add_all(tasks)
            db.session.commit()
            
            # Add chat messages
            messages = [
                ChatMessage(
                    message='Hi team, I\'ve reviewed the requirements. Let\'s start with the database design first.',
                    project_id=project.id,
                    sender_id=manager.id
                ),
                ChatMessage(
                    message='Database schema is ready for review.',
                    project_id=project.id,
                    sender_id=team3.id
                ),
                ChatMessage(
                    message='Looking forward to seeing the progress!',
                    project_id=project.id,
                    sender_id=customer1.id
                )
            ]
            db.session.add_all(messages)
            db.session.commit()
            
            print("=" * 60)
            print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
            print("=" * 60)
            print("\n🔐 TEST CREDENTIALS:")
            print("   Manager: manager@supportsphere.com / manager123")
            print("   Team: mike@supportsphere.com / team123")
            print("   Customer: john@example.com / customer123")
            print("=" * 60)


# ==================== RUN APP ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)